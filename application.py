import pickle

from yival.configs.config_utils import load_and_validate_configs
from yival.experiment.app.app import create_dash_app  # type: ignore
from yival.experiment.evaluator import Evaluator
from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import Experiment
from yival.states.experiment_state import ExperimentState

experiment_config = load_and_validate_configs('tt.yaml')
with open("auto_generated_tt_0.pkl", 'rb') as file:
    experiment: Experiment = pickle.load(file)


app = create_dash_app(
    experiment,
    experiment_config,
    {},
    [],
    ExperimentState(),
    TokenLogger(),
    Evaluator([]),
    False,
)

application = app.server

if __name__ == '__main__':
    # When running locally: enable debug mode for development purposes
    app.run_server(debug=True)  # Specify the port if needed