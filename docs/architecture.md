# Architecture

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

## Data Generation

The process starts with the generation of a dataset which can come from multiple sources:

- **Specific Data Generator**: A defined method or algorithm that automatically churns out data.
- **Data Reader**: A component that reads data from external places.
- **Manual Input**: As straightforward as it sounds, data can be added manually.

## Combination Creation

Once we have our dataset, we form combinations that are pivotal for the subsequent analysis:

- Formed using specific combination creators.
- Defined manually.

## Analysis

This is the heart of the Yival framework. A custom function provided by the user
takes in the dataset and combination list to produce valuable insights.

## Evaluation

After analysis, the results are subjected to evaluation. Several methodologies
can be applied to grasp and gauge the data's behavior deeply.

## Selection

From the evaluations, the most promising results are selected. This process
ensures only the most vital insights are pushed forward.

## Improvement

The selected results are then fine-tuned in this phase. An "Improver" is applied
to enhance these results. This stage can loop back to the analysis stage, indicating an ongoing, iterative process of refinement.
