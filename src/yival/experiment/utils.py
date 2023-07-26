from importlib import import_module
from typing import Any, Dict

from ..data.base_reader import BaseReader
from ..evaluators.base_evaluator import BaseEvaluator
from ..schemas.reader_configs import CSVReaderConfig


def register_custom_readers(custom_readers: Dict[str, Dict[str, Any]]):
    for name, details in custom_readers.items():
        reader_cls_path = details["class"]
        module_name, class_name = reader_cls_path.rsplit(".", 1)
        reader_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseReader.register_reader(name, reader_cls, config_cls)
    from ..data.csv_reader import CSVReader
    _ = CSVReader(CSVReaderConfig())


def register_custom_evaluators(custom_evaulators: Dict[str, Dict[str, Any]]):
    for name, details in custom_evaulators.items():
        evaluator_cls_path = details["class"]
        module_name, class_name = evaluator_cls_path.rsplit(".", 1)
        evaluator_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseEvaluator.register_evaluator(name, evaluator_cls, config_cls)


def register_custom_wrappers(custom_wrappers: Dict[str, Dict[str, Any]]):
    for name, details in custom_wrappers.items():
        wrapper_cls_path = details["class"]
        module_name, class_name = wrapper_cls_path.rsplit(".", 1)
        wrapper_cls = getattr(import_module(module_name), class_name)

        config_cls = None
        if "config_cls" in details:
            config_cls_path = details["config_cls"]
            module_name, class_name = config_cls_path.rsplit(".", 1)
            config_cls = getattr(import_module(module_name), class_name)

        BaseEvaluator.register_evaluator(name, wrapper_cls, config_cls)
