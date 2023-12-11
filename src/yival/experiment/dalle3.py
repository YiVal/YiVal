from openai import OpenAI

import os

INITIAL_PROMPT = """
DALLE-3 is a transformer-based generative model developed by OpenAI that generates images from textual descriptions, also known as prompts. The quality of the generated images depends greatly on the specificity and descriptiveness of the prompts.

Here is the guide to generate DALLE-3 prompts:

1. Be specific and detailed: Provide a clear and detailed description of your subject. For example, "A majestic white unicorn standing on a cliff overlooking a rainbow-colored waterfall."
2. Mood and atmosphere: Describe the mood or atmosphere you want in the image. For instance, "The image should evoke a sense of serene tranquility and mystical wonder."
3. Use descriptive adjectives: Use adjectives to refine your description. Instead of saying "a bird," say "a vibrant, multi-colored tropical bird with long, flowing tail feathers."
4. Perspective and composition: Specify the perspective or composition you want, such as a close-up, a wide shot, a bird’s-eye view, or a specific angle.
5. Lighting and time of day: Describe the lighting conditions and the time of day. For example, "The scene should be bathed in the soft, golden glow of a setting sun."
6. Incorporate action or movement: Describe any actions or movements to make the image more dynamic. For example, "The unicorn should be rearing up on its hind legs with its mane flowing in the wind."
7. Avoid overloading the prompt: While details enhance the image, too many can confuse the AI. Strive for a balance between being descriptive and being concise.
8. Use analogies or comparisons: If it helps, compare what you want with something well-known. For example, "The image should be in the style of a Hayao Miyazaki animation."
9. Specify desired styles or themes: If you have a particular artistic style or theme in mind, mention it. For example, "The image should have a fantasy theme with a touch of surrealism."
10. Iterative approach: If the first image doesn't meet your expectations, refine your prompt based on the results and try again.

Here are some examples of DALLE-3 prompts:

1. Prompt: "A quiet, peaceful forest glade bathed in the soft, dappled light of a setting sun, with a majestic stag standing in the foreground. The image should have a fantasy theme and resemble a digital painting in the style of Thomas Kinkade."

2. Prompt: "A futuristic cyberpunk cityscape at night, glowing with neon lights. The city should be bustling with high-tech vehicles and people, with towering skyscrapers reaching up to the star-filled sky."

3. Prompt: "A whimsical scene of a tea party on the moon, with anthropomorphic rabbit creatures dressed in Victorian clothing. The image should be in the style of a children's book illustration."

Now, please provide a DALLE-3 prompt following the guidelines and examples given. Remember, your prompt should be concise yet detailed, with a clear description of the subject, mood, lighting, movement, perspective, and any specific styles or themes.
"""

INITIAL_EVAL_PROMPT = """
The task here is to create a prompt that guides the AI in generating a thorough, critical evaluation. This prompt will be used in conjunction with the existing metrics: {metric}. The evaluation should rigorously examine common pain points in image generation.

Here is the guide to generate an evaluation prompt:

Define the task: Clearly state the task that the AI needs to perform. For instance, "Critically evaluate the quality of the image and how well it reproduces the details described in the {text content}, paying close attention to common pain points in image generation."
Highlight key factors: Instruct the AI to focus on the metrics. For text relevance, the AI should consider the color, size, and position of the objects in the image. Further, guide the AI to specifically scrutinize the examine common pain points in image generation.
Provide answer options: Give a set of answer options that lean towards a more critical evaluation. This allows the AI to quantify its evaluation.
Guide the AI's reasoning: Ask the AI to print only a single choice from the answer options first, then elaborate its reasoning in a meticulous, step-by-step manner. This ensures that the AI's conclusion is reasoned and not simply stated.
Repeat the answer: Instruct the AI to repeat just the answer by itself on a new line at the end. This ensures clarity and avoids confusion.
Here are some examples of evaluation prompts:

Prompt: "Given an image and its corresponding {text content}, critically evaluate the quality of the image. Pay special attention to the possible rendering of human hands, the uncanny valley effect and realism. Consider the clarity, color saturation, and contrast of the image. Select one of the following options: A) Very poor, B) Poor, C) Fair, D) Satisfactory, E) Good. First, print only a single choice from the options. Then, write out your reasoning in a step-by-step manner. Finally, repeat just the answer by itself on a new line."
Now, please provide an evaluation prompt following the guidelines and examples given. Remember, your prompt should clearly define the task, highlight key factors, provide answer options, guide the AI's reasoning, and repeat the answer.
"""

