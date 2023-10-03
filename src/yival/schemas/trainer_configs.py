from dataclasses import dataclass, field
from typing import List, Optional

from attr import asdict


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
    target_modules: List[str] = field(
        default_factory=lambda: ["q_proj", "v_proj"]
    )
    bias = "none"
    task_type: str = "CAUSAL_LM"
    lora_dropout: float = 0.05
    inference_mode: bool = False


@dataclass
class BnbConfig:
    load_in_4_bit: bool = False
    load_in_8_bit: bool = False


@dataclass
class SFTTrainerConfig:
    """
    Supervised Fine-tuning trainer config
    """
    model_name: str
    output_path: str
    enable_bits_and_bytes: bool = False
    bnb_config: Optional[BnbConfig] = None
    enable_lora: bool = False
    lora_config: Optional[LoRAConfig] = None