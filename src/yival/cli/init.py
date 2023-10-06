from argparse import Namespace

from yival.wrappers.string_wrapper import StringWrapper

from ..combination_improvers.openai_prompt_based_combination_improver import (
    OpenAIPromptBasedCombinationImprover,
)
from ..combination_improvers.optimize_by_prompt_improver import OptimizeByPromptImprover
from ..data.csv_reader import CSVReader
from ..data_generators.openai_prompt_data_generator import OpenAIPromptBasedGeneratorConfig
from ..evaluators.bertscore_evaluator import BertScoreEvaluator
from ..evaluators.openai_elo_evaluator import OpenAIEloEvaluator
from ..evaluators.openai_prompt_based_evaluator import OpenAIPromptBasedEvaluator
from ..evaluators.rouge_evaluator import RougeEvaluator
from ..evaluators.string_expected_result_evaluator import StringExpectedResultEvaluator
from ..result_selectors.ahp_selection import AHPSelection
from ..schemas.experiment_config import WrapperConfig, WrapperVariation
from ..variation_generators.openai_prompt_based_variation_generator import (
    OpenAIPromptBasedVariationGenerator,
)
from .utils import generate_experiment_config_yaml

try:
    from ..finetune.sft_trainer import SFTTrainer
except ImportError:
    # isort: skip
    from ..finetune.back_up_trainer import BackUpTrainer as SFTTrainer  # type: ignore
    print(
        """[Warn] missing modules while import SFTTrainer, ignore this warn if you don't want to finetune model in yival\n 
            solve this by 'pip install yival[trainers]' """
    )


def _prevent_unused_imports():

    #tools
    _ = StringWrapper
    _ = CSVReader

    #DataGenerator
    _ = OpenAIPromptBasedGeneratorConfig
    _ = OpenAIPromptBasedVariationGenerator

    #Evaluator
    _ = StringExpectedResultEvaluator
    _ = RougeEvaluator
    _ = BertScoreEvaluator
    _ = OpenAIEloEvaluator
    _ = OpenAIPromptBasedEvaluator

    #Improver
    _ = OpenAIPromptBasedCombinationImprover
    _ = OptimizeByPromptImprover

    #Strategy
    _ = AHPSelection

    #Trainer
    _ = SFTTrainer


def variation_type(arg: str):
    """Parse variations for experiment configuration."""
    try:
        parts = arg.split(';')

        key, rest = parts[0].split('=')
        value_type, values_str = rest.split(':')
        values = values_str.split(',')
        variations = [
            WrapperVariation(value_type=value_type, value=value)
            for value in values
        ]

        generator_name = None
        for part in parts[1:]:
            if "generator_name" in part:
                _, generator_name = part.split('=')

        return {
            "name": key,
            "variations": variations,
            "generator_name": generator_name
        }
    except ValueError as exc:
        raise ValueError(
            "Invalid format for variation: {}.\n"
            "Expected format: key=value_type:value1,value2,...;\n"
            "generator_name=gen_name".format(arg)
        ) from exc