# INITIAL_EVAL_PROMPT = """
# The task here is to create a prompt that guides the AI in generating a thorough, critical evaluation. This prompt will be used in conjunction with the existing metrics: {metric}. The evaluation should rigorously examine common pain points in image generation such as the rendering of human hands, the generation of meaningful text, the uncanny valley effect of non-imaged characters, the realism of the generated image, the consistency of lighting, and the proportionality of objects.
# Here is the guide to generate an evaluation prompt:
# Define the task: Clearly state the task that the AI needs to perform. For instance, "Critically evaluate the quality of the image and how well it reproduces the details described in the text, paying close attention to common pain points in image generation."
# Highlight key factors: Instruct the AI to focus on the clarity, color saturation, and contrast of the image for image quality. For text relevance, the AI should consider the color, size, and position of the objects in the image. Further, guide the AI to specifically scrutinize the rendering of human hands, the generation of meaningful text, the uncanny valley effect of non-imaged characters, the realism of the image, the consistency of lighting, and the proportionality of objects in the image.
# Provide answer options: Give a set of answer options that lean towards a more critical evaluation. This allows the AI to quantify its evaluation.
# Guide the AI's reasoning: Ask the AI to print only a single choice from the answer options first, then elaborate its reasoning in a meticulous, step-by-step manner. This ensures that the AI's conclusion is reasoned and not simply stated.
# Repeat the answer: Instruct the AI to repeat just the answer by itself on a new line at the end. This ensures clarity and avoids confusion.
# Here are some examples of evaluation prompts:
# Prompt: "Given an image and its corresponding {text content}, critically evaluate the quality of the image. Pay special attention to the possible rendering of human hands, the generation of meaningful text, the uncanny valley effect, realism, lighting consistency, and object proportionality in the image. Consider the clarity, color saturation, and contrast of the image. Select one of the following options: A) Very poor, B) Poor, C) Fair, D) Satisfactory, E) Good. First, print only a single choice from the options. Then, write out your reasoning in a step-by-step manner. Finally, repeat just the answer by itself on a new line."
# Now, please provide an evaluation prompt following the guidelines and examples given. Remember, your prompt should clearly define the task, highlight key factors, provide answer options, guide the AI's reasoning, and repeat the answer.
# """

INITIAL_ENHAN_PROMPT = """
The task here is to create a prompt that will guide the AI in generating an enhancement based on the evaluation. This prompt will be used in conjunction with existing evaluation comments: {eval content} and the former image generation prompt: {image prompt}. Only the new prompt will be returned.
"""

END_META_PROMPT = """
Give me a new prompt that address all the critcs above and keep the original format of the prompts. Emphezise on solving the critics
The followings is an example of using prompt to help the AI model generate images: 
masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, (1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)
"""


class DALLEAutoPrompt:

    def __init__(self):
        self.comments = []
        self.prompts = []

    def add_human_comment(self, comment):
        self.comments.append(comment)

    def add_prompt(self, prompt):
        self.prompts.append(prompt)

    def generate_initial_prompt(self, prompt):
        initial_prompt = INITIAL_PROMPT + prompt
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": initial_prompt
            }]
        )
        self.add_prompt(response.choices[0].message.content)
        return response.choices[0].message.content

    def generate_image(self, prompt):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )

        return response.data[0].url

    def generate_openai_based_evaluation_prompt(self, metric):
        initial_eval_prompt = INITIAL_EVAL_PROMPT.replace("{metric}", metric)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": initial_eval_prompt
            }]
        )
        self.add_prompt(response.choices[0].message.content)
        return response.choices[0].message.content

    def generate_openai_based_enhancement_prompt(
        self, evaluation_result, prompt
    ):
        enhance_prompt = INITIAL_ENHAN_PROMPT.replace(
            "{eval content}", evaluation_result
        ).replace("{image prompt}", prompt)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": enhance_prompt
            }]
        )
        self.add_prompt(response.choices[0].message.content)
        return response.choices[0].message.content

    def openai_based_evaluation(self, prompt, ini_eval_prompt, image_url):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # print(f"[DEBUG]ini_eval_prompt:{ini_eval_prompt}")

        eval_prompt = ini_eval_prompt.replace("{text content}", prompt)
        # print(f"[DEBUG]eval_prompt:{eval_prompt}")
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role":
                "user",
                "content": [
                    {
                        "type": "text",
                        "text": eval_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": image_url,
                    },
                ],
            }],
            max_tokens=600,
        )
        self.add_prompt(response.choices[0].message.content)
        return response.choices[0].message.content


def main():

    # CASE 1
    dalle = DALLEAutoPrompt()
    ## Step 1: Generate initial prompt
    print("----- first generation prompt -----")
    prompt = dalle.generate_initial_prompt(
        # "A newspaper with the headline 'The End of the World'"
        "two hands on piano"
    )
    print(prompt)

    print("----- first image -----")
    initial_image_url = dalle.generate_image(prompt)
    print(initial_image_url)

    print("----- first evaluation prompt -----")
    eval_prompt = dalle.generate_openai_based_evaluation_prompt(
        "the correctness of human hands, five fingers, and the proportion of the hands"
    )
    print(eval_prompt)

    print("----- first evaluation -----")
    evaluation_result = dalle.openai_based_evaluation(
        prompt, eval_prompt, initial_image_url
    )
    print(evaluation_result)

    print("----- first enhancement prompt -----")
    enhance_prompt = dalle.generate_openai_based_enhancement_prompt(
        evaluation_result, prompt
    )
    print(enhance_prompt)

    print("----- first enhancement -----")
    enhancement_image_url = dalle.generate_image(enhance_prompt)
    print(enhancement_image_url)


if __name__ == "__main__":
    main()
