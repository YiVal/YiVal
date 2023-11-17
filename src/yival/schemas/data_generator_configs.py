from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union

from .model_configs import CallOption


@dataclass
class BaseDataGeneratorConfig:
    """
    Base configuration class for all data generators.
    """

    chunk_size: int = 1000
    number_of_examples: int = 10
    output_path: Optional[str] = None

    def asdict(self):
        return asdict(self)


@dataclass
class OpenAIPromptBasedGeneratorConfig(BaseDataGeneratorConfig):
    """
    Generate test cases from prompt. Currently only support openai models.
    """
    model_name: str = "gpt-4"
    prompt: Union[str, List[Dict[str, str]]] = """
        "Please provide a concrete and realistic test case as a dictionary for function invocation using the ** operator.
        Only include parameters, excluding description and name.
        Ensure it's succinct and well-structured.
        **Only provide the dictionary.**"    
    """
    input_function: Dict[str, Any] = field(default_factory=dict)
    # Whether to diversify the generated examples.
    diversify: bool = True
    max_token = 2000
    single_shot: bool = False

    # Expected Value name
    expected_param_name: str = ""

    # Llm call option
    call_option: Optional[CallOption] = None

    output_csv_path: Optional[str] = None

    fixed_input: Optional[Dict[str, Any]] = None

    def asdict(self):
        return asdict(self)


@dataclass
class DocumentDataGeneratorConfig(BaseDataGeneratorConfig):
    """
    Generate question data from documents.
    """
    max_token = 2000
    model_name: str = "gpt-4"
    prompt: str = ""
    document: str = ""

    # The source of the document. "text" for plain text in `document` field,
    # "file" for local unstructured file path in `document` field,
    # "drive" for file id in google drive.
    source: str = "text"

    # For per example, the number of questions you want in per chunk.
    num_questions_per_chunk: int = 5

    # The template you want for the generated questions
    text_question_template: Optional[str] = None
    question_gen_query: str = ""

    number_of_examples: int = 1
    document_chunk_size: int = 512
    output_csv_path: Optional[str] = None

    def asdict(self):
        return asdict(self)
