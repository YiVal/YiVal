"""
This module provides an implementation of Supervised Fine-tuning trainer.

"""
import os
from pprint import pprint

from transformers import AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments

from ..schemas.experiment_config import Experiment, ExperimentConfig, TrainerOutput
from ..schemas.trainer_configs import DatasetConfig, SFTTrainerConfig, TrainArguments
from .base_trainer import BaseTrainer
from .utils import (
    display_dataset,
    extract_from_input_data,
    get_hg_tokenizer,
    print_trainable_parameters,
)

DEFAULT_PROMPT_FORMAT = """
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\n
### Input: {prompt}
### Output: {completion}
"""


class SFTTrainer(BaseTrainer):
    """
    SFT Trainer implement
    """

    default_config = SFTTrainerConfig(
        name="sft_trainer",
        model_name="PY007/TinyLlama-1.1B-Chat-v0.3",
        output_path="output/",
        dataset_config=DatasetConfig(
            prompt_key="teacher_quiz",
            completioin_key=None,
            formatting_prompts_format=None
        ),
        enable_bits_and_bytes=False,
        bnb_config=None,
        enable_lora=False,
        lora_config=None,
        train_arguments=TrainArguments(),
    )

    def __init__(self, config: SFTTrainerConfig) -> None:
        super().__init__(config)
        self.config: SFTTrainerConfig = config

    def find_all_linear_names(self, model):
        import bitsandbytes as bnb  # type: ignore
        cls = bnb.nn.Linear4bit
        lora_module_names = set()
        for name, module in model.named_modules():
            if isinstance(module, cls):
                names = name.split('.')
                lora_module_names.add(
                    names[0] if len(names) == 1 else names[-1]
                )

        return list(lora_module_names)

    def train(
        self,
        experiment: Experiment,
        experiment_config: ExperimentConfig,
    ) -> TrainerOutput:

        import torch
        from peft import LoraConfig, get_peft_model  # type: ignore
        from trl import SFTTrainer as TRL_SFTTrainer  # type: ignore

        pprint(f"[INFO][sft_trainer] train config:")
        pprint(self.config.asdict())

        #Extract data from experiment according to condition
        assert (isinstance(self.config.dataset_config, dict))
        dataset = extract_from_input_data(
            experiment, self.config.dataset_config.get("prompt_key", None),
            self.config.dataset_config.get("completion_key", None),
            self.config.dataset_config.get("condition", None)
        )
        display_dataset(dataset, 5)

        #Prepare base model and tokenizer
        model_name = self.config.model_name
        tokenizer = get_hg_tokenizer(model_name)

        #Assemble bitsandbytes quant config
        bnb_config = None
        if self.config.enable_bits_and_bytes:
            assert (isinstance(self.config.bnb_config, dict))
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=self.config.bnb_config.load_in_4_bit,
                load_in_8bit=self.config.bnb_config.load_in_8_bit
            )

        #Load base model from hg
        base_model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.half, quantization_config=bnb_config
        )

        #prepare peft, lora e.g.
        peft_config = None
        if self.config.enable_lora:
            assert (isinstance(self.config.lora_config, dict))
            peft_config = LoraConfig(
                r=self.config.lora_config["r"],
                lora_alpha=self.config.lora_config["lora_alpha"],
                target_modules=self.find_all_linear_names(base_model),
                lora_dropout=self.config.lora_config["lora_dropout"],
                task_type=self.config.lora_config["task_type"],
                bias=self.config.lora_config["bias"]
            )
            base_model = get_peft_model(base_model, peft_config)

        print_trainable_parameters(base_model)

        assert (isinstance(self.config.train_arguments, dict))
        # Parameters for training arguments details => https://github.com/huggingface/transformers/blob/main/src/transformers/training_args.py#L158
        output_dir = self.config.output_path
        training_args = TrainingArguments(
            per_device_train_batch_size=self.config.train_arguments.get(
                "per_device_train_batch_size", 4
            ),
            gradient_accumulation_steps=self.config.train_arguments.get(
                "gradient_accumulation_steps", 4
            ),
            gradient_checkpointing=self.config.train_arguments.get(
                "gradient_checkpointing", True
            ),
            max_grad_norm=self.config.train_arguments.get(
                "max_grad_norm", 0.3
            ),
            num_train_epochs=self.config.train_arguments.get(
                "num_train_epochs", 15
            ),
            learning_rate=self.config.train_arguments.get(
                "learning_rate", 2e-4
            ),
            bf16=self.config.train_arguments.get("bf16", False),
            save_total_limit=self.config.train_arguments.get(
                "save_total_limit", 3
            ),
            logging_steps=self.config.train_arguments.get("logging_steps", 1),
            output_dir=output_dir,
            optim=self.config.train_arguments.get(
                "optim", "paged_adamw_32bit"
            ),
            lr_scheduler_type=self.config.train_arguments.get(
                "lr_scheduler_type", "cosine"
            ),
            warmup_ratio=self.config.train_arguments.get("warmup_ratio", 0.05),
            log_level=self.config.train_arguments.get('log_level', 'debug')
        )

        output_dir = self.config.output_path

        def formatting_prompts_func(example):
            output_texts = []
            prompt_template = DEFAULT_PROMPT_FORMAT
            if self.config.dataset_config.get("formatting_prompts_format"):
                prompt_template = self.config.dataset_config[
                    "formatting_prompts_format"]

            for i in range(len(example['prompt'])):
                text = prompt_template.format(
                    prompt=example['prompt'][i],
                    completion=example['prompt'][i]
                )
                output_texts.append(text)
            return output_texts

        trainer = TRL_SFTTrainer(
            base_model,
            train_dataset=dataset,
            tokenizer=tokenizer,
            max_seq_length=2048,
            formatting_func=formatting_prompts_func,
            args=training_args
        )

        trainer.train()
        trainer.save_model(output_dir)

        output_dir = os.path.join(output_dir, "final_checkpoint")
        trainer.model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        return TrainerOutput(train_logs=[])


BaseTrainer.register_trainer("sft_trainer", SFTTrainer, SFTTrainerConfig)