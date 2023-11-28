'''
This file contains the default task and context information for the autogen task demo
'''


class InputValues:

    def __init__(self, task, context_info, evaluation_aspects):
        self.task = task
        self.context_info = context_info
        self.evaluation_aspects = evaluation_aspects


input_values1 = InputValues(
    'Tiktok Headline Generation Bot',
    'generate a short tiktok video title based on the {{content summary}} and {{target_audience}}',
    'emoji, oneline'
)
input_values2 = InputValues(
    'Email Auto Reply Bot',
    'generate a short automatic email reply based on the {{email_subject}} and {{user_availability}}',
    'politeness, clarity'
)
input_values3 = InputValues(
    'Fitness Plan Bot',
    'create a fitness plan based on the {{fitness_goal}} and {{current_fitness_level}}',
    'feasibility, progression'
)


class DefaultValueProvider:

    @staticmethod
    def get_default_values(button_id):
        if button_id == 'update-button-1':
            return input_values1
        elif button_id == 'update-button-2':
            return input_values2
        elif button_id == 'update-button-3':
            return input_values3
        else:
            raise ValueError(f"Invalid button_id: {button_id}")
