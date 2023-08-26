# 🧚🏻‍️ YiVal

⚡ Build any AIGC application with evaluation and improvement ⚡

Check our main website [here]().

👉 Follow us: [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/YiValai.svg?style=social&label=Follow%20%40YiVal)](https://twitter.com/yivalloveaigc) | 
[![](https://dcbadge.vercel.app/api/server/UBWW23E3?compact=true&style=flat)](https://discord.gg/UBWW23E3)

[![Downloads](https://static.pepy.tech/badge/YiVal/month)](https://pepy.tech/project/YiVal)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub star chart](https://img.shields.io/github/stars/YiVal/YiVal?style=social)](https://star-history.com/#YiVal/YiVal)
[![Dependency Status](https://img.shields.io/librariesio/github/YiVal/YiVal)](https://libraries.io/github/YiVal/YiVal)
[![Open Issues](https://img.shields.io/github/issues-raw/YiVal/YiVal)](https://github.com/YiVal/YiVal/issues)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/YiVal/YiVal)

**Production Support:** As you move your YiVal into production, we'd love to offer more hands-on support.
Fill out [this form]() to share more about your use cases, and our team try our best to support !

## 🤔 What is YiVal?

YiVal is an AIGC-Ops framework that allows you to iteratively tune your **AIGC model metadata, prompts and retrieval
configs** all at once with your preferred choices of test dataset generation, evaluation algorithms and improvement strategies(RLHF
or algorithm
based). [Check out our quickstart guide!]() →

🔧 Experiment Mode:

```mermaid
%%{init: { 'theme': 'default', 'flowchart': { 'htmlLabels': false, 'width': '50px', 'height': '50px' } }}%%
graph TD
    A[Define your AI/ML task] --> B[Test dataset generation]
    B --> C[Evaluation]
    C --> D[Improve]
    D --> C
    D --> E[Ideal settings for inference]
```

🤖 Agent Mode (Auto-prompting):

```mermaid
%%{init: { 'theme': 'default', 'flowchart': { 'htmlLabels': false, 'width': '50px', 'height': '50px' } }}%%
graph TD
    A[Define your AI/ML task] --> B[Automated prompting]
    B --> C[Ideal settings for inference]
```

## Installation

```sh
pip install yival
```


### Fun Cast Fortune Telling

Dive into the world of YiChing and discover your fortune on our index page.
A fun and interactive way to get started with Yival.

![Screenshot 2023-08-16 at 10 50 57 PM](https://github.com/YiVal/YiVal/assets/1544154/b5c04295-7809-4331-8cce-cc4a1ceea73c)



## Demo

### Basic Interactive Mode

To get started with a demo for basic interactive mode of YiVal,
run the following command:

```sh
yival demo --basic_interactive
```

Once started, navigate to the following address in your web browser:

<http://127.0.0.1:8073/interactive>

![Screenshot 2023-08-17 at 10 55 31 PM](https://github.com/YiVal/YiVal/assets/1544154/a720c3ad-1288-4830-8a3d-377d9827f46e)

For more details on this demo,
check out the [Basic Interactive Mode Demo].

[Basic Interactive Mode Demo]:https://github.com/YiVal/YiVal/blob/master/docs/basic_interactive_mode.md#demo

### Question Answering with expected result evaluator

```sh
yival demo --qa_expected_results
```

Once started, navigate to the following address in your web browser:

<http://127.0.0.1:8073/>

![Screenshot 2023-08-18 at 1 11 44 AM](https://github.com/YiVal/YiVal/assets/1544154/4e9a182f-07ba-413e-9160-f38bfdc743ce)

For more details on this demo,
check out the [Question Answering with expected result evaluator].

[Question Answering with expected result evaluator]:https://github.com/YiVal/YiVal/blob/master/docs/qa_expected_results.md#demo

### Auto prompts generation

```sh
yival demo --auto_prompts
```

![Screenshot 2023-08-20 at 10 53 36 PM](https://github.com/YiVal/YiVal/assets/1544154/85f5c08f-3e14-42e7-85c6-47dcdd4a4121)

For more details on this demo,
check out the [Auto prompts generation].

[Auto prompts generation]:https://github.com/YiVal/YiVal/blob/master/docs/auto_prompts_generation.md#demo
