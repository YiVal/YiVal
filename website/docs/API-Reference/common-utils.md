---
sidebar_position: 2
---
# Common Utils

## `HFInference`

### Introduction

The `HFInference` class facilitates local inference using models from the HuggingFace transformers library. It provides utilities to load and run inference on a specified model, ensuring efficient text generation directly on the host system.

### Class Definition

#### Description

The `HFInference` class provides an interface for local inference using HuggingFace models.

#### Attributes

- **`model_name(str)`**:
    - The name or path of the HuggingFace model to be loaded.

#### Methods

- **`__init__(self, model_name: str)`**:

    - Initializes the `HFInference` instance and loads the specified model.
    - Parameters:
        - `model_name (str)`: The name or path of the HuggingFace model.
- **`load_model(self, model_name: str) -> Tuple[PreTrainedModel, PreTrainedTokenizer]`**:

    - Loads the model and corresponding tokenizer from the transformers library.
    - Parameters:
    - `model_name (str)`: The name or path of the HuggingFace model.
    - Returns:
        - A tuple containing the loaded model and its tokenizer.
- **`generate(self, prompt: str, max_length: int = 200, temperature: float = 0, top_p: float = 0.99, repetition_penalty: float = 1)`**:

    - Generates text based on the provided prompt using the loaded model.
    - Parameters:
    - `prompt (str)`: The input text or prompt for the model.
    - `max_length (int)`: Maximum length of the generated text. The default value is `200`.
    - `temperature (float)`: Sampling temperature. The default value is `0`.
    - `top_p (float)`: Nucleus sampling's top-p value. The default value is `0.99`.
    - `repetition_penalty (float)`: Repetition penalty factor. The default value is `1`.
    - Returns:
    - A generator that yields each generated token or word.

#### Notes

- The `HFInference` class incorporates a patched `greedy_search` method from the transformers library for efficient text generation.
- It is optimized to work on both CPU and GPU environments, allowing for faster inferencing when GPU support is available.
- The class dynamically detects the model architecture from the given model's configuration, ensuring compatibility with various HuggingFace model architectures.

### Example

```Python
# Assuming necessary imports are in place
# Initialize the HFInference class with a model name
hf_inference = HFInference("gpt2-medium")

# Generate text using the model
prompt_text = "Once upon a time"
generated_tokens = hf_inference.generate(prompt_text, max_length=100)

# Display the generated text
generated_text = " ".join(generated_tokens)
print(generated_text)
```

### [Source Code](https://security.larksuite.com/link/safety?target=https%3A%2F%2Fgithub.com%2FYiVal%2FYiVal%2Fblob%2Fmaster%2Fsrc%2Fyival%2Fcommon%2Fhuggingface%2Fhf.py&scene=ccm&logParams={)

## `DocSimilarityUtils`

### Introduction

This module provides utilities for obtaining embeddings of textual data using the OpenAI API and for computing the cosine similarity between two sets of embeddings.

### Class Definition

#### Description

Fetches the embedding for a given string using the OpenAI API.

#### Methods (Functions)

- **`get_embedding(input_str: str) -> list[float]`\*\***:\*\*
    - Fetches the embedding for a given string using the OpenAI API.
    - Parameters:
        - **`input_str (str)`**: The input text for which the embedding is to be obtained.
    - Returns:
        - **`list[float]`**: A list of floats representing the embedding of the input text.
- **`cosine_similarity(a: list[float], b: list[float]) -> float`**:
    - Computes the cosine similarity between two sets of embeddings.
    - Parameters:
        - **`a (list[float])`**: The first set of embeddings.
        - **`b (list[float])`**: The second set of embeddings.
    - Returns:
        - **`float`**: A float value representing the cosine similarity between the two sets of embeddings.
- **`get_cosine_simarity(doc1: str, doc2: str) -> float`\*\***:\*\*
    - Computes the cosine similarity between the embeddings of two textual documents.
    - Parameters:
        - **`doc1 (str)`**: The first document text.
        - **`doc2 (str)`**: The second document text.
    - Returns:
        - **`float`**: A float value representing the cosine similarity between the embeddings of the two documents.

#### Notes

- Ensure that you have properly set up and authenticated your OpenAI API before using these utilities.
- The cosine similarity function is a general-purpose function and can be used to compute the similarity between any two sets of embeddings, not just textual embeddings.

### Example

```Python
# get_embedding example
embedding = get_embedding("Hello, world!")
print(embedding)
```

```Python
# cosine_similarity example
embedding1 = [0.2, 0.5, 0.8]
embedding2 = [0.1, 0.6, 0.9]
similarity = cosine_similarity(embedding1, embedding2)
print(similarity)
```

```Python
# get_cosine_similarity example
document1 = "The sun shines brightly."
document2 = "It's a bright and sunny day."
similarity = get_cosine_similarity(document1, document2)
print(similarity)
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/common/doc_similarity_utils.py)

## `Utils`

### Introduction

This module provides common utility functions designed primarily for asynchronous interactions with OpenAI's API, managing rate limits, and obtaining embeddings.

### Class Definition

#### `RateLimiter`

##### Description

 The `RateLimiter` class ensures that the rate of requests and token usage do not exceed specified limits.

##### Attributes

- `max_rate (int)`: Maximum number of requests allowed per second.
- `max_tokens_per_minute (int)`: Maximum number of tokens allowed to be used per minute.
- `start_time (float)`: Time when the rate limiter was initialized.
- `request_count (int)`: Number of requests made since initialization.
- `token_usage (deque)`: A deque containing tuples of tokens used and the time they were used.

##### Example

```Python
import asyncio

# Create an instance of RateLimiter with specified limits
rate_limiter = RateLimiter(max_rate=5, max_tokens_per_minute=1000)

# A mock function that simulates API request and uses rate limiter
async def mock_api_request():
    await rate_limiter.wait()  # Wait for the rate limiter
    # Add tokens to the rate limiter (simulating token usage)
    rate_limiter.add_tokens(50)
    print("API request made!")

# Simulate multiple API requests using asyncio
async def main():
    tasks = [mock_api_request() for _ in range(10)]
    await asyncio.gather(*tasks)
asyncio.run(main())
```

### Function Definition

#### `parallel_completions(message_batches, model, max_tokens,temperature=1.3, presence_penalty=0, pbar=None, logit_bias=None) -> list`

##### Description

 Asynchronously performs parallel completions using OpenAI's API.

##### Parameters

- `message_batches (list)`: A list containing batches of messages for completion.
- `model (str)`: Model to be used for completion.
- `max_tokens (int)`: Maximum tokens to be used for completion.
- `temperature (float, optional)`: Sampling temperature. The default value is `1.3`.
- `presence_penalty (float, optional)`: Presence penalty. The default value is `0`.
- `pbar (optional)`: A progress bar instance. The default value is `None`.
- `logit_bias (optional)`: Bias for the logit. The default value is `None`.

##### Example

```Python
import asyncio

# Define the message batches for completion
message_batches = [
    [{"role": "user", "content": "tell me a joke"}],
    [{"role": "user", "content": "what's the weather like?"}],
    [{"role": "user", "content": "how are you?"}],
]

# Use the parallel_completions function to get completions
async def main():
    responses = await parallel_completions(
        message_batches=message_batches,
        model="gpt-3.5-turbo",
        max_tokens=50
    )

    for response in responses:
        print(response['choices'][0]['message']['content'])

asyncio.run(main())
```

### [Source Code](https://github.com/YiVal/YiVal/blob/master/src/yival/common/utils.py)
