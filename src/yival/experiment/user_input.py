from typing import Any, Dict, List

import npyscreen  # type: ignore

from ..logger.token_logger import TokenLogger
from ..schemas.experiment_config import ExperimentConfig, InputData
from ..states.experiment_state import ExperimentState
from .evaluator import Evaluator
from .utils import generate_experiment, get_function_args, run_single_input


class CustomTheme(npyscreen.ThemeManager):
    default_colors = {
        'DEFAULT': 'WHITE_BLACK',
        'FORMCOLOR': 'WHITE_BLACK',
        'NO_EDIT': 'BLUE_BLACK',
        'STANDOUT': 'CYAN_BLACK',
        'CURSOR': 'WHITE_BLACK',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL': 'GREEN_BLACK',
        'LABELBOLD': 'WHITE_BLACK',
        'CONTROL': 'YELLOW_BLACK',
        'IMPORTANT': 'YELLOW_BLACK',
        'SAFE': 'GREEN_BLACK',
        'WARNING': 'RED_BLACK',
        'DANGER': 'RED_BLACK',
        'CRITICAL': 'BLACK_RED',
        'GOOD': 'GREEN_BLACK',
        'GOODHL': 'GREEN_BLACK',
        'VERYGOOD': 'BLUE_BLACK',
        'CAUTION': 'YELLOW_BLACK',
        'QUESTION': 'CYAN_BLACK',
    }


