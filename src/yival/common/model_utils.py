from typing import Callable

from yival.common.huggingface.hf import HFInference
from yival.schemas.model_configs import ModelProvider, Request, Response

# from litellm import completion

# def _litellm_completion(
#     request: Request, provider: ModelProvider | None = None
# ) -> Response:
#     if isinstance(request.prompt, str):
#         prompt = [{"content": request.prompt, "role": "user"}]
#     else:
#         prompt = request.prompt
#     if request.params is not None:
#         params = request.params
#     else:
#         params = {}
#     if provider and provider.provider_name:
#         response = completion(
#             request.model_name,
#             messages=prompt,
#             custom_llm_provider=provider.provider_name,
#             **params
#         )
#     else:
#         response = completion(request.model_name, messages=prompt, **params)
#     return Response(output=response)


def huggerface_local_completion(request: Request) -> Response:
    hf = HFInference(request.model_name)
    if request.params is not None:
        params = request.params
    else:
        params = {}
    assert isinstance(request.prompt, str)
    output = hf.generate(prompt=request.prompt, **params)
    res = ""
    for generated_token in output:
        res += generated_token

    return Response(output=res)


model_inference_mapping: dict[str, Callable[[Request, ModelProvider | None],
                                            Response]] = {}

model_to_provider_maping: dict[str, str] = {
    "a16z-infra/llama-2-13b-chat:9dff94b1bed5af738655d4a7cbcdcde2bd503aa85c94334fe1f42af7f3dd5ee3":
    "replicate",
    "replicate/llama-2-70b-chat:2796ee9483c3fd7aa2e171d38f4ca12251a30609463dcfd4cd76703f22e96cdf":
    "replicate",
    "replicate/vicuna-13b:6282abe6a492de4145d7bb601023762212f9ddbbe78278bd6771c8b3b2f2a13b":
    "replicate"
}

# def llm_completion(
#     request: Request, provider: ModelProvider | None = None
# ) -> Response:
#     """Perform model completion based on the provided request and optional
#     model provider.

#     Parameters:
#         request (Request): The request object containing the model name and
#         other details.
#         provider (ModelProvider | None, optional): The model provider object.
#         If None,  a provider will be determined based on the
#         `model_to_provider_mapping`.

#     Returns:
#         Response: The model completion result as a Response object.
#     """

#     completion_method = model_inference_mapping.get(
#         request.model_name, _litellm_completion
#     )
#     if provider is None and model_to_provider_maping.get(
#         request.model_name, ""
#     ) != "":
#         provider = ModelProvider(
#             provider_name=model_to_provider_maping.get(request.model_name, "")
#         )
#     return completion_method(request, provider)


def main():
    user_message = "Hello, whats the weather in San Francisco??"
    request = Request(
        model_name="codellama/CodeLlama-7b-hf",
        prompt=user_message,
    )
    response = huggerface_local_completion(request)
    print("Response from stabilityai/stablecode-completion-alpha-3b-4k")
    print(response)
    print("\n\n")


if __name__ == "__main__":
    main()
