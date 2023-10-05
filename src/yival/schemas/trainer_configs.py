from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class BaseTrainerConfig:
    """
    Base configuration class for all trainers
    """
    name: str

    def asdict(self):
        return asdict(self)


@dataclass
class LoRAConfig:
    """
    LoRA config for SFT Trainer
    """
    r: int = 8
    lora_alpha: int = 32
    bias = "none"
    task_type: str = "CAUSAL_LM"
    lora_dropout: float = 0.05
    inference_mode: bool = False

    def asdict(self):
        return asdict(self)


@dataclass
class BnbConfig:
    load_in_4_bit: bool = False
    load_in_8_bit: bool = False

    def asdict(self):
        return asdict(self)


@dataclass
class DatasetConfig:
    prompt_key: str
    completioin_key: Optional[str] = None
    formatting_prompts_format: Optional[str] = None
    condition: Optional[str] = None

    def asdict(self):
        return asdict(self)


@dataclass
class TrainArguments:
    """
    Train Arguments in trl trainer
    Parameters for training arguments details => https://github.com/huggingface/transformers/blob/main/src/transformers/training_args.py#L158
    """
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    gradient_checkpointing: bool = True
    max_grad_norm: float = 0.3
    num_train_epochs: int = 15
    learning_rate: float = 0.0002
    bf16: bool = False
    save_total_limit: int = 3
    logging_steps: int = 1
    optim: str = "paged_adamw_32bit"
    lr_scheduler_type: str = "cosine"
    warmup_ratio: float = 0.05
    log_level: str = 'debug'

    def asdict(self):
        return asdict(self)


@dataclass
class SFTTrainerConfig(BaseTrainerConfig):
    """
    Supervised Fine-tuning trainer config
    """
    model_name: str
    output_path: str
    dataset_config: DatasetConfig
    enable_bits_and_bytes: bool = False
    bnb_config: Optional[BnbConfig] = None
    enable_lora: bool = False
    lora_config: Optional[LoRAConfig] = None
    train_arguments: Optional[TrainArguments] = None

    def asdict(self):
        return asdict(self)
