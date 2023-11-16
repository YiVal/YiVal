'''
This file contains the default task and context information for the autogen task demo
'''


class InputValues:

    def __init__(self, task, context_info, evaluation_aspects):
        self.task = task
        self.context_info = context_info
        self.evaluation_aspects = evaluation_aspects


input_values1 = InputValues('task 1', 'context info 1', 'evaluation aspects 1')
input_values2 = InputValues('task 2', 'context info 2', 'evaluation aspects 2')
input_values3 = InputValues('task 3', 'context info 3', 'evaluation aspects 3')


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
            return InputValues('', '', '')
