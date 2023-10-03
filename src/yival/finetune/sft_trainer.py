"""
This module provides an implementation of Supervised Fine-tuning trainer.

"""
import os

import torch
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer as TRL_SFTTrainer

from ..experiment.evaluator import Evaluator
from ..logger.token_logger import TokenLogger
from ..schemas.experiment_config import (
    Experiment,
    ExperimentConfig,
    TrainerOutput,
)
from ..schemas.trainer_configs import SFTTrainerConfig
from .base_trainer import BaseTrainer
from .utils import (
    find_all_linear_names,
    get_hg_tokenizer,
    print_trainable_parameters,
)


class SFTTrainer(BaseTrainer):
    """
    SFT Trainer implement
    """

    def __init__(self, config: SFTTrainerConfig) -> None:
        super().__init__(config)
        self.config: SFTTrainerConfig = config

    def train(
        self, experiment: Experiment, config: ExperimentConfig,
        evaluator: Evaluator, token_logger: TokenLogger
    ) -> TrainerOutput:

        #Prepare base model and tokenizer
        model_name = self.config.model_name
        tokenizer = get_hg_tokenizer(model_name)

        #Assemble bitsandbytes quant config
        bnb_config = None
        if self.config.enable_bits_and_bytes:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=self.config.bnb_config.load_in_4_bit,
                load_in_8bit=self.config.bnb_config.load_in_8_bit
            )

        base_model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.half, quantization_config=bnb_config
        )

        peft_config = None
        if self.config.enable_lora:
            peft_config = LoraConfig(
                r=self.config.lora_config.r,
                lora_alpha=self.config.lora_config.lora_alpha,
                target_modules=find_all_linear_names(base_model),
                lora_dropout=self.config.lora_config.lora_dropout,
                task_type=self.config.lora_config.task_type,
                bias=self.config.lora_config.bias
            )
            base_model = get_peft_model(base_model, peft_config)

        print_trainable_parameters(base_model)

        # Parameters for training arguments details => https://github.com/huggingface/transformers/blob/main/src/transformers/training_args.py#L158
        training_args = TrainingArguments(
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            gradient_checkpointing=True,
            max_grad_norm=0.3,
            num_train_epochs=15,
            learning_rate=2e-4,
            bf16=True,
            save_total_limit=3,
            logging_steps=10,
            output_dir=self.config.output_path,
            optim="paged_adamw_32bit",
            lr_scheduler_type="cosine",
            warmup_ratio=0.05,
        )

        output_dir = self.config.output_path

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
