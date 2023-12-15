import openai
import argparse
import ast

# INITIAL_PROMPT = """
# I want you to act as a prompt generator for Stable Difusion artificial intelligence program.
# Your job is to provide detailed and creative descriptions that will inspire unique and interesting
# images from the AI.
# Keep in mind that the AI is capable of understanding a wide range of language and can interpret
# abstract concepts, so feel free to be as imaginative and descriptive as possible.
# For example, you could describe a scene from a futuristic city, or a surreal
# landscape filled with strange creatures. The more detailed and imaginative your description,
# the more interesting the resulting image will be. Here is your first prompt: \n
# StableDiffusion is a Vincent graph model using deep learning that supports generating new images by using prompt words to describe elements to be included or omitted.
# I introduce the Prompt concept in the StableDiffusion algorithm here, also known as the prompt.
# The prompt below is used to guide the AI painting model to create images. They include various details of the image, such as the appearance of the characters, background, color and lighting effects, as well as the theme and style of the image. The format of these prompts often includes weighted numbers in parentheses to designate the importance or emphasis of certain details. For example, "(masterpiece:1.5)" indicates that the quality of the work is very important, and multiple brackets have a similar effect. In addition, if you use square brackets, such as "{blue hair:white hair:0.3}", this means that blue hair and white hair are combined, and the proportion of blue hair is 0.3.
# The following is an example of using prompt to help the AI model generate images: masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, (1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)
# Following the example, give a set of prompts that describe the following in detail. Start giving prompts directly without describing them in natural language:\n
# """

INITIAL_PROMPT = """
I want you to act as a prompt generator for Stable Difusion artificial intelligence program.
Your job is to provide detailed and creative descriptions that will inspire unique and interesting
images from the AI.
Keep in mind that the AI is capable of understanding a wide range of language and can interpret
abstract concepts, so feel free to be as imaginative and descriptive as possible.

Describe the image you want using keywords and, if necessary, assign weights to emphasize certain aspects.
For instance, you can use phrases like ({keyword1}:{weight1}), ({keyword2}:{weight2}), and so on.
You can also combine keywords with weights, such as ({element1}:{element2}:{weight_element1}), to specify relationships.

Here is an example prompt format: ({fantasy:1.5}), ({surreal:1.2}), ({futuristic:1.8}), ({cityscape:0.9}), ({creatures:1.2}),
({character:1.5}), ({background:1.2}), ({color:1.2}), ({lighting:1.5}), ({theme:1.2}), ({style:1.5}).

Feel free to provide multiple prompts or variations to guide the AI in generating diverse images.
Following the example, give a set of prompts that describe the following in detail.
Start giving prompts directly without describing them in natural language:\n
"""





HEAD_META_PROMPT_TEMPLATE = """
Generate a image on stable diffussion with the guide
Start by clearly defining your subject. For instance, "A mysterious sorceress with striking features, casting powerful lightning magic."
Specify the artistic medium. Example: "The image should resemble a digital painting."
 Include the desired artistic style. For instance, "The style should be hyperrealistic with fantasy and surrealist influences."
Mention any artists whose style you want to emulate. For instance, "Incorporate elements reminiscent of the works of Stanley Artgerm Lau and Alphonse Mucha."
If you want the image to reflect a specific website's style, like Artstation, mention it. Example: "The image should have an Artstation-like quality."
Indicate your preference for the image's resolution and detail. For instance, "The image should be highly detailed with a sharp focus."
Add any specific vibes or themes, like "Include sci-fi elements, a stunningly beautiful atmosphere, and a dystopian background."
If you have a preference for certain colors, mention them. Example: "The dominant color should be iridescent gold."
Describe the desired lighting. For instance, "Use cinematic lighting with dark, moody undertones."
Include what you don't want in the image in negative prompt. Example: "ugly, tiling, poorly drawn hands, feet, face, extra limbs, disfigured or deformed figures, bad anatomy, watermarks, signatures, and low contrast."
Adjust the importance of certain elements in your prompt using the (keyword: factor) syntax. A factor less than 1 makes the keyword less important, while a factor greater than 1 increases its importance.
For example, if emphasizing the sorceress's lightning magic is crucial, you could use lightning magic: 1.5. Conversely, to de-emphasize an element, like dystopian background: 0.5.
() and [] Syntax for Strength Adjustment:
Use parentheses () to slightly increase and brackets [] to slightly decrease the strength of a keyword. Multiple parentheses or brackets multiply this effect.
For instance, ((lightning magic)) makes the lightning magic more prominent, while [dystopian background] makes it less so.
Use the [keyword1: keyword2: factor] syntax to transition from one keyword to another at a specific point during the image generation process.
For example, sorceress[early phase: late phase: 0.5] can be used to start with a focus on the sorceress and transition to another theme halfway through the process.
If aiming for consistency in certain features across multiple images, use multiple related keywords with weights.
For example, (striking features:0.5), (mysterious aura:1.2) ensures that the sorceress's features and aura are blended consistently.
Reinforce your negative prompts with weighting or strength adjustment for unwanted elements. Example: [(ugly:0.5), (poorly drawn hands:0)], indicating a strong avoidance of these elements.
Use color and lighting keywords with weights to emphasize or de-emphasize certain aspects.
For instance, (iridescent gold: 1.3), (cinematic lighting: 1.2).
I already have some prompts and their critcs: \n
"""

