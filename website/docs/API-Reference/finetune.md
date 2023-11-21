---
sidebar_position: 11

---

# Finetune 

##  `OpenAIFineTuneUtils`

###   Introduction 

  This module is designed to fine-tune OpenAI's GPT model using a specified dataset and conditions. It provides a utility for extracting relevant results from an experiment, transforming this data into the desired format, and then leveraging OpenAI's API to perform fine-tuning.

  It takes ExperimentResult dump (pkl), and filtered conditions to extract the result.

###   Class Definition 

####    Description

####    Attributes

###   Example 

```Python
def main():
    finetune(
        'test_demo_results.pkl',
        "name == openai_prompt_based_evaluator AND result >= 0 AND display_name == clarity",
    )
```

##  `SFTTrainer`

###   Introduction 

  The `SFTTrainer` class is designed to finetune a pre-trainer model on a specific task. It's a part of the yival framework that allows for easy and efficient fine-tuning of models. The class is built on top of the Hugging Face Transformers library and provides a high-level, easy-to-use API for fine-tuning.

  The `SFTTrainer` class supports fine-tuning with different configurations, including enabling bits and bytes for quantization and LoRA for low-rank adaptation. It also supports different training arguments such as batchsize、learning_rate and number of epochs.

  We recommend two ways to use Yival's SFTTrainer.

- Use various dataset generators built into Yival (including huggingface, openai_generator, etc.) for data upload or generation, and then finetune the model 
- Provide a custom_func, use advanced models like GPT-4 for data generation, and customize the selection criteria. The model is then finetuned based on the selected data.

###   `DataSetConfig` 

####    Description

   Configuration class for the training arguments. It specifies various parameters including per device train batch size, gradient accumulation steps, gradient checkpointing, max grad norm, num train epochs, learning rate, bf16, save total limit, logging steps, optim, lr scheduler type, warmup ratio, and log level.

####    Attributes

- **`per_device_train_batch_size(int)`**:
  - specifies the batch size for training per device.
- **`gradient_accumulation_steps(int)`**:
  - specifies the number of steps to accumulate gradients before updating.
- **`gradient_checkpointing(bool)`**:
  - specifies whether to use gradient checkpointing to save memory.
- **`max_grad_norm(float)`**:
  - specifies the maximum norm of the gradients.
- **`num_train_epochs(int)`**:
  - specifies the number of training epochs.
- **`learning_rate(float)`**:
  - specifies the learning rate.
- **`bf16(bool)`**:
  - specifies whether to use bf16 precision for training.
- **`save_total_limit(int)`**:
  - specifies the total number of checkpoints to save.
- **`logging_steps(int)`**:
  - specifies the number of steps between logging.
- **`optim(str)`**:
  - specifies the optimizer to use for training.
- **`lr_scheduler_type(str)`**:
  - specifies the type of learning rate scheduler to use.
- **`warmup_ratio(float)`**:
  - specifies the warmup ratio for the learning rate scheduler.
- **`log_level(str)`**:
  - specifies the log level.

###   `TrainArguments`

####    Description

   Configuration class for the dataset. It specifies various parameters including prompt key, completion key, formatting prompts format, and condition.

####    Attributes

###   `BnbConfig`

####    Description

   Configuration class for the bits and bytes. It specifies whether to load in 4 bit or 8 bit.

####    Attributes

- **`load_in_4_bit(bool)`**:
  - specifies whether to load in 4 bit.
- **`load_in_8_bit(bool)`**:
  - specifies whether to load in 8 bit.



###   `LoRAConfig`

####    Description

   Configuration class for the LoRA. It specifies various parameters including r, lora alpha, bias, task type, lora dropout, and inference mode.

####    Attributes

- **`r(int)`**:
  - specifies the rank for the LoRA.
- **`lora_alpha(int)`**:
  - specifies the alpha for the LoRA.
- **`bias(str)`**:
  - specifies the bias for the LoRA.
- **`task_type(str)`**:
- specifies the task type for the LoRA.
- **`lora_dropout(float)`**:
  - specifies the dropout for the LoRA.
- **`inference_mode(bool)`**:
  - specifies whether to use inference mode for the LoRA.

###   Example 

####    Dataset load and finetune model in yival config

