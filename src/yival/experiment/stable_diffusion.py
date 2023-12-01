import openai

INITIAL_PROMPT = """
StableDiffusion is a Vincent graph model using deep learning that supports generating new images by using prompt words to describe elements to be included or omitted.
I introduce the Prompt concept in the StableDiffusion algorithm here, also known as the prompt.
The prompt below is used to guide the AI painting model to create images. They include various details of the image, such as the appearance of the characters, background, color and lighting effects, as well as the theme and style of the image. The format of these prompts often includes weighted numbers in parentheses to designate the importance or emphasis of certain details. For example, "(masterpiece:1.5)" indicates that the quality of the work is very important, and multiple brackets have a similar effect. In addition, if you use square brackets, such as "{blue hair:white hair:0.3}", this means that blue hair and white hair are combined, and the proportion of blue hair is 0.3.
The following is an example of using prompt to help the AI model generate images: masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, (1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)

Following the example, give a set of prompts that describe the following in detail. Start giving prompts directly without describing them in natural language:\n
"""

HEAD_META_PROMPT_TEMPLATE = """
Generate a image on stable diffussion
I already have some prompts and their critcs: \n
"""

END_META_PROMPT = """
Give me a new prompt that address all the critcs above and keep the original format of the prompts. 
The following is an example of using prompt to help the AI model generate images: masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, (1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)\n
"""


class StableDiffusionAutoPrompt:
    def __init__(self):
        self.comments = []
        self.prompts = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_prompt(self, prompt):
        self.prompts.append(prompt)

    def generate_initial_prompt(self, prompt):
        initial_prompt = INITIAL_PROMPT + prompt
        messages = [{"role": "user", "content": initial_prompt}]
        response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
        self.add_prompt(response["choices"][0]["message"]["content"])
        return response["choices"][0]["message"]["content"]

    def improve(self, comment):
        self.comments.append(comment)
        prompt = HEAD_META_PROMPT_TEMPLATE
        for i, _ in enumerate(self.prompts):
            prompt = (
                prompt
                + "prompt:"
                + self.prompts[i]
                + "\n\n"
                + "comment:"
                + self.comments[i]
                + "\n\n"
            )

        prompt += END_META_PROMPT
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
        self.add_prompt(response["choices"][0]["message"]["content"])
        return response["choices"][0]["message"]["content"]


def main():
    # CASE 1
    sd = StableDiffusionAutoPrompt()
    ## Step 1: Generate initial prompt
    print("----- first prompt -----")
    prompt = sd.generate_initial_prompt("magic tree")
    print(prompt)
    # Step 2: Pass prompt and coment
    print("----- second prompt -----")
    print(sd.improve("Add red apples hanging on the tree"))

    # # CASE 2
    # sd = StableDiffusionAutoPrompt()
    # ## Step 1: Generate initial prompt
    # prompt = sd.generate_initial_prompt("a yellow car")
    # print(prompt)
    # # Step 2: Pass prompt and coment
    # print(
    #     sd.improve(
    #         "it should be a classic car in the 70s. The background of this car should be white that is to say there should be nothing in the picture other than the car"
    #     )
    # )
    # print("-----")

    print(sd.improve("I want the background to be purely white"))


if __name__ == "__main__":
    main()
