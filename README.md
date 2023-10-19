<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD041 -->

<p align="center">
    <h1 align="center">
        <img src="https://github.com/YiVal/YiVal/assets/1544154/b0c681e7-7474-4b87-9c69-fde6e0e47401"
         alt="YiVal Logo" width="100"
        height="100" style="vertical-align: middle;">
        YiVal
    </h1>
     <p align="center">⚡ Build any Generative AI application with evaluation
    and enhancement ⚡</p>
</p>

<!-- markdownlint-disable-next-line MD013 -->
👉 Follow
us: [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/YiValai.svg?style=social&label=Follow%20%40YiVal)](https://twitter.com/yivalloveaigc) |
[![Discord](https://dcbadge.vercel.app/api/server/HnUWVW4kth?compact=true&style=flat)](https://discord.gg/HnUWVW4kth)

[![Downloads](https://static.pepy.tech/badge/YiVal/month)](https://pepy.tech/project/YiVal)
[![License: MIT](https://img.shields.io/badge/License-Apache2.0-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub star chart](https://img.shields.io/github/stars/YiVal/YiVal?style=social)](https://star-history.com/#YiVal/YiVal)
[![Open Issues](https://img.shields.io/github/issues-raw/YiVal/YiVal)](https://github.com/YiVal/YiVal/issues)

## What is YiVal?

**YiVal is a versatile platform and framework that streamlines the evaluation
and enhancement of your Generative AI applications.**  
Tune your prompts like how professional machine learning engineers tune their
neural model parameters. With YiVal, you can simultaneously and seamlessly adjust
your GenAI app prompts, modify Retrieval(RAG) configurations, and fine-tune model
parameters. This data-driven approach empowers you to achieve improved results,
minimize latency,and reduce inference costs with ease!"

[Check out our quickstart guide!][1]

[1]: https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/tutorial.md

<img src="https://github.com/YiVal/YiVal/assets/1544154/dba5acd9-995c-45fd-9d08-c7cf198a77ad">

## Installation

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

2. **Clone the Repository**:

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

    ```bash
    export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
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

## Demo

[Demo Video](https://user-images.githubusercontent.com/68423614/275689372-c3d3497c-1dc4-48bd-860b-a773f11db9f7.mp4)

| Use Case Demo | Supported Features                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Colab Link |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|
| 🐯 Craft your AI story with ChatGPT and MidJourney | **Multi-modal** support: Design an AI-powered narrative using YiVal's multi-modal support of simultaneous text and images. It supports native and seamless [Reinforcement Learning from Human Feedback](https://en.wikipedia.org/wiki/Reinforcement_learning_from_human_feedback)(RLHF) and [Reinforcement Learning from AI Feedback](https://arxiv.org/abs/2309.00267)(RLAIF). Please watch the video above for this use case.                                                |[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DgtDZghleiLEaaNF7f4vSGJ4ChDVls2X?usp=sharing) |
| 🌟 Evaluate performance of multiple LLMs with your own Q&A test dataset | Conveniently **evaluate and compare** performance of your model of choice against 100+ models, thanks to [LiteLLM](https://github.com/BerriAI/litellm). Analyze model performance benchmarks tailored to your **customized test data** or use case.                                                                                                                                                                                                                            |[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1cSjsEKNwDq8W4O2oeRI93vH-BhYH5JXj?usp=sharing) |
| 🔥 Startup Company Headline Generation Bot | Streamline generation of headlines for your startup with automated test data **creation**, prompt **crafting**, results **evaluation**, and performance **enhancement** via GPT-4.                                                                                                                                                                                                                                                                                             |[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1EiWUL8rE_kfNLXVPowCWCh6hwHFagvs_?usp=sharing) |
| 🧳 Build a Customized Travel Guide Bot | Leverage **automated prompts** inspired by the travel **community's** most popular suggestions, such as those from [awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts).                                                                                                                                                                                                                                                                                    |[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1L7miRwTQSZfm5xOKBakWOG5bOumMynpv?usp=sharing) |
| 📖 Build a Cheaper Translator: Use GPT-3.5 to teach Llama2 to create a translator with lower inference cost | Using [Replicate](https://replicate.com/docs/guides/fine-tune-a-language-model) and GPT-3.5's test data, you can **fine-tune** Llama2's translation bot. Benefit from 18x savings while experiencing only a 6% performance decrease.                                                                                                                                                                                                                                           |[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](<https://colab.research.google.com/drive/1HtQOadV0o3vrXjVI9Nf0Xv4rLarqu-fv?usp=sharing>) |
| 🤖️ Chat with Your Favorite Characters - Dantan Ji from Till the End of the Moon | Bring your favorite characters to life through automated prompt creation and **character script retrieval**.                                                                                                                                                                                                                                                                                                                                                                   |[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/12XS1fhgxRAHsRZPXtJ8c5exslgj7EDHE#scrollTo=31Wq1Oeb-bSY) |
| 🔍Evaluate guardrails's performance in generating Python(.py) outputs | [Guardrails](https://github.com/ShreyaR/guardrails): where are my guardrails? 😭 <br>Yival: I am here. ⭐️<br><br>The **integrated evaluation** [experiment](https://github.com/ShreyaR/guardrails/issues/345) is carried out with 80 LeetCode problems in csv, using guardrail and using only GPT-4. The accuracy drops from 0.625 to 0.55 with guardrail, latency increases by 44%, and cost increases by 140%. Guardrail still has a long way to go from demo to production. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](<https://colab.research.google.com/drive/1QgRQmFmC_L07Ler4vbq_vcCNm_OHmJL_#scrollTo=KnmaSTEc13Rg>) |

## Contribution Guidelines

If you want to contribute to YiVal, be sure to review
the [contribution guidelines](https://yival.github.io/YiVal/contributing/).
We use [GitHub issues](https://github.com/YiVal/YiVal/issues) for tracking
requests and bugs.
Please join [YiVal's discord channel](https://discord.gg/HnUWVW4kth) for
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

| **Paper**                                                                                  | **Author**                                                                                                                                                                                                                                                  | **Topics**                        | **YiVal Contributor**                      | **Data Generator**                                                                                                                | **Variation Generator**                                                                                                                                | **Evaluator**                                                                                                                                                                                                                            | **Selector**                                                                                          | **Enhancer**                                                                                                                                                   | **Config**                                                                                                     |
|--------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| [Large Language Models Are Human-Level Prompt Engineers](https://arxiv.org/abs/2211.01910) | [Yongchao Zhou](https://arxiv.org/search/cs?searchtype=author&query=Zhou,+Y), [Andrei Ioan Muresanu](https://arxiv.org/search/cs?searchtype=author&query=Muresanu,+A+I), [Ziwen Han](https://arxiv.org/search/cs?searchtype=author&query=Han,+Z)            | YiVal Evolver, Auto-Prompting     | [@Tao Feng](https://github.com/oliverfeng) | [OpenAIPromptDataGenerator](https://github.com/YiVal/YiVal/blob/master/src/yival/data_generators/openai_prompt_data_generator.py) | [OpenAIPromptVariationGenerator](https://github.com/YiVal/YiVal/blob/master/src/yival/variation_generators/openai_prompt_based_variation_generator.py) | [OpenAIPromptEvaluator](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/openai_prompt_based_evaluator.py), [OpenAIEloEvaluator](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/openai_elo_evaluator.py) | [AHPSelector](https://github.com/YiVal/YiVal/blob/master/src/yival/result_selectors/ahp_selection.py) | [OpenAIPromptBasedCombinationImprover](https://github.com/YiVal/YiVal/blob/master/src/yival/combination_improvers/openai_prompt_based_combination_improver.py) | [config](https://github.com/YiVal/YiVal/blob/master/demo/configs/headline_generation_improve.yml)              |
| [BERTScore: Evaluating Text Generation with BERT](https://arxiv.org/abs/1904.09675)        | [Tianyi Zhang](https://arxiv.org/search/cs?searchtype=author&query=Zhang,+T), [Varsha Kishore](https://arxiv.org/search/cs?searchtype=author&query=Kishore,+V), [Felix Wu](https://arxiv.org/search/cs?searchtype=author&query=Wu,+F)                       | YiVal Evaluator, bertscore, rouge | [@crazycth](https://github.com/crazycth)   | -                                                                                                                                 | -                                                                                                                                                      | [BertScoreEvaluator](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/bertscore_evaluator.py)                                                                                                                             | -                                                                                                     | -                                                                                                                                                              | -                                                                                                              |
| [AlpacaEval](https://github.com/tatsu-lab/alpaca_eval)                                     | [Xuechen Li](https://arxiv.org/search/cs?searchtype=author&query=Xuechen%20Li), [Tianyi Zhang](https://arxiv.org/search/cs?searchtype=author&query=Tianyi%20Zhang), [Yann Dubois](https://arxiv.org/search/cs?searchtype=author&query=Yann%20Dubois) et. al | YiVal Evaluator                   | [@Tao Feng](https://github.com/oliverfeng) | -                                                                                                                                 | -                                                                                                                                                      | [AlpacaEvalEvaluator](https://github.com/YiVal/YiVal/blob/master/src/yival/evaluators/alpaca_eval_evaluator.py)                                                                                                                          | -                                                                                                     | -                                                                                                                                                              | [config](https://github.com/YiVal/YiVal/blob/master/demo/configs/alpaca_eval.yml)                              |
 [Chain of Density](https://arxiv.org/pdf/2309.04269.pdf)                                   | [Griffin Adams](https://arxiv.org/search/?query=Griffin+Adam) [Alexander R. Fabbri](https://arxiv.org/search/?query=Alexander+R.+Fabbri) et. al                                                                                                             | Prompt Engineering                | [@Tao Feng](https://github.com/oliverfeng) | -                                                                                                                                 | [ChainOfDensityGenerator](https://github.com/YiVal/YiVal/blob/master/src/yival/variation_generators/chain_of_density_prompt.py)                        | -                                                                                                                                                                                                                                        | -                                                                                                     | -                                                                                                                                                              | [config](https://github.com/YiVal/YiVal/blob/master/demo/configs/summary_config.yml)                           |
 [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409)                    | [Chengrun Yang](https://arxiv.org/search/cs?searchtype=author&query=Yang,+C) [Xuezhi Wang](https://arxiv.org/search/cs?searchtype=author&query=Wang,+X) et. al                                                                                              | Prompt Engineering                | [@crazycth](https://github.com/crazycth)   | -                                                                                                                                 | -                                                                                                                                                      | -                                                                                                                                                                                                                                        | -                                                                                                     | [optimize_by_prompt_improver](https://github.com/YiVal/YiVal/blob/opro_implement/src/yival/combination_improvers/optimize_by_prompt_improver.py)               | [config](https://github.com/YiVal/YiVal/blob/opro_implement/demo/configs/headline_generation_improve.yml#L174) | 123213 | [Chengrun Yang](https://arxiv.org/search/cs?searchtype=author&query=Yang,+C) [Xuezhi Wang](https://arxiv.org/search/cs?searchtype=author&query=Wang,+X) et. al | Prompt Engineering |[@crazycth](https://github.com/crazycth) |-  | - |-  |- |[optimize_by_prompt_improver](https://github.com/YiVal/YiVal/blob/opro_implement/src/yival/combination_improvers/optimize_by_prompt_improver.py)  | [config](https://github.com/YiVal/YiVal/blob/opro_implement/demo/configs/headline_generation_improve.yml#L174)|
 [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)     | [Edward J. Hu](https://arxiv.org/search/cs?searchtype=author&query=Hu,+E+J) [Yelong Shen](https://arxiv.org/search/cs?searchtype=author&query=Shen,+Y) et. al                                                                                               | LLM Finetune                      | [@crazycth](https://github.com/crazycth)   | -                                                                                                                                 | -                                                                                                                                                      | -                                                                                                                                                                                                                                        | -                                                                                                     | [sft_trainer](https://github.com/YiVal/YiVal/blob/add_finetune_module/src/yival/finetune/sft_trainer.py#L40)                                                   | [config](https://github.com/YiVal/YiVal/blob/add_finetune_module/src/yival/schemas/trainer_configs.py#L48)     |

<!--  -->
