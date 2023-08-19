from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Type

from ..schemas.experiment_config import WrapperVariation
from ..schemas.varation_generator_configs import BaseVariationGeneratorConfig


class BaseVariationGenerator(ABC):
    """
    Abstract base class for all variation variation.
    """
    _registry: Dict[str, Dict[str, Any]] = {}
    default_config: Optional[BaseVariationGeneratorConfig] = None

    @classmethod
    def get_variation_generator(
        cls, name: str
    ) -> Optional[Type['BaseVariationGenerator']]:
        """Retrieve variation generator class from registry by its name."""
        generator_info = cls._registry.get(name, {})
        return generator_info.get(
            "class", None
        ) if "class" in generator_info else None

    @classmethod
    def get_default_config(
        cls, name: str
    ) -> Optional[BaseVariationGeneratorConfig]:
        """Retrieve the default configuration of a variation generator by its name."""
        generator_info = cls._registry.get(name, {})
        return generator_info.get(
            "default_config", None
        ) if "default_config" in generator_info else None

    def __init__(self, config: BaseVariationGeneratorConfig):
        self.config = config

    @classmethod
    def get_config_class(
        cls, name: str
    ) -> Optional[Type[BaseVariationGeneratorConfig]]:
        """Retrieve the configuration class of a generator_info by its name."""
        generator_info = cls._registry.get(name, {})
        return generator_info.get("config_cls", None)

    @classmethod
    def register_variation_generator(
        cls,
        name: str,
        variation_generator_cls: Type['BaseVariationGenerator'],
        config_cls: Optional[Type[BaseVariationGeneratorConfig]] = None
    ):
        cls._registry[name] = {
            "class": variation_generator_cls,
            "default_config": variation_generator_cls.default_config,
            "config_cls": config_cls
        }

    @abstractmethod
    def generate_variations(self) -> Iterator[List[WrapperVariation]]:
        """
        Generate a sequence of variations to be used in experiments.
        
        This method should yield lists of variations, with each list typically representing a set
        or batch of variations to be used in a single experiment or iteration.
        
        Returns:
            Iterator[List[WrapperVariation]]: An iterator yielding lists of WrapperVariation objects.
            
        Note:
            The specific logic for generating variations should be implemented by subclasses.
        """
        pass
