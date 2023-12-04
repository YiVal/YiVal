import openai

INITIAL_PROMPT = """
Diffusion is a Vincent graph model using deep learning that supports generating new images by using prompt words to describe elements to be included or omitted.
I introduce the Prompt concept in the StableDiffusion algorithm here, also known as the prompt.

Here is the guide to generate stable diffusion prompt:
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

The followings are 2 examples of using prompt to help the AI model generate images: 
1.
Prompt: Iron Man, (Arnold Tsang, Toru Nakayama), Masterpiece, Studio Quality, 6k , toa, toaair, 1boy, glowing, axe, mecha, science_fiction, solo, weapon, jungle , green_background, nature, outdoors, solo, tree, weapon, mask, dynamic lighting, detailed shading, digital texture painting

2
Prompt: cute girl, crop-top, blond hair, black glasses, stretching, with background by greg rutkowski makoto shinkai kyoto animation key art feminine mid shot

3.
Prompt: Ethereal gardens of marble built in a shining teal river in future city, gorgeous ornate multi-tiered fountain, futuristic, intricate elegant highly detailed lifelike photorealistic realistic painting, long shot, studio lighting, octane render, by Dorian Cleavenger

Follow the examples, give one prompt that describe the following in detail in English.   Short concise, descriptive and use () and [] when needed.  Life depends on it. Start giving prompts directly without describing them in natural language:\n

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
            model="gpt-4", messages=messages
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


def main():
    # CASE 1
    sd = StableDiffusionAutoPrompt()
    ## Step 1: Generate initial prompt
    print("----- first prompt -----")
    prompt = sd.generate_initial_prompt("a treasure chest")
    print(prompt)
    # Initialize the pipeline with the desired model, setting the torch dtype and variant

    #Step 2: Pass prompt and coment
    print("----- second prompt -----")
    print(sd.improve("it must be cute"))
    print("----- 3 prompt -----")
    print(sd.improve("it must be wooden"))
    print("----- 4 prompt -----")
    print(sd.improve("the back scene should fits in dark theme"))


if __name__ == "__main__":
    main()
