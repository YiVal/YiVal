export ngrok=true
ngrok config add-authtoken 2XOI3eO1YrYKwvrT3PoqTXiPrUE_5MRXtts2wkGkTd4qzmkuK
poetry run python -m yival.experiment.app.app --experiment deploy/email_case/auto_generated_email_0.pkl --self_config deploy/deploy/config.pkl --all_combinations deploy/deploy/all_combinatioins --instance deploy/deploy/instance.pkl --logger deploy/deploy/logger.pkl --evaluator deploy/deploy/evaluator.pkl