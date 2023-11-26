"""
This module provides an implementation of Large Language models as enhancers, 
https://arxiv.org/abs/2309.08532 , which is /evo/ for short

The goal of this module is to enhance and auto-generate the prompt with the 
ability of llms.

In each iteration , we construct the new propmt by the following steps:
    1. select two prompts by a select function as parents prompts.
    2. cross over the two prompts
    3. mutate

To simplify, we follow the idea of the paper, just define two evolutionary operates: c
rossover and mutate. 

If there is a need for users to customize the behavior of the evolutionary process, 
we can modify the code, and this is a easy task.

We use "rouge" to calculate scores and if there is a need for users to customize the 
evaluator, we can modify the code, and this is a easy task.

"""

import copy
import itertools
import json
from copy import deepcopy
from typing import Dict, List, Tuple

import evaluate
import numpy as np

from ..common.model_utils import llm_completion
from ..experiment.evaluator import Evaluator
from ..experiment.lite_experiment import LiteExperimentRunner
from ..experiment.rate_limiter import RateLimiter
from ..experiment.utils import generate_experiment, get_selection_strategy
from ..logger.token_logger import TokenLogger
from ..result_selectors.selection_context import SelectionContext
from ..schemas.combination_enhancer_configs import AutomaticPromptEngConfig
from ..schemas.common_structures import InputData
from ..schemas.experiment_config import (
    EnhancerOutput,
    Experiment,
    ExperimentConfig,
    ExperimentResult,
)
from ..schemas.model_configs import Request
from .base_combination_enhancer import BaseCombinationEnhancer
from .utils import (
    construct_output_format,
    construct_template_restrict,
    format_input_from_dict,
    scratch_template_vars,
    scratch_variations_from_str,
)

rouge_score = evaluate.load("rouge")
rate_limiter = RateLimiter(60 / 60)
output_dict = {}

def find_origin_combo_key(experiment: Experiment) -> str:
    """
    Find the combo key from best_combination
    Ensure that we have selector config
    """
    if experiment.selection_output is not None:
        combo_key = experiment.selection_output.best_combination
        return combo_key
    else:
        raise ValueError("Selection output is None")

def find_combo_with_score(experiment: Experiment) -> Tuple[Dict, Dict]:
    """
    Fine the best combination and its score from experiment. If the experiment
    has selection output , use the best combination from selection output.
    Otherwise , use the first combination from the experiment.
    """
    best_combo = {}
    score = {}

    if experiment.selection_output:
        combo_string = experiment.selection_output.best_combination
        best_combo = json.loads(combo_string)  #type: ignore
        score = experiment.selection_output.selection_reason or {
        }  #type: ignore

    return best_combo, score

def construct_full_prompt(
    prompt: str, enhance_var: List[str], template_vars: List[str] | None
) -> str:
    """
    construct the new prompt in a certain format
    """
    full_prompt = prompt
    if template_vars:
        full_prompt += construct_template_restrict(template_vars)
    full_prompt += construct_output_format(enhance_var)
    return full_prompt

def fetch_next_response(prompt: str, model_name="gpt-4")-> str:
        """
        fetch response for prompt
        """
        response = llm_completion(
            Request(
                model_name=model_name,
                prompt=prompt,
                params={"temperature": 1.0}
            )
        ).output

        llm_output_str = response["choices"][0]["message"]["content"].strip(
            "'"
        ).strip('"')  #type: ignore
        # print(llm_output_str)
        return llm_output_str

def collect_all_data(experiment: Experiment) -> List[InputData]:
    datas: List[InputData] = []
    for r in experiment.combination_aggregated_metrics[0].experiment_results:
        input_data = copy.deepcopy(r.input_data)
        input_data.content.pop("raw_output", None)
        datas.append(input_data)
    return datas

