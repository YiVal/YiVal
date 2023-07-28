from argparse import ArgumentParser, ArgumentTypeError, Namespace
from mimetypes import inited

from yival.wrappers.string_wrapper import StringWrapper

from ..data.csv_reader import CSVReader
from ..evaluators.string_expected_result_evaluator import (
    StringExpectedResultEvaluator,
)
from ..schemas.experiment_config import WrapperConfig, WrapperVariation
from .utils import generate_experiment_config_yaml


def _prevent_unused_imports():
    _ = StringWrapper
    _ = StringExpectedResultEvaluator
    _ = CSVReader


def variation_type(arg: str):
    """Custom argparse type function for variations."""
    try:
        key, rest = arg.split('=')
        value_type, values_str = rest.split(':')
        values = values_str.split(',')
        variations = [
            WrapperVariation(value_type=value_type, value=value)
            for value in values
        ]
        return {key: variations}
    except ValueError:
        raise ArgumentTypeError(
            f"Invalid format for variation: {arg}. Expected format: key=value_type:value1,value2,..."
        )


def add_arguments_to(subparser):
    """Add arguments to subcommand add."""
    parser: ArgumentParser = subparser.add_parser("init", help=inited.__doc__)
    parser.description = init.__doc__
    parser.set_defaults(func=init)

    parser.add_argument(
        "--config_path",
        type=str,
        help="Path to save the configuration template."
    )
    parser.add_argument(
        "--source_type",
        type=str,
        default="dataset",
        choices=["dataset", "user"],
        help=
        "Type of source for the experiment. Choices are ['DATASET', 'USER']."
    )
    parser.add_argument(
        "--evaluator_names",
        type=str,
        nargs='+',
        help="Names of evaluators to include in the config."
    )
    parser.add_argument(
        "--reader_name",
        type=str,
        help="Name of the reader to include in the config."
    )
    parser.add_argument(
        "--function",
        type=str,
        help=
        "Function that will be used to run the experiment, module_name.function_name."
    )
    parser.add_argument(
        "--wrapper_names",
        type=str,
        nargs='+',
        help="Names of wrappers to include in the config."
    )
    parser.add_argument(
        "--variations",
        type=variation_type,
        nargs='+',
        help="Variations in 'key=value_type:value1,value2,...' format."
    )
    parser.add_argument(
        "--custom_reader",
        type=str,
        help=
        "Specify custom readers in 'name:class_path:config_cls_path' format."
    )
    parser.add_argument(
        "--custom_wrappers",
        type=str,
        nargs='+',
        help=
        "Specify custom wrappers in 'name:class_path:config_cls_path' format."
    )
    parser.add_argument(
        "--custom_evaluators",
        type=str,
        nargs='+',
        help=
        "Specify custom evaluators in 'name:class_path:config_cls_path' format."
    )


def init(args: Namespace):
    """Initialize experiment configuration template."""
    # Convert variations from a list of dictionaries to a list of WrapperConfig objects
    wrapper_config_objects = [
        WrapperConfig(
            name=list(wc_dict.keys())[0], variations=list(wc_dict.values())[0]
        ) for wc_dict in args.variations
    ]
    custom_reader = {}
    if args.custom_reader:
        reader_name, reader_class_path, reader_config_cls_path = args.custom_reader.split(
            ":"
        )
        custom_reader[reader_name] = {
            "class_path": reader_class_path,
            "config_path": reader_config_cls_path
        }
    custom_wrappers = {}
    if args.custom_wrappers:
        for custom_wrapper in args.custom_wrappers:
            wrapper_name, wrapper_class_path, wrapper_config_cls_path = custom_wrapper.split(
                ":"
            )
            custom_wrappers[wrapper_name] = {
                "class_path": wrapper_class_path,
                "config_path": wrapper_config_cls_path
            }
    custom_evaluators = {}
    if args.custom_evaluators:
        for custom_evaluator in args.custom_evaluators:
            evaluator_name, evaluator_class_path, evaluator_config_cls_path = custom_evaluator(
                ":"
            )
            custom_evaluators[evaluator_name] = {
                "class_path": evaluator_class_path,
                "config_path": evaluator_config_cls_path
            }

    # Generate the configuration template dynamically
    yaml_template = generate_experiment_config_yaml(
        custom_function=args.function,
        source_type=args.source_type,
        evaluator_names=args.evaluator_names,
        reader_name=args.reader_name,
        wrapper_names=args.wrapper_names,
        wrapper_configs=wrapper_config_objects,
        custom_reader=custom_reader,
        custom_wrappers=custom_wrappers,
        custom_evaluators=custom_evaluators
    )

    # Save the generated template to the specified config path
    with open(args.config_path, 'w') as f:
        f.write(yaml_template)

    print(f"Configuration template generated and saved to {args.config_path}")
    print("Please configure the YAML file according to your experiment needs.")
