from typing import cast

from omegaconf import OmegaConf
from omegaconf.listconfig import ListConfig

from ..schemas.experiment_config import ExperimentConfig


def load_and_validate_config(config_filepath: str) -> ExperimentConfig:
    """
    Load and validate the experiment configuration directly from a specified filepath.
    """

    # Load the configuration directly from the specified filepath
    dict_config = OmegaConf.load(config_filepath)

    # Convert the DictConfig to ExperimentConfig and cast it
    config = cast(ExperimentConfig, OmegaConf.to_object(dict_config))

    return config


def load_and_validate_configs(config_filepath: str) -> list[ExperimentConfig]:
    dict_configs = OmegaConf.load(config_filepath)
    if isinstance(dict_configs, ListConfig):
        configs = [
            cast(ExperimentConfig, OmegaConf.to_object(dc))
            for dc in dict_configs
        ]
    else:
        configs = [cast(ExperimentConfig, OmegaConf.to_object(dict_configs))]

    return configs