class AutomaticPromptEng(BaseCombinationEnhancer):
    """
    Optimization by PROmpting enhancer to enhance and auto-generate combination.
    """

    default_config =  AutomaticPromptEngConfig(
        name = "automatic-prompt-eng",
        init = [],
        dev = [],
        enhance_var=["task"],
        model_name = "gpt-4",
        max_iterations = 3,
        population = 2,
    )

    def __init__(self, config: AutomaticPromptEngConfig):
        super().__init__(config)
        self.config: AutomaticPromptEngConfig = config

    def fetch_next_variations(self, prompt: str) -> Dict:
        """
        enhance variations according to opro
        
        make sure llm response format is valid and return new varations
        """
        response = llm_completion(
            Request(
                model_name=self.config.model_name,
                prompt=prompt,
                params={"temperature": 1.0}
            )
        ).output

        llm_output_str = response["choices"][0]["message"]["content"].strip(
            "'"
        ).strip('"')  #type: ignore

        variations = scratch_variations_from_str(
            llm_output_str, self.config.enhance_var
        )

        return variations
    
    def generateRandomPromptsLLM(self, init_prompts: List[str], enhance_vars: List[str], template_vars: List[str]):
        '''
        generate all the init set by some prompts
        '''
        prompts = deepcopy(init_prompts)
        num_generated = self.config.population
        prompts_num = len(prompts)
        prompt = prompts[0]
        
        GENERATED_PROMPT =  f"""Please read the Large Language Model prompt following the <prompt> tag and try to understand what its task is.
                 Then respond with a new, robust prompt which will generate a better response to the task. Only return that prompt. Do not include a <prompt> tag.
            <prompt>
            {prompt}
        """
        if template_vars:
            GENERATED_PROMPT += construct_template_restrict(template_vars)
        GENERATED_PROMPT += construct_output_format(enhance_vars)
        
        while prompts_num < num_generated:
            response = llm_completion(
                Request(
                    model_name= self.config.model_name,
                    prompt=GENERATED_PROMPT,
                    params={"temperature": 1.0,}
                )
            ).output
            llm_output_str = response["choices"][0]["message"]["content"].strip(
                "'"
            ).strip('"') 
            
            variations = scratch_variations_from_str(
                llm_output_str, enhance_vars
            )
            new_prompt = format_input_from_dict(variations,enhance_vars)
            print(new_prompt)
            if new_prompt != prompt:
                try:
                    prompts.append(new_prompt)
                    prompts_num += 1
                except:
                    continue
        return prompts
    
    def roulette_wheel_selection(self, dic):
        print(dic)
        score_dic = {features['score']:prompt for (prompt,features) in dic.items()}
        print(score_dic)
        scores = list(score_dic.keys())
        prompts = list(score_dic.items())
        
        if len(scores) > 2:
            
            # Min-Max normalization
            min_val = np.min(scores)
            max_val = np.max(scores)
            normalized_scores = (scores - min_val) / (max_val - min_val)
            # Make sure they sum to 1 for probabilities
            normalized_scores /= (normalized_scores.sum())
            print(normalized_scores)
            
            # Randomly select two indices based on their probabilities
            selected_scores = np.random.choice(scores, 2, replace=False, p=normalized_scores)
            prompt_1 = score_dic[selected_scores[0]]
            prompt_2 = score_dic[selected_scores[1]]
            return (prompt_1, prompt_2)
        else:
            return(prompts[0],prompts[1])
        
    def construct_cross_prompt(self, prompt1:str, prompt2:str):
        CROSSOVER_PROMPT = f"""Given the following two parent prompts which come after the <prompt> tag,
            create a new prompt by crossing over or combining portions of the parents. 
            The new prompt should convey the same idea and or accomplish the same task as the parents.
            Your new prompt should only contain single quotes and should not include the <prompt> tag.
            
            <prompt>
            Prompt 1: {prompt1}
            
            Prompt 2: {prompt2}
            """
        return  CROSSOVER_PROMPT
    
    def construct_mutate_prompt(self, prompt:str):
        MUTATE_PROMPT = f"""Please read the prompt following the <prompt> tag and rewrite it in a way that is different than the original. 
                You can add or remove portions.
                Replace words with synonyms and antonyms.
                Change the goal of the prompt.
                Only respond with a prompt. Do not include the <prompt> tag or anything before or after the prompt.
                    
                <prompt>
                {prompt}
                """
        # if template_vars:
        #     MUTATE_PROMPT += construct_template_restrict(template_vars)
        #     MUTATE_PROMPT += construct_output_format(enhance_var)
        return MUTATE_PROMPT
          
    def get_best_prompt(self, dic):
        '''
        get best prompt by score
        '''
        best_prompt = ""
        max_score = 0
        for p, v in dic.items():
            if v['score'] >= max_score:
                max_score = v['score']
                best_prompt = p
        
        return best_prompt

    def fetch_next_variations(self, prompt: str) -> Dict:
        """
        enhance variations according to 
        
        make sure llm response format is valid and return new varations
        """
        response = llm_completion(
            Request(
                model_name=self.config.model_name,
                prompt=prompt,
                params={"temperature": 1.0}
            )
        ).output

        llm_output_str = response["choices"][0]["message"]["content"].strip(
            "'"
        ).strip('"')  #type: ignore

        variations = scratch_variations_from_str(
            llm_output_str, self.config.enhance_var
        )

        return variations
    
    def cal_totalscore(self, score:dict):
        return sum(score.values())
    
    def enhance(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> EnhancerOutput:
        
        experiments: List[Experiment] = []
        results: List[ExperimentResult] = []
        original_combo_key = find_origin_combo_key(experiment)
        self.updated_config = copy.deepcopy(config)
        use_dev = False
        enhance_var = deepcopy(self.config.enhance_var)
        print("total iterations:",self.config.max_iterations)
        
        #INIT SOME GENERAL VARIABLE (REFER TO OPRO)
        group_num = len(experiment.group_experiment_results)
        results_num = len(experiment.group_experiment_results[0].experiment_results)
        
        print("GROUP NUM:", group_num)
        print("RESULTS_NUM:",results_num)
        print("###########RESULTS WE ALREADY HAVE#############")
        print("selection output:",experiment.selection_output)

        
        best_combo, score = find_combo_with_score(experiment)
        
        avg_score = self.cal_totalscore(score)
        
        print("#####################################BEST COMBO#############################################")

        print("best_combo:",best_combo)
        print("score",score)
        print("############################################################################################")

        init_prompt = format_input_from_dict(best_combo,self.config.enhance_var)
        print("#####################################INIT PROMPT#############################################")

        print("init_prompt:",init_prompt)
        print("#############################################################################################")

        
        for combo_me in experiment.combination_aggregated_metrics:
            if combo_me.combo_key == json.dumps(best_combo):
                results.extend(combo_me.experiment_results)
        
        template_vars = [
            scratch_template_vars(str_value)
            for str_value in best_combo.values()
        ]
        
        if template_vars:
            
            template_vars = list(itertools.chain(*template_vars)) 
            
        else:
            template_vars = None
        
        model_prompts = []
        
        if self.config.init == []:
            model_prompts = self.generateRandomPromptsLLM([init_prompt],enhance_var,template_vars)
        else:
            model_prompts = self.generateRandomPromptsLLM(self.config.init,enhance_var,template_vars)
        # model_prompts = [init_prompt]
        
        if self.config.dev != []:
            dev = deepcopy(self.config.dev)
            use_dev = True
        
        assert set(self.config.enhance_var).issubset(set(best_combo.keys()))
        
    
        P = {}
        
        # GENERATED THE INIT PROMPTS
        for prompt in model_prompts:
            # print(prompt)
            P[prompt] = {}
        
        #CALCULATE ROUGE SCORES FOR INIT PROMPTS
        
        lite_experiment_runner = LiteExperimentRunner(
            config=self.updated_config,
            limiter=rate_limiter,
            data=collect_all_data(experiment),
            token_logger=token_logger,
            evaluator=evaluator
        )
        
        for p in P: 
            print("p",p)
            temp_p = deepcopy(p)
            print("#####################################TEMP PROMPT#############################################")
            print(temp_p)
            print("#############################################################################################")
                       
            gen_variations = scratch_variations_from_str(temp_p, self.config.enhance_var)
            if not gen_variations:
                print(
                    f"[INFO][optimize_by_prompt_enhancer] fetch next variations error"
                )
            else:
                print(
                    f"[INFO][optimize_by_prompt_enhancer] generate new variations: {gen_variations}"
                )
                
                
            lite_experiment_runner.set_variations([{
                key: [value]
                for key, value in gen_variations.items()
            }])
            
            
            experiment = lite_experiment_runner.run_experiment(
                enable_selector=True
                
            )
            if use_dev == False:
                
                temp_combo, score = find_combo_with_score(experiment)
                avg_score = self.cal_totalscore(score)
                P[p]['score'] = avg_score
                print("temp_combo:",temp_combo)
                print("score",score)
                
            else:
                pred = []
                for r in experiment.group_experiment_results:
                    pred.append(r.experiment_results[0].raw_output.text_output)
                score = rouge_score.compute(
                    predictions= pred,
                    references = dev
                )  
                
                P[p]['score'] = round(score['rouge1'], 3)
        
        best_prompt = init_prompt
    
        # RUN EXPERIMENT (REFER TO OPRO)
        
        # OPTIMIZE BY PROMPT FOR MAX_ITERATIONS TIMES
        for i in range(self.config.max_iterations):
            
            print(
                f"[INFO][evo_prompt_enhancer] start iteration[{i+1}]"
            )
            
            # STEP1: CROSS OVER
            print("************************** STEP1 ************************(********)")
            p1,p2 = self.roulette_wheel_selection(P)
            CROSSOVER_PROMPT = self.construct_cross_prompt(p1, p2)
            i = 0
            crossover_prompts = []
            while i < self.config.population:
                print("STEP 1: i=",i)
                content = fetch_next_response(CROSSOVER_PROMPT, self.config.model_name) 
                print("content:", content)
                print()
                if content != p1 and content != p2:
                    try:
                        crossover_prompts.append((content))
                        i += 1
                    except SyntaxError:
                        continue
            
            print("################################CROSS OVER PROMPTS################################")
            print("cross_over prompts:", crossover_prompts)
            print("################################END################################")
            
            # STEP2: MUTATE
            print("************************** STEP2 ************************(********)")
            mutated_prompts = []
            for co_prompt in crossover_prompts:
                MUTATE_PROMPT = self.construct_mutate_prompt(co_prompt)
                MUTATE_PROMPT = construct_full_prompt(MUTATE_PROMPT
                                                      ,enhance_var,template_vars)
                content = fetch_next_response(MUTATE_PROMPT, self.config.model_name)
                if content != co_prompt:
                    try:
                        mutated_prompts.append(content)
                    except SyntaxError:
                        continue   
                    
            #STEP3: CALCULATE ROUGE SCORES FOR ALL PROMPTS    
            print("************************** STEP3 ************************(********)")     
            for p in mutated_prompts: 
                P[p] = {}
            
            for p in P.copy().keys():
                if not P[p]:
                    temp_p = deepcopy(p)
                    # temp_prompt = construct_full_prompt(temp_p,enhance_var,template_vars)
                    gen_variations = scratch_variations_from_str(temp_p, self.config.enhance_var)
                    lite_experiment_runner.set_variations([{
                        key: [value]
                        for key, value in gen_variations.items()
                    }])
            
                    experiment = lite_experiment_runner.run_experiment(
                        enable_selector=True
                
                    )
                    
                    if use_dev == False:
                
                        temp_combo, score = find_combo_with_score(experiment)
                        avg_score = self.cal_totalscore(score)
                        P[p]['score'] = avg_score
                        print("temp_combo:",temp_combo)
                        print("score",avg_score)
                        
                    else:
                        pred = []
                        for r in experiment.group_experiment_results:
                            pred.append(r.experiment_results[0].raw_output.text_output)
                        score = rouge_score.compute(
                            predictions= pred,
                            references = dev
                        )  
                        
                        P[p]['score'] = round(score['rouge1'], 3)
            
            #STEP4: SELECT NEXT GENERATION
            
            print("************************** STEP4 ************************(********)")
            survival_scores = {features['score']:prompt for (prompt,features) in P.items()}
            print("survival_scores:", survival_scores)
            P_temp = sorted(list(survival_scores.keys()), reverse=True)
            P_temp = P_temp[:self.config.population]
            P_reduced = [survival_scores[s] for s in P_temp]
            for p in P.copy().keys():
                if p not in P_reduced:
                    del P[p]
            
            bestofnow_prompt = self.get_best_prompt(P)
            
            if best_prompt != bestofnow_prompt:
                best_prompt = deepcopy(bestofnow_prompt)
            else:
                best_prompt += "\n"
            
            # temp_prompt = construct_full_prompt(best_prompt,enhance_var,template_vars)
            gen_variations = scratch_variations_from_str(best_prompt, self.config.enhance_var)
            
            print("gen_variation:", gen_variations)
            
            lite_experiment_runner.set_variations([{
                key: [value]
                for key, value in gen_variations.items()
            }])

            experiment = lite_experiment_runner.run_experiment(
                enable_selector=True
            )
            
            experiments.append(experiment)
           
        for exp in experiments:
            for res in exp.combination_aggregated_metrics:
                results.extend(res.experiment_results)
        
        experiment = generate_experiment(
            results, evaluator, evaluate_group=False, evaluate_all=False
        )
        
        enable_custom_func = "custom_function" in self.updated_config  #type: ignore
        
        strategy = get_selection_strategy(self.updated_config)
        
        if strategy and enable_custom_func:
            context_trade_off = SelectionContext(strategy=strategy)
            experiment.selection_output = context_trade_off.execute_selection( # type: ignore
                experiment=experiment
            )

        enhancer_output = EnhancerOutput(
            group_experiment_results=experiment.group_experiment_results,
            combination_aggregated_metrics=experiment.combination_aggregated_metrics,
            original_best_combo_key=original_combo_key,
            selection_output=experiment.selection_output
        )
        
        return enhancer_output

BaseCombinationEnhancer.register_enhancer(
     "automatic_prompt_eng", AutomaticPromptEng,
    AutomaticPromptEngConfig
)