import openai

INITIAL_PROMPT = """
I want you to act as a prompt generator for Stable Difusion artificial intelligence program.
Your job is to provide detailed and creative descriptions that will inspire unique and interesting
images from the AI.
Keep in mind that the AI is capable of understanding a wide range of language and can interpret
abstract concepts, so feel free to be as imaginative and descriptive as possible. 
For example, you could describe a scene from a futuristic city, or a surreal
landscape filled with strange creatures. The more detailed and imaginative your description,
the more interesting the resulting image will be. Here is your first prompt: \n

"""

HEAD_META_PROMPT_TEMPLATE = """
Generate a image on stable diffussion
I already have some prompt and its comment: \n

"""

END_META_PROMPT = """
Give me a new prompt that is different from all pairs above, and address all the comment above and keep the essense of the task
"""


class StableDiffusionAutoPrompt():

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
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=messages
        )
        self.add_prompt(response['choices'][0]['message']['content'])
        return response['choices'][0]['message']['content']

    def improve(self, comment):
        self.comments.append(comment)
        prompt = HEAD_META_PROMPT_TEMPLATE
        for i, _ in enumerate(self.prompts):
            prompt = prompt + "prompt:" + self.prompts[
                i] + "\n\n" + "comment:" + self.comments[i] + "\n\n"

        prompt += END_META_PROMPT
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=messages
        )
        self.add_prompt(response['choices'][0]['message']['content'])
        return response['choices'][0]['message']['content']


def main():
    sd = StableDiffusionAutoPrompt()
    ## Step 1: Generate initial prompt
    prompt = sd.generate_initial_prompt("wooden house for horror game")
    ## print(prompt)
    ## Step 2: Pass prompt and coment
    # print(
    #     sd.improve(
    #         TEST_PROMPT,
    #         "The house need to be smaller, one story and three rooms"
    #     )
    # )


if __name__ == "__main__":
    main()