END_META_PROMPT = """
Give me a new prompt that address all the critcs above and keep the original format of the prompts. Emphezise on solving the critics
The followings is an example of using prompt to help the AI model generate images:
masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, (1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)
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
        response = openai.ChatCompletion.create(
            model="GPT-4 Turbo", messages=messages
        )
        self.add_prompt(response["choices"][0]["message"]["content"])
        return response["choices"][0]["message"]["content"]

    def improve(self, comment):
        self.comments.append(comment)
        prompt = HEAD_META_PROMPT_TEMPLATE
        for i, _ in enumerate(self.prompts):
            prompt = (
                prompt + "prompt:" + self.prompts[i] + "\n\n" + "comment:" +
                self.comments[i] + "\n\n"
            )

        prompt += END_META_PROMPT
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=messages
        )
        self.add_prompt(response["choices"][0]["message"]["content"])
        return response["choices"][0]["message"]["content"]

parser = argparse.ArgumentParser(description="Arguments for stable_diffusion",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-t", "--iteration", default = 1, help="number of iteration")
parser.add_argument("-n", "--prompts", default = 1, help="number of prompts")
parser.add_argument("-c", "--comment", help="comment")
parser.add_argument("-p", "--prev", default="[]", nargs='+', help="previous prompts")
args = parser.parse_args()
# config = vars(args)

def main(NumofIter, NumOfPrompts, comment, prev_prompts_list):
    # NumofIter: num of iteration
    # NumOfPrompts: num of output prompts
    # comment: user's comments
    # prev_prompts: previous prompts

    prompts = []
    prev_prompts = prev_prompts_list
    # Break loop if we have enough output prompts
    while len(prompts) < int(NumOfPrompts):
        sd = StableDiffusionAutoPrompt()

        # If no previous prompts provided
        if prev_prompts == []:

            i = 0
            cur_prompt = sd.generate_initial_prompt(comment)

            # Iteration "NumofIter" times, argument given by user
            while i < int(NumofIter):
                cur_prompt = sd.improve(cur_prompt)
                i += 1

            prompts.append(cur_prompt)

        # Previous prompts provided, in this case, we don't need to generate initial
        # prompt, we are only doing improvements
        else:

            # Improve for each previous prompt, add comment to the prompt and
            # improve it, after NumofIter iterations, append the prompt in the list
            for prevP in prev_prompts:
                cur_prompt = prevP + comment
                for i in range(int(NumofIter)):
                    cur_prompt = sd.improve(cur_prompt)
                    # print(len(cur_prompt))
                prompts.append(cur_prompt)

    return prompts

if __name__ == "__main__":
    prompts = main(NumofIter=args.iteration, NumOfPrompts=args.prompts,
    comment=args.comment, prev_prompts_list=args.prev)
    print("Generated prompts:")
    for i, prompt in enumerate(prompts):
        print(f"Prompt {i + 1} prompt: {prompt}")



    # # CASE 1
    # sd = StableDiffusionAutoPrompt()
    # ## Step 1: Generate initial prompt
    # print("----- first prompt -----")
    # prompt = sd.generate_initial_prompt("a treasure chest")
    # print(prompt)
    # # Initialize the pipeline with the desired model, setting the torch dtype and variant

    # #Step 2: Pass prompt and coment
    # print("----- second prompt -----")
    # print(sd.improve("it must be cute"))
    # print("----- 3 prompt -----")
    # print(sd.improve("it must be wooden"))
    # print("----- 4 prompt -----")
    # print(sd.improve("the back scene should fits in dark theme"))


# if __name__ == "__main__":
#     main()
