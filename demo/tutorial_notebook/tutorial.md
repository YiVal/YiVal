<!-- markdownlint-disable MD033 -->
# Yival Tutorial

We provide some easy-to-use demos for you to directly experience the effect
of Yival in the README on Github.

## Startup Company Headline Generation 🤖

* google colab : [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1EiWUL8rE_kfNLXVPowCWCh6hwHFagvs_?usp=sharing)
* notebook : [headline_generation](./headline_generation.ipynb)

The goal of this demo is to generate corresponding page headlines based on the
names of startup companies. YiVal supports automatic generation of related prompts
and test data according to this goal, and self-evaluation based on the configured
evaluator. It provides different result selection methods such as AHP to confirm
the final result.

>For how to confirm the prompt used by the generator, we recommend using a
step-by-step optimization pipeline mode, continuously adjusting based on
the test case results. We provide an example : [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1tr5s_adAPmI9Mv6Zz97JnTGIh3mGojsi?usp=sharing)

## Animal story with MidJourney 🐯

* google colab : [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DgtDZghleiLEaaNF7f4vSGJ4ChDVls2X?usp=sharing)
* notebook : [animal_story](./animal_story.ipynb)

Yival now supports image now , and in near future We will equip Yival
with full modality capabilities (including sound, video, etc.) in
near future.

In this demo, we only need to provide the initial prompt, and Yival will
generate a variety of animal types and personalities, and write cute and
concise animal stories based on different story templates. Finally,
corresponding images are generated through Midjourney. What's surprising
is that this series of actions is completely automated, you only need to
provide a prompt.

![hello](https://uninaruto.oss-cn-shanghai.aliyuncs.com/img/816211693805398_.pic_hd.jpg)

## Model comparison

* google colab: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DgtDZghleiLEaaNF7f4vSGJ4ChDVls2X?usp=sharing)
* notebook : [model_comparison](./model_comparison.ipynb)

For NLP practitioners, a common issue is evaluating the capabilities of
different models. Yival provides a variety of generalized evaluation methods,
requiring only the provision of data and configuration files.In this demo,
we conducted a horizontal comparison of the QA capabilities of the following
four models:

* gpt-3.5-turbo
* llama-2-13b-chat
* llama-2-70b-chat
* vicuna-13b

## Basic Demo

### Basic Interactive Mode

To get started with a demo for basic interactive mode of YiVal, run the following
command:

```shell
yival demo --basic_interactive
```

Once started, navigate to the following address in your web browser:

<http://127.0.0.1:8073/interactive>
<details>
  <summary>Click to view the screenshot</summary>
  
  ![Screenshot 2023-08-17 at 10 55 31 PM](https://github.com/YiVal/YiVal/assets/1544154/a720c3ad-1288-4830-8a3d-377d9827f46e)
  
</details>

For more details on this demo, check out the [Basic Interactive Mode Demo](https://github.com/YiVal/YiVal/blob/master/docs/docs/basic_interactive_mode.md#demo).

### Question Answering with expected result evaluator

```shell
yival demo --qa_expected_results
```

Once started, navigate to the following address in your web browser:
<http://127.0.0.1:8073/>
<details>
  <summary>Click to view the screenshot</summary>
  
 <img width="1288" alt="Screenshot 2023-08-18 at 1 11 44 AM" src="https://github.com/YiVal/YiVal/assets/1544154/4e9a182f-07ba-413e-9160-f38bfdc743ce">

</details>

For more details, check out the [Question Answering with expected result evaluator](https://github.com/YiVal/YiVal/blob/master/docs/qa_expected_results.md#demo)
