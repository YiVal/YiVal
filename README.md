# YiVal: Adaptable AI Development Framework

YiVal stands at the intersection of flexibility and adaptability in the AI development landscape. Crafted meticulously for those who seek a tailored experimentation experience, it effortlessly caters to both hands-on developers and those who lean into automation.

## Table of Contents

- [YiVal: Adaptable AI Development Framework](#yival-adaptable-ai-development-framework)
    - [Table of Contents](#table-of-contents)
    - [Overview](#overview)
        - [Fun Cast Fortune Telling](#fun-cast-fortune-telling)
        - [Experimentation](#experimentation)
        - [Additional Features](#additional-features)
    - [Architecture](#architecture)
        - [Data Generation](#data-generation)
        - [Combination Creation](#combination-creation)
        - [Analysis](#analysis)
        - [Evaluation](#evaluation)
        - [Selection](#selection)
        - [Improvement](#improvement)
    - [Installation](#installation)
    - [Demo](#demo)
        - [Basic Interactive Mode](#basic-interactive-mode)

## Overview

At its core, YiVal is more than just a framework—it's a philosophy. A philosophy that believes in offering tools that can be seamlessly molded to fit unique experimentation needs. With a robust architecture and versatile components, Yival ensures that every AI journey, regardless of its complexity, is smooth and efficient.

<details>
<summary> Web UI</summary>

### Fun Cast Fortune Telling

Dive into the world of YiChing and discover your fortune on our index page. A fun and interactive way to get started with Yival.
<img width="1344" alt="Screenshot 2023-08-16 at 10 50 57 PM" src="https://github.com/YiVal/YiVal/assets/1544154/b5c04295-7809-4331-8cce-cc4a1ceea73c">

### Experimentation

- **Experiment Result Analysis**: Gain insights into aggregated outputs for each combination, evaluator outcomes, average latency, token usage, and sample test case results. The best combinations will be highlighted for ease of reference.
<img width="1360" alt="Screenshot 2023-08-16 at 10 51 57 PM" src="https://github.com/YiVal/YiVal/assets/1544154/054e7659-ceb1-4048-af4e-301958b0b675">

- **Data Analysis Page**: Delve deep into your experiment data, extracting meaningful insights and patterns that can guide further experimentation.
<img width="1349" alt="Screenshot 2023-08-16 at 10 54 50 PM" src="https://github.com/YiVal/YiVal/assets/1544154/3440b51c-f607-477d-9092-94be94b4ebbe">

- **Detailed Test Results**: A granular look at each test case result for every combination, providing a comprehensive understanding of the experiment's outcomes.
<img width="1321" alt="Screenshot 2023-08-16 at 10 57 22 PM" src="https://github.com/YiVal/YiVal/assets/1544154/8f1f9e04-e94c-473e-b7f8-83e6ce0f16e8">

- **Improver Experiment Result Analysis**: After the improvement phase, see the aggregated outputs for each combination. This includes evaluator outputs, average latency, token usage, and sample test cases, with the best combinations highlighted.
<img width="1322" alt="Screenshot 2023-08-16 at 10 57 58 PM" src="https://github.com/YiVal/YiVal/assets/1544154/fd087b34-d3d4-48bb-800e-68cf09e47e5d">

- **Improver Detailed Test Results**: Post-improvement, this page offers a detailed view of each test case result for every combination, showcasing the enhancement in results.
<img width="1283" alt="Screenshot 2023-08-16 at 10 58 18 PM" src="https://github.com/YiVal/YiVal/assets/1544154/3145de90-04b4-4cd6-8405-fae0ecb40545">

### Additional Features

- **Export Data**: Securely store and export your experiment for future reference or to share with peers.
<img width="295" alt="Screenshot 2023-08-16 at 10 59 01 PM" src="https://github.com/YiVal/YiVal/assets/1544154/2664fd03-0a3c-43ff-b065-8ea6cf440158">

- **Rating**: Human touch matters. Add ratings to each test case on the experiment results page based on configurable criteria.
<img width="1132" alt="Screenshot 2023-08-16 at 10 59 18 PM" src="https://github.com/YiVal/YiVal/assets/1544154/87161a42-711a-4fc5-bb87-93e79d745554">

- **Interactive Mode**: Flexibility at its best. Enter new test cases for combinations, tailoring your experimentation in real-time.
<img width="1358" alt="Screenshot 2023-08-16 at 11 02 37 PM" src="https://github.com/YiVal/YiVal/assets/1544154/f2ed3997-5f3c-4376-89a8-3ed3c5df0720">

</details>

## Architecture

### Data Generation

The process starts with the generation of a dataset which can come from multiple sources:

- **Specific Data Generator**: A defined method or algorithm that automatically churns out data.
- **Data Reader**: A component that reads data from external places.
- **Manual Input**: As straightforward as it sounds, data can be added manually.

### Combination Creation

Once we have our dataset, we form combinations that are pivotal for the subsequent analysis:

- Formed using specific combination creators.
- Defined manually.

### Analysis

This is the heart of the Yival framework. A custom function provided by the user takes in the dataset and combination list to produce valuable insights.

### Evaluation

After analysis, the results are subjected to evaluation. Several methodologies can be applied to grasp and gauge the data's behavior deeply.

### Selection

From the evaluations, the most promising results are selected. This process ensures only the most vital insights are pushed forward.

### Improvement

The selected results are then fine-tuned in this phase. An "Improver" is applied to enhance these results. This stage can loop back to the analysis stage, indicating an ongoing, iterative process of refinement.

```mermaid
flowchart TD

    %% Data Generation Stage
    A[Start]
    A --> |Data Generation| A1[Dataset]
    A1 --> A2[DataGenerator]
    A2 --> A3[Specific Generator]
    A1 --> A4[DataReader]
    A4 --> A5[Specific Reader]
    A1 --> A6[Manual Input]

    %% Create Combinations Stage
    A1 --> |Create Combinations| B
    B --> B1[Specific Combination Creator]
    B --> B2[Set Combinations Manually]
    B --> B3[List of Combinations]

    %% Evaluate Stage
    B3 --> |Analysis| C
    C --> C1[User's Function]
    C --> C2[Results from Function]
    A1 --> C1

    %% Evaluator Stage
    C2 --> |Evaluation| D
    D --> D1[Method 1]
    D --> D2[Method 2]
    D --> D3[Method 3]

    %% Select Stage
    D --> |Selection| E

    %% Improver Stage
    E --> |Improvement| F
    F --> F1[Improver]
    F1 --> C

    %% Styling
    style A fill:#f9d77e,stroke:#f96e5b
    style B fill:#a1d4c6,stroke:#f96e5b
    style C fill:#f6c3d5,stroke:#f96e5b
    style D fill:#b2b1cf,stroke:#f96e5b
    style E fill:#f9efaa,stroke:#f96e5b
    style F fill:#f2a3b3,stroke:#f96e5b
```

## Installation

```
pip install yival
```

## Demo

### Basic Interactive Mode

To get started with a demo of YiVal, run the following command:

```
yival demo --basic_interactive
```

Once started, navigate to the following address in your web browser:

<http://127.0.0.1:8073/interactive>
<details>
  <summary>Click to view the screenshot</summary>
  
  ![Screenshot 2023-08-17 at 10 55 31 PM](https://github.com/YiVal/YiVal/assets/1544154/a720c3ad-1288-4830-8a3d-377d9827f46e)
  
</details>

For more details on our demo, check out the [Basic Interactive Mode Demo](https://github.com/YiVal/YiVal/blob/master/docs/docs/basic_interactive_mode.md#demo).
