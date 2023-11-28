---
sidebar_position: 2
---
# Installation

## Prerequisites

- **Python Version**: Ensure that `Python 3.10` or later is installed. We suggest using a Python version manager such as PyEnv, Virtualenv, and Anaconda, if needed.
- **OpenAI API Key**: Obtain an API key from OpenAI. Once you have the key, set it as an environment variable named `OPENAI_API_KEY`.

## Installation Methods

### Using pip (Recommended)

You can install the `yival` package directly using pip:

```Python
pip install yival
```

### Using Poetry

If you're interested in contributing or configuring a development environment, Poetry is the recommended choice. Below are the step-by-step instructions to help you get started:

1. **Install Poetry**: If you haven't already, [install Poetry](https://python-poetry.org/docs/#installation).

2. **Clone the Repository**:

```Python
git clone https://github.com/YiVal/YiVal.git
cd YiVal
```

3. **Setup with Poetry**: Initialize the Python virtual environment and install dependencies using Poetry:

```Plaintext
poetry install --sync
```

## Create Your First YiVal Program

Once the setup is complete, you can swiftly begin your journey with YiVal by creating datasets containing randomly generated tech startup business names following the instructions below. You can find a step-by-step guide below to begin creating your first YiVal program:

1. **Navigate to the** **`yival`** **Directory**:

```Shell
cd /YiVal/src/yival
```

2. **Set OpenAI API Key**: Replace `$YOUR_OPENAI_API_KEY` with your actual OpenAI API key.

```Shell
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

3. **Define YiVal Configuration**: Create a configuration file named `config_data_generation.yml` for automated test dataset generation with the following content:

```YAML
description: Generate test data
dataset:
    data_generators:
    openai_prompt_data_generator:
        chunk_size: 100000
        diversify: true
        model_name: gpt-4
        input_function:
            description: # Description of the function
            Given a tech startup business, generate a corresponding landing page headline
            name: headline_generation_for_business
            parameters:
                tech_startup_business: str # Parameter name and type
        number_of_examples: 3
        output_csv_path: generated_examples.csv
    source_type: machine_generated
```

4. **Execute YiVal**: Run the following command from within the `/YiVal/src/yival` directory:

```Plaintext
yival run config_data_generation.yml
```

5. **Check the Generated Dataset**: The generated test dataset will be stored in `generated_examples.csv`.