```YAML
description: Generated experiment config
dataset:
  data_generators:
    openai_prompt_data_generator:
      chunk_size: 100000
      diversify: true
      # model_name specify the llm model , e.g. a16z-infra/llama-2-13b-chat:9dff94b1bed5af738655d4a7cbcdcde2bd503aa85c94334fe1f42af7f3dd5ee3
      model_name: gpt-4
      prompt:
          "Please provide a concrete and realistic test case as a dictionary for function invocation using the ** operator.
          Only include parameters, excluding description and name.
          Ensure it's succinct and well-structured.
          **Only provide the dictionary.**"
      input_function:
        description:
          The current function is to evaluate the English to Chinese translation ability of the large language model. You will play the role of a teacher, so please provide a coherent English sentence (teacher_quiz), and give the corresponding Chinese translation (teachaer_answer).
        name: translation_english_to_chinese
        parameters:
          teacher_quiz: str
          teacher_answer: str
      expected_param_name: teacher_answer
      number_of_examples: 5
      output_path: english2chinese1.pkl
  source_type: machine_generated

trainer:
  name: sft_trainer
  model_name: PY007/TinyLlama-1.1B-Chat-v0.3
  output_path: output
  dataset_config:
    prompt_key: teacher_quiz
  enable_lora: False
  enable_bits_and_bytes: False
```

- Custom_func then customize the selection criteria. The model is then finetuned based on the selected data in yival config

```YAML
custom_function: demo.headline_generation_detail.headline_generation
description: Generated experiment config
dataset:
  data_generators:
    openai_prompt_data_generator:
      chunk_size: 100000
      diversify: true
      # model_name specify the llm model , e.g. a16z-infra/llama-2-13b-chat:9dff94b1bed5af738655d4a7cbcdcde2bd503aa85c94334fe1f42af7f3dd5ee3
      model_name: gpt-4
      prompt:
          "Please provide a concrete and realistic test case as a dictionary for function invocation using the ** operator.
          Only include parameters, excluding description and name.
          Ensure it's succinct and well-structured.
          **Only provide the dictionary.**"
      input_function:
        description:
          "Given a tech startup business named [tech_startup_business], specializing in [business], and target_peopleing [target_people], generate a corresponding landing page headline."
        name: headline_generation_for_business
        parameters:
          tech_startup_business: str
          business: str
          target_people: str
      number_of_examples: 3
      output_path: null
  source_type: machine_generated

variations:
  - name: task
    variations:
      - instantiated_value: Generate landing page headline for {tech_startup_business}, company business is {business}, target_people is {target_people}
        value: Generate landing page headline for {tech_startup_business}, company business is {business}, target_people is {target_people}
        value_type: str
        variation_id: null

evaluators:
  - evaluator_type: individual
    metric_calculators:
      - method: AVERAGE
    name: openai_prompt_based_evaluator
    display_name: clear
    prompt: |-
      You are assessing a submitted answer on a given task based on a criterion. Here is the data:
      - Task: Given an tech startup business, generate one corresponding landing page headline
      - Does the headline clearly communicate what the startup does or what problem it solves?
        It should be immediately clear to anyone who reads the headline what the startup's purpose is.
        A lack of clarity can lead to confusion and may discourage potential users or investors.
      [Input]: {tech_startup_business}
      [Result]: {raw_output}
      Answer the question by selecting one of the following options:
      A It fails to meet the criterion at all.
      B It somewhat meets the criterion, but there is significant room for improvement.
      C It meets the criterion to a satisfactory degree.
      D It meets the criterion very well.
      E It meets the criterion exceptionally well, with little to no room for improvement.
    choices: ["A", "B", "C", "D", "E"]
    # model_name specify the llm model , e.g. a16z-infra/llama-2-13b-chat:9dff94b1bed5af738655d4a7cbcdcde2bd503aa85c94334fe1f42af7f3dd5ee3
    model_name: gpt-4
    description: "evaluate the quality of the landing page headline"
    scale_description: "0-4"
    choice_scores:
      A: 0
      B: 1
      C: 2
      D: 3
      E: 4

selection_strategy:
  ahp_selection:
    criteria:
      - "openai_prompt_based_evaluator: clear"
      - average_token_usage
      - average_latency
    criteria_maximization:
      "openai_prompt_based_evaluator: clear": true
      average_latency: false
      average_token_usage: false
    criteria_weights:
      "openai_prompt_based_evaluator: clear": 0.6
      average_latency: 0.2
      average_token_usage: 0.2
    normalize_func: "z-score"

trainer:
  name: sft_trainer
  model_name: PY007/TinyLlama-1.1B-Chat-v0.3
  output_path: output
  dataset_config:
    prompt_key: teacher_quiz
    condition: "name == openai_prompt_based_evaluator AND result >= 0 AND display_name == clear"
  enable_lora: False
  enable_bits_and_bytes: False
```

##  `BackUpSFTTrainer`

###   Introduction

###   Class Definition

####    Description

####    Attributes

###   Example

