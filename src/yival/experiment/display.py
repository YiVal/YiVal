import random

import npyscreen  # type: ignore

from ..schemas.common_structures import InputData
from ..schemas.evaluator_config import (
    EvaluatorOutput,
    MethodCalculationMethod,
    MetricCalculatorConfig,
)
from ..schemas.experiment_config import (
    CombinationAggregatedMetrics,
    Experiment,
    ExperimentResult,
    GroupedExperimentResult,
    HumanRating,
    Metric,
)


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

    def when_next_pressed(self):
        # Get list of form names and find the next group form
        forms = list(self.parentApp._Forms)
        current_idx = forms.index(self.name)
        next_form = forms[(current_idx + 1) % len(forms)]
        while "Combo" in next_form:  # Make sure it's a group form
            current_idx += 1
            next_form = forms[current_idx % len(forms)]
        self.parentApp.switchForm(next_form)

    def when_back_pressed(self):
        # Get list of form names and find the previous group form
        forms = list(self.parentApp._Forms)
        current_idx = forms.index(self.name)
        prev_form = forms[(current_idx - 1) % len(forms)]
        while "Combo" in prev_form:  # Make sure it's a group form
            current_idx -= 1
            prev_form = forms[current_idx % len(forms)]
        self.parentApp.switchForm(prev_form)

    def switch_to_metrics(self):
        # Directly switch to the CombinationAggregatedMetricsForm
        self.parentApp.switchForm("CombinationAggregatedMetrics")


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

        # Populate results_display with metrics from all combos
        metrics_text = ""
        for combo_metrics in self.parentApp.experiment_data.combination_aggregated_metrics:
            metrics_text += f"\n\n=========================== Combo Key: {combo_metrics.combo_key} ===========================sn\n"
            for key, metrics in combo_metrics.aggregated_metrics.items():
                metrics_text += f"{key}: {', '.join([str(m) for m in metrics])}\n"
            metrics_text += f"Average Token Usage: {combo_metrics.average_token_usage}\n"
            metrics_text += f"Average Latency: {combo_metrics.average_latency}\n"
        self.results_display.value = metrics_text

    def switch_to_groups(self):
        # If there's a remembered last form, switch to it
        if self.parentApp.last_form:
            self.parentApp.switchForm(self.parentApp.last_form)

        else:
            # Default behavior: switch to the first group form
            first_group_form_name = self.parentApp.experiment_data.group_experiment_results[
                0].group_key
            self.parentApp.switchForm(first_group_form_name)


class ResultsApp(npyscreen.NPSAppManaged):

    def __init__(self, experiment_data):
        super().__init__()
        self.experiment_data = experiment_data
        self.last_form = None

    def onStart(self):
        npyscreen.setTheme(CustomTheme)
        # Add Group Experiment Results Form
        for group_result in self.experiment_data.group_experiment_results:
            form_name = group_result.group_key
            form = self.addForm(
                f_id=form_name,
                name=form_name,
                FormClass=GroupExperimentResultsForm
            )
            results_text = ""
            for item in group_result.experiment_results:
                results_text += f"=========================== Combination: {item.combination} ===========================\n"
                results_text += f"Raw Output:  {item.raw_output}\n"
                results_text += f"Expected result:  {item.input_data.expected_result}\n"
                results_text += f"Latency:     {item.latency}\n"
                results_text += f"Evaluator Output:  {item.evaluator_outputs}\n"
                results_text += f"Token Usage: {item.token_usage}\n\n"
            form.results_display.value = results_text

        # Add Combination Aggregated Metrics Form
        self.addForm(
            "CombinationAggregatedMetrics",
            CombinationAggregatedMetricsForm,
            name="Combination Metrics"
        )

        # Setting the first form dynamically based on the first group_experiment_results
        initial_form_name = self.experiment_data.group_experiment_results[
            0
        ].group_key if self.experiment_data.group_experiment_results else None
        self.setNextForm(initial_form_name)

    def get_form_name(self, form_or_name):
        if isinstance(form_or_name, str):
            return form_or_name
        for name, form in self._Forms.items():
            if form is form_or_name:
                return name
        return None

    def switchForm(self, form_name):
        # Remember the last form before switching
        self.last_form = self.ACTIVE_FORM_NAME
        super().switchForm(form_name)


def generate_random_experiment_data():
    num_examples = 5  # Number of examples per group

    def generate_experiment_result(example_id: int) -> ExperimentResult:
        return ExperimentResult(
            input_data=InputData(
                example_id=str(example_id),
                content={"text": f"Sample content {example_id}"},
            ),
            combination={
                "wrapper1": "variationA",
                "wrapper2": "variationB"
            },
            raw_output=f"Generated output for {example_id}",
            latency=random.uniform(10, 200),
            token_usage=random.randint(50, 1000),
            evaluator_outputs=[
                EvaluatorOutput(
                    name="Evaluator1",
                    result="Success",
                    metric_calculators=[
                        MetricCalculatorConfig(
                            method=MethodCalculationMethod.AVERAGE
                        )
                    ],
                )
            ],
            human_rating=HumanRating(
                aspect="Output Quality", rating=random.uniform(1, 5)
            ),
        )

    group_results = [
        GroupedExperimentResult(
            group_key=f"Group {i + 1}",
            experiment_results=[
                generate_experiment_result(j) for j in range(num_examples)
            ]
        ) for i in range(2)  # Generating data for 2 groups
    ]

    combo_metrics = [
        CombinationAggregatedMetrics(
            combo_key=f"Combo {i + 1}",
            experiment_results=[
                generate_experiment_result(j) for j in range(num_examples)
            ],
            aggregated_metrics={
                "MetricA": [
                    Metric(name=f"MetricA_{j}", value=random.uniform(0, 100))
                    for j in range(num_examples)
                ],
                "MetricB": [
                    Metric(name=f"MetricB_{j}", value=random.uniform(0, 100))
                    for j in range(num_examples)
                ],
            },
            average_token_usage=random.uniform(50, 1000),
            average_latency=random.uniform(10, 200),
        ) for i in range(2)  # Generating data for 2 combinations
    ]

    return Experiment(
        group_experiment_results=group_results,
        combination_aggregated_metrics=combo_metrics
    )


def display_results(experiment_data):
    app = ResultsApp(experiment_data)
    app.run()