def add_arguments_to(subparser):
    """Define the arguments for the 'init' subcommand."""
    parser = subparser.add_parser(
        "init", help="Initialize an experiment configuration template."
    )
    parser.description = (
        "Generate a configuration template for AI "
        "experiments based on provided parameters."
    )
    parser.set_defaults(func=init)

    # Basic configuration arguments
    parser.add_argument(
        "--config_path",
        type=str,
        help="Path to save the generated configuration template."
    )
    parser.add_argument(
        "--source_type",
        type=str,
        default="dataset",
        choices=["dataset", "machine_generated", "user"],
        help=(
            "Source type for the experiment. Options: "
            "'dataset', 'machine_generated', or 'user'."
        )
    )

    # Component-specific arguments
    parser.add_argument(
        "--evaluator_names",
        type=str,
        nargs='+',
        help="List of evaluator names for the config."
    )
    parser.add_argument(
        "--reader_name",
        type=str,
        help="Name of the data reader for the config."
    )
    parser.add_argument(
        "--improver_name",
        type=str,
        help="Name of the improver for the config."
    )
    parser.add_argument(
        "--function",
        type=str,
        help="Function (module_name.function_name) to run the experiment."
    )
    parser.add_argument(
        "--data_genertaor_names",
        type=str,
        nargs='+',
        help="List of data generator names for the config."
    )
    parser.add_argument(
        "--wrapper_names",
        type=str,
        nargs='+',
        help="List of wrapper names for the config."
    )

    parser.add_argument(
        "--variations",
        type=variation_type,
        nargs='+',
        help=(
            "Variations in 'key=value_type:value1,value2,...' format."
            "To include a generator, append ';generator_name=gen_name"
        )
    )
    parser.add_argument(
        "--custom_reader",
        type=str,
        help=(
            "Specify custom reader in "
            "'name:class_path:config_cls_path' format."
        )
    )
    parser.add_argument(
        "--custom_improver",
        type=str,
        help=
        "Specify custom improver in 'name:class_path:config_cls_path' format."
    )
    parser.add_argument(
        "--selection_strategy",
        type=str,
        help="Specify selection strategy name"
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
    parser.add_argument(
        "--custom_data_generators",
        type=str,
        nargs='+',
        help=
        "Specify custom data generators in 'name:class_path:config_cls_path' format."
    )
    parser.add_argument(
        "--custom_variation_generators",
        type=str,
        nargs='+',
        help=(
            "Specify custom variation generators in "
            "'name:class_path:config_cls_path' format."
        )
    )
    parser.add_argument(
        "--custom_selection_strategy",
        type=str,
        help=(
            "Specify custom selection strategies in "
            "'name:class_path:config_cls_path' format."
        )
    )


def init(args: Namespace):
    """Generate and save an experiment configuration template."""
    wrapper_config_objects = []
    if args.variations:
        for wc_dict in args.variations:
            name = wc_dict["name"]
            variations = wc_dict["variations"]
            generator_name = wc_dict.get(
                "generator_name"
            )  # This will be None if not provided

            wrapper_config_objects.append(
                WrapperConfig(
                    name=name,
                    variations=variations,
                    generator_name=generator_name
                )
            )

    custom_reader = {}
    if args.custom_reader:
        reader_name, reader_class_path, reader_config_cls_path = (
            args.custom_reader.split(":")
        )
        custom_reader[reader_name] = {
            "class_path": reader_class_path,
            "config_path": reader_config_cls_path
        }
    custom_improver = {}
    if args.custom_improver:
        improver_name, improver_class_path, improver_config_cls_path = (
            args.custom_improver.split(":")
        )
        custom_improver[improver_name] = {
            "class_path": improver_class_path,
            "config_path": improver_config_cls_path
        }
    custom_wrappers = {}
    if args.custom_wrappers:
        for custom_wrapper in args.custom_wrappers:
            wrapper_name, wrapper_class_path, wrapper_config_cls_path = (
                custom_wrapper.split(":")
            )
            custom_wrappers[wrapper_name] = {
                "class_path": wrapper_class_path,
                "config_path": wrapper_config_cls_path
            }
    custom_evaluators = {}
    if args.custom_evaluators:
        for custom_evaluator in args.custom_evaluators:
            evaluator_name, evaluator_class_path, evaluator_config_cls_path = (
                custom_evaluator.split(":")
            )
            custom_evaluators[evaluator_name] = {
                "class_path": evaluator_class_path,
                "config_path": evaluator_config_cls_path
            }
    custom_data_generators = {}
    if args.custom_data_generators:
        for custom_data_generator in args.custom_data_generators:
            data_generator_name, data_generator_class_path, data_generator_config_cls_path = (
                custom_data_generator.split(":")
            )
            custom_data_generators[data_generator_name] = {
                "class_path": data_generator_class_path,
                "config_path": data_generator_config_cls_path
            }
    custom_variation_generators = {}
    if args.custom_variation_generators:
        for custom_variation_generator in args.custom_variation_generators:
            variation_generator_name, variation_generator_class_path, variation_generator_config_cls_path = (
                custom_variation_generator.split(":")
            )
            custom_variation_generators[variation_generator_name] = {
                "class_path": variation_generator_class_path,
                "config_path": variation_generator_config_cls_path
            }

    custom_selection_strategy = {}
    if args.custom_selection_strategy:
        strategy_name, strategy_class_path, strategy_config_cls_path = (
            args.custom_selection_strategy.split(":")
        )
        custom_selection_strategy[strategy_name] = {
            "class_path": strategy_class_path,
            "config_path": strategy_config_cls_path
        }

    # Generate the configuration template dynamically
    yaml_template = generate_experiment_config_yaml(
        custom_function=args.function,
        source_type=args.source_type,
        evaluator_names=args.evaluator_names,
        reader_name=args.reader_name,
        improver_name=args.improver_name,
        wrapper_names=args.wrapper_names,
        data_generator_names=args.data_genertaor_names,
        selection_strategy_name=args.selection_strategy,
        wrapper_configs=wrapper_config_objects,
        custom_reader=custom_reader,
        custom_wrappers=custom_wrappers,
        custom_evaluators=custom_evaluators,
        custom_data_generators=custom_data_generators,
        custom_variation_generators=custom_variation_generators,
        custom_selection_strategy=custom_selection_strategy,
        custom_improver=custom_improver
    )

    # Save the generated template to the specified config path
    with open(args.config_path, 'w') as f:
        f.write(yaml_template)

    print(f"Configuration template generated and saved to {args.config_path}")
    print("Please configure the YAML file according to your experiment needs.")
