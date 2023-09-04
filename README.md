<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD041 -->

<p align="center">
    <h1 align="center">🧚🏻‍️ YiVal</h1>
</p>

<p align="center">
  <a aria-label="website" href="" target="_blank">
    Website
  </a>
  ·
  <a aria-label="producthunt" href="" target="_blank">
    Producthunt
  </a>
·
  <a aria-label="producthunt" href="" target="_blank">
    Documentation
  </a>

</p>

<p align="center">
    <h5 align="center">⚡ Build any Generative AI application with evaluation
        and improvement ⚡</h5>
</p>

<!-- markdownlint-disable-next-line MD013 -->
👉 Follow us: [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/YiValai.svg?style=social&label=Follow%20%40YiVal)](https://twitter.com/yivalloveaigc) |
[![Discord](https://dcbadge.vercel.app/api/server/4V4jyt2K?compact=true&style=flat)](https://discord.gg/4V4jyt2K)

[![Downloads](https://static.pepy.tech/badge/YiVal/month)](https://pepy.tech/project/YiVal)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub star chart](https://img.shields.io/github/stars/YiVal/YiVal?style=social)](https://star-history.com/#YiVal/YiVal)
[![Dependency Status](https://img.shields.io/librariesio/github/YiVal/YiVal)](https://libraries.io/github/YiVal/YiVal)
[![Open Issues](https://img.shields.io/github/issues-raw/YiVal/YiVal)](https://github.com/YiVal/YiVal/issues)

## 🤔 What is YiVal?

YiVal is an GenAI-Ops framework that allows you to iteratively tune your **Generative
 AI model metadata, params, prompts and retrieval configs** all at once with your
 preferred choices of test dataset generation, evaluation algorithms and improvement
strategies.
  <!-- markdownlint-disable-next-line MD013 -->
[Check out our quickstart guide!](https://github.com/YiVal/YiVal/blob/master/demo/tutorial_notebook/tutorial.md) →

## 📣 What's Next?

### Expected Features in Sep

- Add ROUGE and BERTScore evaluators
- Add support to midjourney
- Add support to LLaMA2-70B, LLaMA2-7B, Falcon-40B,
- Support LoRA fine-tune to open source models

## 🚀 Features

|          | 🔧 Experiment Mode:                                           | 🤖 Agent Mode (Auto-prompting):                               |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Workflow | Define your AI/ML application ➡️ Define test dataset ➡️ Evaluate 🔄 Improve ➡️ Prompt related artifacts built ✅ | Define your AI/ML application ➡️ Auto-prompting ➡️ Prompt related artifacts built ✅ |
| Features | 🌟 Streamlined prompt development process<br/> 🌟 Support for multimedia and multimodel<br/> 🌟 Support CSV upload and GPT4 generated test data<br/>🌟 Dashboard tracking latency, price and evaluator results<br/> 🌟 Human(RLHF) and algorithm based improvers <br/>🌟 Service with detailed web view<br/>🌟 Customizable evaluators and improvers | 🌟 Non-code experience of Gen-AI application build<br/>  🌟 Witness your Gen-AI application born and improve with just one click |
| Demos    |                                                              | - Startup Company Headline Generation Bot🔥 [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1EiWUL8rE_kfNLXVPowCWCh6hwHFagvs_?usp=sharing)<br /> - Animal story with MidJourney 🐯 [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DgtDZghleiLEaaNF7f4vSGJ4ChDVls2X?usp=sharing)  |

## Installation

```sh
pip install yival
```

## Demo

### Basic Interactive Mode

To get started with a demo for basic interactive mode of YiVal, run the
following command:

```python
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

```python
yival demo --qa_expected_results
```

Once started, navigate to the following address in your web browser:
<http://127.0.0.1:8073/>
<details>
  <summary>Click to view the screenshot</summary>
  
 <img width="1288" alt="Screenshot 2023-08-18 at 1 11 44 AM" src="https://github.com/YiVal/YiVal/assets/1544154/4e9a182f-07ba-413e-9160-f38bfdc743ce">

</details>

For more details, check out the [Question Answering with expected result evaluator](https://github.com/YiVal/YiVal/blob/master/docs/qa_expected_results.md#demo).

### Fun Cast Fortune Telling

Dive into the world of YiChing and discover your fortune on our index page.
A fun and interactive way to get started with Yival.

![Screenshot 2023-08-16 at 10 50 57 PM](https://github.com/YiVal/YiVal/assets/1544154/b5c04295-7809-4331-8cce-cc4a1ceea73c)

![MidJourney](https://uninaruto.oss-cn-shanghai.aliyuncs.com/img/816211693805398_.pic_hd.jpg)
