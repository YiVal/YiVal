from .config_utils import load_and_validate_config

# Sample configuration for mocking
sample_config_content = """
description: "Test experiment"
wrappers:
  - name: "wrapper1"
    variations: ["var1", "var2"]
dataset:
    input_type: "DATASET"
    file_path: "some_path.csv"
evaluator:
    evaluator_type: "individual"
output:
    path: "output_path"
    formatter: "__main__:sample_formatter_function"
"""


def test_load_and_validate_config(tmpdir):
    # Write the sample configuration to a temporary file
    config_file = tmpdir.join("sample_config.yaml")
    config_file.write(sample_config_content)

    # Load and validate the configuration using the function
    config = load_and_validate_config(config_filepath=str(config_file))

    # Assertions to verify that the configuration is loaded and parsed correctly
    assert config["description"] == "Test experiment"
    assert config["wrappers"][0]["name"] == "wrapper1"
    assert config["dataset"]["input_type"] == "DATASET"
    assert config["dataset"]["file_path"] == "some_path.csv"
    assert config["evaluator"]["evaluator_type"] == "individual"
    # Note: The callable check for the formatter will be more complex and might need adjustment
    assert config["output"]["formatter"
                            ] == "__main__:sample_formatter_function"