class ResultDisplay(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit


class CombinationAggregatedMetricsForm(npyscreen.ActionForm):

    def create(self):
        terminal_height, _ = self._max_physical()
        result_display_height = max(5, terminal_height - 10)
        self.nextrely += 1
        self.results_display = self.add(
            ResultDisplay,
            name="Combination Aggregated Metrics",
            max_height=result_display_height
        )
        self.nextrely += 1
        self.add(
            npyscreen.ButtonPress,
            name="Back to Groups",
            when_pressed_function=self.switch_to_groups,
            color='CONTROL'
        )
        self.add(
            npyscreen.ButtonPress,
            name="Export to JSON",
            when_pressed_function=self.export_to_json,
            color='CONTROL'
        )

        # Populate results_display with metrics from all combos
        metrics_text = ""
        if self.parentApp.metrics_data:
            for combo_metrics in self.parentApp.metrics_data.combination_aggregated_metrics:
                metrics_text += f"\n\n=========================== Combo Key: {combo_metrics.combo_key} ===========================sn\n"
                for key, metrics in combo_metrics.aggregated_metrics.items():
                    metrics_text += f"{key}: {', '.join([str(m) for m in metrics])}\n"
                metrics_text += f"Average Token Usage: {combo_metrics.average_token_usage}\n"
                metrics_text += f"Average Latency: {combo_metrics.average_latency}\n"
            self.results_display.value = metrics_text

    def beforeEditing(
        self
    ):  # This method is called just before the form becomes active
        self.populate_metrics()

    def populate_metrics(self):
        # Populate results_display with metrics from all combos
        metrics_text = ""
        if self.parentApp.metrics_data:
            for combo_metrics in self.parentApp.metrics_data.combination_aggregated_metrics:
                metrics_text += f"\n\n=========================== Combo Key: {combo_metrics.combo_key} ===========================\n"
                for key, metrics in combo_metrics.aggregated_metrics.items():
                    metrics_text += f"{key}: {', '.join([str(m) for m in metrics])}\n"
                metrics_text += f"Average Token Usage: {combo_metrics.average_token_usage}\n"
                metrics_text += f"Average Latency: {combo_metrics.average_latency}\n"
            self.results_display.value = metrics_text
            self.results_display.display()  # Refresh the display

    def switch_to_groups(self):
        # If there's a remembered last form, switch to it
        if self.parentApp.last_form:
            self.parentApp.switchForm(self.parentApp.last_form)

        else:
            # Default behavior: switch to the first group form
            first_group_form_name = self.parentApp.experiment_data.group_experiment_results[
                0].group_key
            self.parentApp.switchForm(first_group_form_name)

    def export_to_json(self):
        # Export the metrics data to a JSON file
        import json
        with open("experiment_results.json", "w") as file:
            json.dump(self.parentApp.metrics_data.asdict(), file)


class ExperimentInputForm(npyscreen.ActionForm):

    def __init__(
        self,
        *args,
        config: ExperimentConfig,
        all_combinations: List[Dict[str, Any]],
        custom_function=None,
        state: ExperimentState,
        logger: TokenLogger,
        evaluator: Evaluator,
        **kwargs
    ):
        self.config = config
        self.state = state
        self.logger = logger
        self.evaluator = evaluator
        self.all_combinations = all_combinations
        super().__init__(*args, **kwargs)

    def create(self):
        self.fields = {}
        self.add(npyscreen.TitleText, name="Example ID (Optional):")

        args = get_function_args(self.config["custom_function"]
                                 ) if self.config["custom_function"] else {}
        for arg_name, arg_type in args.items():
            self.fields[arg_name] = self.add(
                npyscreen.TitleText, name=f"{arg_name} ({arg_type}):"
            )
        self.add(npyscreen.TitleText, name="Expected Result (Optional):")
        self.add(
            npyscreen.ButtonPress,
            name="Submit",
            when_pressed_function=self.on_submit
        )

    def on_submit(self):
        example_id = self.fields.get("Example ID (Optional):", None)
        if example_id:
            example_id = example_id.value or None
        content = {}
        for arg_name, widget in self.fields.items():
            content[arg_name] = widget.value
        expected_result = self.fields.get("Expected Result (Optional):", None)
        if expected_result:
            expected_result = expected_result.value or None
        input_data = InputData(
            example_id=example_id,
            content=content,
            expected_result=expected_result
        )
        results = run_single_input(
            input_data,
            self.config,
            all_combinations=self.all_combinations,
            state=self.state,
            logger=self.logger,
            evaluator=self.evaluator
        )
        self.parentApp.experiment_data[-1].extend(results)
        self.clear_form()
        self.parentApp.switchForm("GroupExperimentResultsForm")
        self.parentApp.getForm(
            "GroupExperimentResultsForm"
        ).current_index = len(self.parentApp.experiment_data) - 1
        self.parentApp.getForm("GroupExperimentResultsForm").display_results()

    def clear_form(self):
        # Clear the fields
        for widget in self.fields.values():
            widget.value = ''
        self.display()

    def finish_and_show_metrics(self):
        # Switch to CombinationAggregatedMetricsForm
        self.parentApp.switchForm("CombinationAggregatedMetricsForm")


class GroupExperimentResultsForm(npyscreen.ActionForm):

    def create(self):
        terminal_height, _ = self._max_physical()
        result_display_height = max(5, terminal_height - 10)

        self.add_widget(
            npyscreen.TitleText,
            name="Input Data:",
            value=self.name,
            color='LABEL'
        )
        self.nextrely += 1
        self.results_display = self.add(
            ResultDisplay,
            name="Group Experiment Results",
            max_height=result_display_height
        )
        self.nextrely += 1
        self.add(
            npyscreen.ButtonPress,
            name="Next Group",
            when_pressed_function=self.when_next_pressed,
            color='CONTROL'
        )
        self.add(
            npyscreen.ButtonPress,
            name="Previous Group",
            when_pressed_function=self.when_back_pressed,
            color='CONTROL'
        )
        self.add(
            npyscreen.ButtonPress,
            name="Go to Metrics",
            when_pressed_function=self.switch_to_metrics,
            color='CONTROL'
        )
        self.add(
            npyscreen.ButtonPress,
            name="Add More Examples",
            when_pressed_function=self.add_more_examples,
            color='CONTROL'
        )
        self.current_index = 0 if len(
            self.parentApp.experiment_data
        ) == 1 else -1
        self.display_results()

    def display_results(self):
        current_results = self.parentApp.experiment_data[self.current_index]
        results_text = ""
        for item in current_results:
            results_text += f"=========================== Combination: {item.combination} ===========================\n"
            results_text += f"Raw Output:        {item.raw_output}\n"
            results_text += f"Expected Result:   {item.input_data.expected_result}\n"
            results_text += f"Latency:           {item.latency}\n"
            results_text += f"Evaluator Output:  {item.evaluator_outputs}\n"
            results_text += f"Token Usage:       {item.token_usage}\n\n"

        self.results_display.value = results_text
        self.results_display.display()

    def beforeEditing(self):
        self.display_results()

    def when_next_pressed(self):
        if self.current_index < len(self.parentApp.experiment_data) - 1:
            self.current_index += 1
        self.display_results()

    def when_back_pressed(self):
        if self.current_index > 0:
            self.current_index -= 1
        self.display_results()

    def add_more_examples(self):
        self.parentApp.experiment_data.append([])
        self.parentApp.switchForm("ExperimentInputForm")

    def switch_to_metrics(self):
        all_results = [
            result for sublist in self.parentApp.experiment_data
            for result in sublist
        ]
        experiment = generate_experiment(all_results, self.parentApp.evaluator)

        self.parentApp.metrics_data = experiment
        self.parentApp.switchForm("CombinationAggregatedMetricsForm")


class ExperimentInputApp(npyscreen.NPSAppManaged):

    def __init__(self, config, combinations, state, logger, evaluator):
        super().__init__()
        self.config = config
        self.combinations = combinations
        self.state = state
        self.logger = logger
        self.evaluator = evaluator
        self.metrics_data = None
        self.experiment_data = [[]]
        self.NEXT_ACTIVE_FORM = "ExperimentInputForm"
        self.last_form = None

    def onStart(self):
        npyscreen.setTheme(CustomTheme)
        self.addForm(
            "ExperimentInputForm",
            ExperimentInputForm,
            name="Input Form",
            config=self.config,
            all_combinations=self.combinations,
            state=self.state,
            logger=self.logger,
            evaluator=self.evaluator
        )

        self.addForm(
            "GroupExperimentResultsForm",
            GroupExperimentResultsForm,
            name="Group Experiment Results"
        )
        self.addForm(
            "CombinationAggregatedMetricsForm",
            CombinationAggregatedMetricsForm,
            name="Combination Metrics"
        )

    def switchForm(self, form_name):
        self.last_form = self.ACTIVE_FORM_NAME
        super().switchForm(form_name)
