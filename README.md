<!-- markdownlint-disable MD033 -->

<!-- markdownlint-disable MD041 -->

<p align="center">
    <h1 align="center">
        <img src="https://github.com/YiVal/YiVal/assets/1544154/b0c681e7-7474-4b87-9c69-fde6e0e47401"
         alt="YiVal Logo" width="100"
        height="100" style="vertical-align: middle;">
        YiVal
    </h1>
     <p align="center">⚡ Auto Prompting ⚡</p>
</p>

<!-- markdownlint-disable-next-line MD013 -->

👉 Follow
us: [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/YiValai.svg?style=social&label=Follow%20%40YiVal)](https://twitter.com/yivalloveaigc) |
[![Discord](https://dcbadge.vercel.app/api/server/HnUWVW4kth?compact=true&style=flat)](https://discord.gg/HnUWVW4kth)

👉 Sponsored by Discord AIGC community:
[![Discord](https://dcbadge.vercel.app/api/server/aigc?compact=true&style=flat)](https://discord.gg/aigc)

[![License: MIT](https://img.shields.io/badge/License-Apache2.0-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub star chart](https://img.shields.io/github/stars/YiVal/YiVal?style=social)](https://star-history.com/#YiVal/YiVal)
[![Open Issues](https://img.shields.io/github/issues-raw/YiVal/YiVal)](https://github.com/YiVal/YiVal/issues)

## What is YiVal?

**YiVal: Your Automatic Prompt Engineering Assistant for GenAI Applications**
YiVal is a state-of-the-art tool designed to streamline the tuning process for
your GenAI app prompts and **ANY** configs in the loop. With YiVal, manual adjustments
are a thing of the past. This **data-driven and evaluation-centric** approach ensures
optimal prompts, precise RAG configurations, and fine-tuned model parameters.
Empower your applications to achieve
**enhanced results, reduce latency, and minimize inference costs**
effortlessly with YiVal!

**Problems YiVal trying to tackle:**

1. Prompt Development Challenge: "I can't create a better prompt. A score of 60
   for my current prompt isn't helpful at all🤔."
2. Fine-tuning Difficulty: "I don't know how to fine-tune; the terminology and
   numerous fine-tune algorithms are overwhelming😵."
3. Confidence and Scalability: "I learned tutorials to build agents from Langchain
   and LlamaIndex, but am I doing it right? Will the bot burn through my money
   when I launch? Will users like my GenAI app🤯?"
4. Models and Data Drift: "Models and data keep changing; I worry a well-performing
   GenAI app now may fail later😰."
5. Relevant Metrics and Evaluators: "Which metrics and evaluators should I focus
   on for my use case📊?"

[Check out our quickstart guide!][1]

[1]: https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/tutorial.md
<img src="https://github.com/YiVal/YiVal/assets/1544154/dba5acd9-995c-45fd-9d08-c7cf198a77ad">

### Link to demo

**[Tiktok title autotune](http://ec2-35-85-28-134.us-west-2.compute.amazonaws.com:8074/enhancer-experiment-results)**

## Installation

### Docker Runtime

Install Docker and pull ourimage on DockerHub:

```bash
docker pull yival/release:latest
```

Run our image:

```bash
docker run --it yival/release:latest
```

VSCode with Docker extension is recommended for running and developments. If you are developer using GPU with Pytorch, or need jupyter lab for data science:

```bash
docker pull yival/release:cu12_torch_jupyter
docker run --gpus all --it -p 8888:8888 yival/release:cu12_torch_jupyter
```

### Prerequisites

- **Python Version**: Ensure you have `Python 3.10` or later installed.
- **OpenAI API Key**: Obtain an API key from OpenAI. Once you have the key, set
  it as an environment variable named `OPENAI_API_KEY`.

### Installation Methods

#### Using pip (Recommended for Users)

Install the `yival` package directly using pip:

```bash
pip install yival
```

#### Development Setup Using Poetry

If you're looking to contribute or set up a development environment:

1. **Install Poetry**: If you haven't already, [install Poetry](https://python-poetry.org/docs/#installation).
2. **Clone the Repository, or use CodeSpace**:

   2.1 **Use CodeSpace**
   The easiest way to get YiVal enviornment. Click below to use the GitHub Codespace, then go to the next step.

   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/YiVal/YiVal?quickstart=1)

   2.2 **Clone the Repository**

   ```bash
   git clone https://github.com/YiVal/YiVal.git
   cd YiVal
   ```

3. **Setup with Poetry**: Initialize the Python virtual environment and install
   dependencies using Poetry. Make sure to run the below cmd in `/YiVal` directory:

   ```bash
   poetry install --sync
   ```

## Trying Out YiVal

After setting up, you can quickly get started with YiVal by generating datasets
of random tech startup business names.

### Steps to Run Your First YiVal Program

1. **Navigate to the yival Directory**:

   ```bash
   cd /YiVal/src/yival
   ```

2. **Set OpenAI API Key**: Replace `$YOUR_OPENAI_API_KEY` with your
   actual OpenAI API key.

   On macOS or Linux systems,

   ```bash
   export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
   ```

   On Windows systems,

   ```powershell
   setx OPENAI_API_KEY $YOUR_OPENAI_API_KEY
   ```

3. **Define YiVal Configuration**:
   Create a configuration file named `config_data_generation.yml` for automated
   test dataset generation with the following content:

   ```yaml
   description: Generate test data
   dataset:
     data_generators:
       openai_prompt_data_generator:
         chunk_size: 100000
         diversify: true
         model_name: gpt-4
         input_function:
           description: # Description of the function
             Given a tech startup business, generate a corresponding landing
             page headline
           name: headline_generation_for_business
           parameters:
             tech_startup_business: str # Parameter name and type
         number_of_examples: 3
         output_csv_path: generated_examples.csv
     source_type: machine_generated
   ```

4. **Execute YiVal**:
   Run the following command from within the `/YiVal/src/yival` directory:

   ```bash
   yival run config_data_generation.yml
   ```

5. **Check the Generated Dataset**:
   The generated test dataset will be stored in `generated_examples.csv`.

Please refer to [YiVal Docs Page](https://yival.github.io/YiValApi/) for more details about YiVal!

## Demo

[Demo Video](https://github.com/YiVal/YiVal/assets/80620352/f2438449-2c13-45d1-a660-a783c5ae4eb6)

[Demo Video](https://github.com/YiVal/YiVal/assets/80620352/1a2916c1-de6a-452a-88e0-fb4461e7c04b)

| Use Case Demo                                                                                               | Supported Features                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Github Link                                                                                                                                                               | Video Demo Link                                                                                                                                         |
| ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🐯 Craft your AI story with ChatGPT and MidJourney                                                          | **Multi-modal** support: Design an AI-powered narrative using YiVal's multi-modal support of simultaneous text and images. It supports native and seamless [Reinforcement Learning from Human Feedback](https://en.wikipedia.org/wiki/Reinforcement_learning_from_human_feedback)(RLHF) and [Reinforcement Learning from AI Feedback](https://arxiv.org/abs/2309.00267)(RLAIF). Please watch the video above for this use case.                                                          | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/yival_midjourney_animal_story.ipynb)           |    [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://www.youtube.com/)                                                                                                                                                     |
| 🌟 Evaluate performance of multiple LLMs with your own Q&A test dataset                                     | Conveniently**evaluate and compare** performance of your model of choice against 100+ models, thanks to [LiteLLM](https://github.com/BerriAI/litellm). Analyze model performance benchmarks tailored to your **customized test data** or use case.                                                                                                                                                                                                                              | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/model_compare.ipynb)           | [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://www.youtube.com/)                                                                                                                                                        |
| 🔥 Startup Company Headline Generation Bot                                                                  | Streamline generation of headlines for your startup with automated test data**creation**, prompt **crafting**, results **evaluation**, and performance **enhancement** via GPT-4.                                                                                                                                                                                                                                                                                | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/headline_generation.ipynb)           | [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://github.com/YiVal/YiVal/assets/80620352/1a2916c1-de6a-452a-88e0-fb4461e7c04b) |
| 🧳 Build a Customized Travel Guide Bot                                                                      | Leverage**automated prompts** inspired by the travel **community's** most popular suggestions, such as those from [awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts).                                                                                                                                                                                                                                                                                      | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/yival_prompt_retrieval.ipynb)           | [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://www.youtube.com/watch?v=rIggQqW4iAM)    |
| 📖 Build a Cheaper Translator: Use GPT-3.5 to teach Llama2 to create a translator with lower inference cost | Using[Replicate](https://replicate.com/docs/guides/fine-tune-a-language-model) and GPT-3.5's test data, you can **fine-tune** Llama2's translation bot. Benefit from 18x savings while experiencing only a 6% performance decrease.                                                                                                                                                                                                                                                   | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/yival_translator_demo.ipynb)           | [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://github.com/YiVal/YiVal/assets/80620352/f2438449-2c13-45d1-a660-a783c5ae4eb6) |
| 🤖️ Chat with Your Favorite Characters - Dantan Ji from Till the End of the Moon                           | Bring your favorite characters to life through automated prompt creation and**character script retrieval**.                                                                                                                                                                                                                                                                                                                                                                        | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/yival_auto_reply.ipynb)           | [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://www.youtube.com/watch?v=xD1G2Sl9UeU)                                         |
| 🔍Evaluate guardrails's performance in generating Python(.py) outputs                                       | [Guardrails](https://github.com/ShreyaR/guardrails): where are my guardrails? 😭 `<br>`Yival: I am here. ⭐️`<br><br>`The **integrated evaluation** [experiment](https://github.com/ShreyaR/guardrails/issues/345) is carried out with 80 LeetCode problems in csv, using guardrail and using only GPT-4. The accuracy drops from 0.625 to 0.55 with guardrail, latency increases by 44%, and cost increases by 140%. Guardrail still has a long way to go from demo to production. | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/Guardrails_run_leetcode.ipynb) | [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://www.youtube.com/watch?v=UMPxORBBTFI)                                        |
| 🍨Visualize different foods around the world!🍱                                                             | Just give the place where the food belongs and the best season to taste it, and you can get a video of the season-specific food!🤩                                                                                                                                                                                                                                                                                                                                                       | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/place_food_demo.ipynb)           | [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://www.youtube.com/watch?v=qJj7zSXQbTI)                                        |
| 🎈News article summary with CoD                                                                             | By integrating the[&#34;Chain of Density&#34;](https://huggingface.co/papers/2309.04269) method, **evaluate the enhancer's ability** in text summarization.🎆 Using **3** articles points generated by GPT-4 for evaluation, the coherent score increased by **20.03%**, the attributive score increased by **25.18%!**, the average token usage from **2054.6 -> 1473.4(-28.3%)** 🚀.                                                                        | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/news_summary_with_CoD.ipynb)           | [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://www.youtube.com/watch?v=W86Bct9k7fI)                                        |
| 🥐 Automated TikTok Title Generation Bot                                                                    | With only two input lines, you can easily create**concise and polished** TikTok video titles based on your desired target audience and video content summaries. This is presented by our **auto-prompt feature**: the process is automated, so you can input your requirements and enjoy the results hassle-free!                                                                                                                                                            | [![Open In GitHub](https://img.shields.io/badge/Github-@YiVal-CAC6FC)](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/Auto_TikTok_Title_Generation_Bots_Demo.ipynb)           |  [![Open In Youtube](https://img.shields.io/badge/_-Open%20in%20Youtube-red?logo=youtube&logoColor=red&labelColor=white)](https://www.youtube.com/)                                                                                                                                                       |

## Contribution Guidelines

If you want to contribute to YiVal, be sure to review
the [contribution guidelines](https://yival.github.io/YiVal/contributing/).
We use [GitHub issues](https://github.com/YiVal/YiVal/issues) for tracking
requests and bugs.
Please join [YiVal&#39;s discord channel](https://discord.gg/HnUWVW4kth) for
general questions and discussion.
Join our collaborative community where your unique expertise as researchers and
software engineers is highly valued! Contribute to our project and be a part of
an innovative space where every line of code and research insight actively
fuels advancements in technology, fostering a future that is intelligently
connected and universally accessible.

## Contributors

<a href="https://github.com/YiVal/YiVal/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=YiVal/YiVal" />
</a>  
<p align="center">
<br>
🌟 YiVal welcomes your contributions! 🌟<p align="center">
🥳 Thanks so much to all of our amazing contributors 🥳</p>

## Paper / Algorithm Implementation

| **Paper**                                                                         | **Author**                                                                                                                                                                                                                                   | **Topics**                  | **YiVal Contributor**             | **Data Generator**                                                                                                       | **Variation Generator**                                                                                                                       | **Evaluator**                                                                                                                                                                                                                | **Selector**                                                                                 | **Enhancer**                                                                                                                              | **Config**                                                                                            |
| --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| [Large Language Models Are Human-Level Prompt Engineers](https://arxiv.org/abs/2211.01910) | [Yongchao Zhou](https://arxiv.org/search/cs?searchtype=author&query=Zhou,+Y), [Andrei Ioan Muresanu](https://arxiv.org/search/cs?searchtype=author&query=Muresanu,+A+I), [Ziwen Han](https://arxiv.org/search/cs?searchtype=author&query=Han,+Z)            | YiVal Evolver, Auto-Prompting     | [@Tao Feng](https://github.com/oliverfeng) | [OpenAIPromptDataGenerator](https://github.com/YiVal/YiVal/blob/master/src/yival/data_generators/openai_prompt_data_generator.py) | [OpenAIPromptVariationGenerator](https://github.com/YiVal/YiVal/blob/master/src/yival/variation_generators/openai_prompt_based_variation_generator.py) | [OpenAIPromptEvaluator](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/openai_prompt_based_evaluator.py), [OpenAIEloEvaluator](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/openai_elo_evaluator.py) | [AHPSelector](https://github.com/YiVal/YiVal/blob/master/src/yival/result_selectors/ahp_selection.py) | [OpenAIPromptBasedCombinationEnhancer](https://github.com/YiVal/YiVal/blob/master/src/yival/enhancers/openai_prompt_based_combination_enhancer.py) | [config](https://github.com/YiVal/YiVal/blob/master/demo/configs/headline_generation_enhance.yml)              |
| [BERTScore: Evaluating Text Generation with BERT](https://arxiv.org/abs/1904.09675)        | [Tianyi Zhang](https://arxiv.org/search/cs?searchtype=author&query=Zhang,+T), [Varsha Kishore](https://arxiv.org/search/cs?searchtype=author&query=Kishore,+V), [Felix Wu](https://arxiv.org/search/cs?searchtype=author&query=Wu,+F)                       | YiVal Evaluator, bertscore, rouge | [@crazycth](https://github.com/crazycth)   | -                                                                                                                              | -                                                                                                                                                   | [BertScoreEvaluator](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/bertscore_evaluator.py)                                                                                                                          | -                                                                                                  | -                                                                                                                                               | -                                                                                                           |
| [AlpacaEval](https://github.com/tatsu-lab/alpaca_eval)                                     | [Xuechen Li](https://arxiv.org/search/cs?searchtype=author&query=Xuechen%20Li), [Tianyi Zhang](https://arxiv.org/search/cs?searchtype=author&query=Tianyi%20Zhang), [Yann Dubois](https://arxiv.org/search/cs?searchtype=author&query=Yann%20Dubois) et. al | YiVal Evaluator                   | [@Tao Feng](https://github.com/oliverfeng) | -                                                                                                                              | -                                                                                                                                                   | [AlpacaEvalEvaluator](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/alpaca_eval_evaluator.py)                                                                                                                       | -                                                                                                  | -                                                                                                                                               | [config](https://github.com/YiVal/YiVal/blob/master/demo/configs/alpaca_eval.yml)                              |
| [Chain of Density](https://arxiv.org/pdf/2309.04269.pdf)                                   | [Griffin Adams](https://arxiv.org/search/?query=Griffin+Adam) [Alexander R. Fabbri](https://arxiv.org/search/?query=Alexander+R.+Fabbri) et. al                                                                                                          | Prompt Engineering                | [@Tao Feng](https://github.com/oliverfeng) | -                                                                                                                              | [ChainOfDensityGenerator](https://github.com/YiVal/YiVal/blob/master/src/yival/variation_generators/chain_of_density_prompt.py)                        | -                                                                                                                                                                                                                                  | -                                                                                                  | -                                                                                                                                               | [config](https://github.com/YiVal/YiVal/blob/master/demo/configs/summary_config.yml)                           |
| [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409)                    | [Chengrun Yang](https://arxiv.org/search/cs?searchtype=author&query=Yang,+C) [Xuezhi Wang](https://arxiv.org/search/cs?searchtype=author&query=Wang,+X) et. al                                                                                           | Prompt Engineering                | [@crazycth](https://github.com/crazycth)   | -                                                                                                                              | -                                                                                                                                                   | -                                                                                                                                                                                                                                  | -                                                                                                  | [optimize_by_prompt_enhancer](https://github.com/YiVal/YiVal/blob/opro_implement/src/yival/enhancers/optimize_by_prompt_improver.py)               | [config](https://github.com/YiVal/YiVal/blob/opro_implement/demo/configs/headline_generation_improve.yml#L174) |
| [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)     | [Edward J. Hu](https://arxiv.org/search/cs?searchtype=author&query=Hu,+E+J) [Yelong Shen](https://arxiv.org/search/cs?searchtype=author&query=Shen,+Y) et. al                                                                                            | LLM Finetune                      | [@crazycth](https://github.com/crazycth)   | -                                                                                                                              | -                                                                                                                                                   | -                                                                                                                                                                                                                                  | -                                                                                                  | [sft_trainer](https://github.com/YiVal/YiVal/blob/add_finetune_module/src/yival/finetune/sft_trainer.py#L40)                                       | [config](https://github.com/YiVal/YiVal/blob/add_finetune_module/src/yival/schemas/trainer_configs.py#L48)     |

<!--  -->
