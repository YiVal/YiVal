# YiVal: Adaptable AI Development Framework

YiVal stands at the intersection of flexibility
and adaptability in the AI development landscape.
Crafted meticulously for those who seek a tailored experimentation experience,
it effortlessly caters to both hands-on developers and those who lean into automation.

## Table of Contents

- [YiVal: Adaptable AI Development Framework](#yival-adaptable-ai-development-framework)
    - [Table of Contents](#table-of-contents)
    - [Overview](#overview)
        - [Fun Cast Fortune Telling](#fun-cast-fortune-telling)
        - [Experimentation](#experimentation)
        - [Additional Features](#additional-features)
    - [AIGC app development flow](#aigc-app-development-flow)
    - [Installation](#installation)
    - [Demo](#demo)
        - [Basic Interactive Mode](#basic-interactive-mode)
        - [Question Answering with expected result evaluator](#question-answering-with-expected-result-evaluator)
        - [Auto prompts generation](#auto-prompts-generation)

## Overview

At its core, YiVal is more than just a framework—it's a philosophy.
A philosophy that believes in offering tools
that can be seamlessly molded to fit unique experimentation needs.
With a robust architecture and versatile components,
Yival ensures that every AI journey,
regardless of its complexity, is smooth and efficient.

### Fun Cast Fortune Telling

Dive into the world of YiChing and discover your fortune on our index page.
A fun and interactive way to get started with Yival.

![Screenshot 2023-08-16 at 10 50 57 PM](https://github.com/YiVal/YiVal/assets/1544154/b5c04295-7809-4331-8cce-cc4a1ceea73c)

### Experimentation

- **Experiment Result Analysis**:
    Gain insights into aggregated outputs for each combination,
    evaluator outcomes, average latency, token usage, and sample test case results.
    The best combinations will be highlighted for ease of reference.

    ![Screenshot 2023-08-16 at 10 51 57 PM](https://github.com/YiVal/YiVal/assets/1544154/054e7659-ceb1-4048-af4e-301958b0b675)

- **Data Analysis Page**:
    Delve deep into your experiment data,
    extracting meaningful insights and patterns that can guide further experimentation.

    ![Screenshot 2023-08-16 at 10 54 50 PM](https://github.com/YiVal/YiVal/assets/1544154/3440b51c-f607-477d-9092-94be94b4ebbe)

- **Detailed Test Results**:
    A granular look at each test case result for every combination,
    providing a comprehensive understanding of the experiment's outcomes.

    ![Screenshot 2023-08-16 at 10 57 22 PM](https://github.com/YiVal/YiVal/assets/1544154/8f1f9e04-e94c-473e-b7f8-83e6ce0f16e8)

- **Improver Experiment Result Analysis**:
    After the improvement phase, see the aggregated outputs for each combination.
    This includes evaluator outputs, average latency, token usage,
    and sample test cases, with the best combinations highlighted.

    ![Screenshot 2023-08-16 at 10 57 58 PM](https://github.com/YiVal/YiVal/assets/1544154/fd087b34-d3d4-48bb-800e-68cf09e47e5d)

- **Improver Detailed Test Results**:
    Post-improvement,
    this page offers a detailed view of each test case result for every combination,
    showcasing the enhancement in results.

    ![Screenshot 2023-08-16 at 10 58 18 PM](https://github.com/YiVal/YiVal/assets/1544154/3145de90-04b4-4cd6-8405-fae0ecb40545)

### Additional Features

- **Export Data**:
    Securely store and export your experiment for future reference
    or to share with peers.

    ![Screenshot 2023-08-16 at 10 59 01 PM](https://github.com/YiVal/YiVal/assets/1544154/2664fd03-0a3c-43ff-b065-8ea6cf440158)

- **Rating**:
    Human touch matters.
    Add ratings to each test case on the experiment results page
    based on configurable criteria.

    ![Screenshot 2023-08-16 at 10 59 18 PM](https://github.com/YiVal/YiVal/assets/1544154/87161a42-711a-4fc5-bb87-93e79d745554)

- **Interactive Mode**:
    Flexibility at its best.
    Enter new test cases for combinations,
    tailoring your experimentation in real-time.

    ![Screenshot 2023-08-16 at 11 02 37 PM](https://github.com/YiVal/YiVal/assets/1544154/f2ed3997-5f3c-4376-89a8-3ed3c5df0720)

## AIGC app development flow

The flowchart below depicts the core flow of ideal AI Generated Content (AIGC)
app development that Yival tries to support.
This emphasis on iteration ensures a continuous cycle of improvement,
allowing developers to hone their applications to perfection.

```mermaid
flowchart TD

A{Test Data}
B[Core App Development]
C[Evaluation]
D[Refinement]

A --> B
B --> C
C -->|Check| D
D -->|YiVal Supports Iteration| B

subgraph "Core App Development"
    B1[Retrieve Data]
    B2[Collaborate with Models]
    B3[Select Best Model]
    B4[Prompt Development]
end

subgraph Evaluation
    C1[Human Evaluator]
    C2[Auto Evaluator]
    C --> C1
    C --> C2
end

subgraph Refinement
    D1[Human Improver]
    D2[Auto Improver]
    D --> D1
    D --> D2
end

```

## Installation

```sh
pip install yival
```

## Demo

With just the creation of a configuration file, you can easily use yival to evaluate different experiment environments, fitting unique experimentation needs. For example , we can define a pipeline that XX as follow :

```
# yaml
```

### Write landing page headlines for statups

<!-- we provide Google Colab demo for you to experience YiVal's functionality without any setup required, which is a great way to get a hands-on feel for what is Yival!

#### Write landing page headlines for statups -->

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1EiWUL8rE_kfNLXVPowCWCh6hwHFagvs_?usp=sharing)

In this demo, we aim to find the optimal prompt that allows GPT-4 to generate landing page headlines based on company names. In this demo, LLM not only generates the prompt and test data, but also evaluates the results and selects the optimal prompt.

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
