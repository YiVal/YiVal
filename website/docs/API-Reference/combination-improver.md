---
sidebar_position: 13

---

# Combination Improver

##  `BaseCombinationImprover`
###   Introduction
  This module defines the base class for combination improvers. Combination improvers are responsible for improving the combination of experiments based on their experiment results.

###   Class Definition

####    Description

####    Attributes

###   Example 

##  `OpenAIPromptBasedCombinationImprover`

###   Introduction 

  This module provides an implementation of a combination improver using OpenAI's model to suggest improvements. It leverages the capabilities of OpenAI's language model to analyze the results of an experiment and provide suggestions on how to improve the combination of parameters. The module offers a prompt-based mechanism where the language model is prompted with structured information about the experiment and its results. The model then responds with potential improvements.

###   Class Definition 

####    Description

   The configuration object is specifically tailored for the `OpenAIPromptBasedCombinationImprover` class. It provides settings to control the iterative improvement process using OpenAI's model for suggesting combination improvements.

####    Attributes

- **`openai_model_name(str)`****:** 
  - Specifies the OpenAI model to be used. 
  - The default value is `"gpt-4"`.
- **`max_iterations(int)`****:** 
  - The maximum number of iterations for the improvement process. 
  - The default value is set to `3`.
- **`stop_conditions(Optional[Dict[str, float]])`****:**
  - Conditions to halt the iterative improvement process based on evaluator scores. 
  - The default value is `None`.
- **`average_score(Optional[float])`**
  - A threshold for the average score to stop the iterative process. 
  - The default value is `None`.
- **`selection_strategy(Optional[SelectionOutput])`**
  -  Strategy for selecting the best combination. 
  - The default value is `None`.



###   Example 

##  `OptimizeByPromptImprover`

###   Introduction 

  This module offers an implementation of Optimization by PROmpting (OPRO), a method inspired by the paper [Optimization by PROmpting](https://arxiv.org/pdf/2309.03409.pdf)). OPRO leverages the capabilities of large language models (LLMs) like GPT-4 to optimize tasks by iteratively refining prompts.



  The optimization process is driven by a structured prompt that consists of the following sections:

- HEAD_META_INSTRUCTION
- SOLUTION_SCORE_PAIRS
- OPTIMATION_TASK_FORMAT (optional)
- END_META_INSTRUCTION



  As the optimization process progresses through iterations, new evaluator scores and prompts are appended to the `SOLUTION_SCORE_PAIRS` section, enhancing the overall prompt for the next iteration.

  For practical demonstrations of this concept, refer to the file `demo/configs/headline_generation_improve.yml` and the appendix of the aforementioned paper.

###   Class Definition 

####    `OptimizeByPromptImproverConfig(BaseCombinationImproverConfig)`

#####     Description

​    The configuration object tailored for the `OptimizeByPromptImprover` class, controlling how the optimization by prompting is executed.

#####     Attributes

- **`improve_var(List[str])`**: 
  - List of variables that need improvement.
- **`head_meta_instruction(str)`**: 
  - The initial instructional part of the prompt.
- **`end_meta_instruction(str)`**: 
  - The ending part of the prompt.
- **`optimation_task_format(Optional[str])`**: 
  - An optional task format for optimization.
- **`model_name(str)`**: 
  - Specifies the LLM model to be used. 
  - The default value is `"gpt-4"`.
- **`max_iterations(int)`**: 
  - The maximum number of optimization iterations. 
  - The default value is `3`.

#####     Example

######      Use OPRO Improver to Enhace Experiment Results 

```Python
# Create an OPRO configuration
improver_config = OptimizeByPromptImproverConfig(
    improve_var=["task"],
    head_meta_instruction="Start of the prompt...",
    end_meta_instruction="End of the prompt...",
    optimation_task_format="Optional format...",
    model_name="gpt-4",
    max_iterations=5
)

# Initialize the OPRO improver with the configuration
improver = OptimizeByPromptImprover(improver_config)

# Use the improver to enhance an experiment's prompts
improved_output = improver.improve(experiment, config, evaluator, token_logger)
```

######      Using the OpenAIPromptBasedCombinationImprover in YiVal config

```YAML
improver:
  name: "optimize_by_prompt_improver"
  model_name: "gpt-4"
  max_iterations: 2
  improve_var: ["task"]
  head_meta_instruction: |
    Now you will help me generate a prompt which is used to generate a corresponding
    story according to the species of an animal which is [animal_species] and its character [animal_character]. 
    I already have some prompt and its evaluation results :
    
  end_meta_instruction: |
    Give me a new prompt that is different from all pairs above, and has a evaluation value higher than any of above.
```









##  Custom Combination Improver Guide: `improve` 

  This module defines the base class for combination improvers. Combination improvers are responsible for improving the combination of experiments based on their experiment results.

###   Introduction

  Combination improvers play a pivotal role in the experimental framework by optimizing the combination of experiments based on their outcomes. By leveraging combination improvers, experiments can be fine-tuned to achieve better results. This guide will outline the process of creating a custom combination improver.

###   Overview of Base Combination Improver

  The `BaseCombinationImprover` class provides the foundational structure for all combination improvers. It offers methods to:

- Register new combination improvers.
- Fetch registered combination improvers.
- Retrieve their default configurations.

  The main responsibility of a combination improver is to improve the setup of experiments based on their results.

###   Implementing a Custom Combination Improver

  To create a custom combination improver, one should inherit from the `BaseCombinationImprover` class and implement the `improve` abstract method:

```Python
class CustomCombinationImprover(BaseCombinationImprover):
    """
    Custom combination improver to optimize the setup of experiments.
    """

    def improve(self, experiment, config, evaluator, token_logger):
        """
        Custom logic to improve the experiment based on its results.

        Args:
            experiment (Experiment): The experiment with its results.
            config (ExperimentConfig): The original experiment configuration.
            evaluator (Evaluator): A utility class to evaluate the
            ExperimentResult.
            token_logger (TokenLogger): Logs the token usage.

        Returns:
            ImproverOutput: The result of the improvement.
        """

        # Custom logic for improvement goes here
        pass
```

###   Config

```Plaintext
custom_improvers:
    class: /path/to/custom_improver.CustomImprover
    config_cls: /path/to/custom_improver_config.CustomImproverConfig
```

  To use it

```YAML
improver:
  name: custom_improver
```

###   Conclusion

  By following this guide, you have successfully created and registered a custom combination improver named `CustomCombinationImprover` within the experimental framework. This custom improver will allow you to optimize experiment combinations based on specific logic and criteria you define. As experiments evolve and grow in complexity, custom combination improvers like the one you've developed will become instrumental in achieving more refined and better results.

