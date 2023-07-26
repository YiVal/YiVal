from typing import Callable, List, Optional, Tuple

from ..schemas.experiment_config import FunctionMetadata

FUNCTION_REGISTRY = {}


def register_function(
    name: str,
    description: str,
    parameters: List[Tuple[str, Optional[str]]] = []
):

    def decorator(func: Callable):
        FUNCTION_REGISTRY[name] = {
            "function": func,
            "metadata": FunctionMetadata(description, parameters)
        }
        return func

    return decorator
