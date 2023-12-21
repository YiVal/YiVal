import openai

INITIAL_PROMPT = """
Diffusion is a Vincent graph model using deep learning that supports
generating new images by using prompt words to describe elements to be
included or omitted. I introduce the Prompt concept in the StableDiffusion
algorithm here, also known as the prompt.

Here is the guide to generate stable diffusion prompt:
Start by clearly defining your subject. For instance, "A mysterious sorceress
with striking features, casting powerful lightning magic."
Specify the artistic medium. Example: "The image should resemble a digital
painting."
Include the desired artistic style. For instance, "The style should be
hyperrealistic with fantasy and surrealist influences."
Mention any artists whose style you want to emulate. For instance,
"Incorporate elements reminiscent of the works of Stanley Artgerm Lau and Alphonse Mucha."

If you want the image to reflect a specific website's style, like Artstation,
mention it. Example: "The image should have an Artstation-like quality."
Indicate your preference for the image's resolution and detail. For instance, 
"The image should be highly detailed with a sharp focus."
Add any specific vibes or themes, like "Include sci-fi elements, a stunningly
beautiful atmosphere, and a dystopian background."
If you have a preference for certain colors, mention them.
Example: "The dominant color should be iridescent gold."
Describe the desired lighting. For instance, "Use cinematic lighting with dark,
moody undertones."
Include what you don't want in the image in negative prompt. Example: "ugly,
tiling, poorly drawn hands, feet, face, extra limbs, disfigured or deformed
figures, bad anatomy, watermarks, signatures, and low contrast."
Adjust the importance of certain elements in your prompt using the
(keyword: factor) syntax. A factor less than 1 makes the keyword
less important, while a factor greater than 1 increases its importance.
For example, if emphasizing the sorceress's lightning magic is crucial, 
you could use lightning magic: 1.5. Conversely, to de-emphasize an element, 
like dystopian background: 0.5.
() for Strength Adjustment:
Use parentheses () to slightly increase the strength of a keyword. 
Multiple parentheses or brackets multiply this effect.
For instance, ((lightning magic)) makes the lightning magic more prominent.
If aiming for consistency in certain features across multiple images, 
use multiple related keywords with weights.
For example, (striking features:0.5), (mysterious aura:1.2) ensures that
the sorceress's features and aura are blended consistently.
Reinforce your negative prompts with weighting or strength adjustment for
unwanted elements. Example: (ugly:0.5), (poorly drawn hands:0), 
indicating a strong avoidance of these elements. 
Use color and lighting keywords with weights to emphasize or de-emphasize
certain aspects.
For instance, (iridescent gold: 1.3), (cinematic lighting: 1.2).

The followings are 5 examples of using prompt to help the AI model generate images: 
1. masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, (1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)
2. watermark, (worst quality), (low quality), (normal quality), lowres, monochrome, greyscale
3. (fox looking at monitor that says "404 NOT FOUND":1.2), monitor brand name "FOX", (high quality, masterpiece, high res:1.3), genderless, simple art style, text, (confused, data center server room, anthro furry, facing away, straight on:1.2)
4. (((fantasy masterpiece:1.5))), (best quality:1.5), (ultra detailed face, ultra detailed eyes, detailed mouth, detailed body, detailed hands, ultra detailed clothes, detailed background:1.5), (aesthetic + beautiful + harmonic:1.5), (symmetrical intricate details + sharpen symmetrical details) | (((close up of dignified female martial artist with luscious hair and bright eyes, she wears an elegant hanfu while walks beside her dragon friend:1.5))
5. ((masterpiece:1.3,concept art,best quality)),very cute appealing anthropomorphic kitten,looking at the fruit,big grin,happy,sunshine,,droplets,macro,fog,(holding a sign that says "404"):1.,cartoon art,dynamic composition,dramatic lighting,epic realistic,award winning illustration

ollowing the example, a prompt that describe the following in detail. 
Start giving {number_of_prompt} prompts directly without describing them in natural language:\n

"""

HEAD_META_PROMPT_TEMPLATE = """
Generate a image on stable diffussion with the guide
Start by clearly defining your subject. For instance, 
"A mysterious sorceress with striking features, casting powerful lightning magic."
Specify the artistic medium. 
Example: "The image should resemble a digital painting."
Include the desired artistic style. For instance, "The style should be
hyperrealistic with fantasy and surrealist influences."
Mention any artists whose style you want to emulate. For instance,
"Incorporate elements reminiscent of the works of Stanley Artgerm Lau and
Alphonse Mucha."
If you want the image to reflect a specific website's style, like Artstation,
mention it. Example: "The image should have an Artstation-like quality."
Indicate your preference for the image's resolution and detail. For instance,
"The image should be highly detailed with a sharp focus."
Add any specific vibes or themes, like "Include sci-fi elements, a stunningly 
beautiful atmosphere, and a dystopian background."
If you have a preference for certain colors, mention them. Example: "The
dominant color should be iridescent gold."
Describe the desired lighting. For instance, "Use cinematic lighting with dark,
moody undertones."
Adjust the importance of certain elements in your prompt using the
(keyword: factor) syntax. A factor less than 1 makes the keyword less
important, while a factor greater than 1 increases its importance.
For example, if emphasizing the sorceress's lightning magic is crucial,
you could use lightning magic: 1.5. Conversely, to de-emphasize an element,
like dystopian background: 0.5.
()  Syntax for Strength Adjustment:
Use parentheses () to slightly increase the strength of a keyword.
Multiple parentheses or brackets multiply this effect.
For instance, ((lightning magic)) makes the lightning magic more prominent
If aiming for consistency in certain features across multiple images, 
use multiple related keywords with weights.
For example, (striking features:0.5), (mysterious aura:1.2) ensures that 
the sorceress's features and aura are blended consistently.
Use color and lighting keywords with weights to emphasize or de-emphasize
certain aspects.
For instance, (iridescent gold: 1.3), (cinematic lighting: 1.2).

The followings are 5 examples of using prompt to help the AI model generate 
images:
1. masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, 
(1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),
(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)
2. watermark, (worst quality), (low quality), (normal quality), lowres, monochrome, greyscale
3. (fox looking at monitor that says "404 NOT FOUND":1.2), monitor brand name "FOX", (high quality, masterpiece, high res:1.3), genderless, simple art style, text, (confused, data center server room, anthro furry, facing away, straight on:1.2)
4. (((fantasy masterpiece:1.5))), (best quality:1.5), (ultra detailed face, ultra detailed eyes, detailed mouth, detailed body, detailed hands, ultra detailed clothes, detailed background:1.5), (aesthetic + beautiful + harmonic:1.5), (symmetrical intricate details + sharpen symmetrical details) | (((close up of dignified female martial artist with luscious hair and bright eyes, she wears an elegant hanfu while walks beside her dragon friend:1.5))
5. ((masterpiece:1.3,concept art,best quality)),very cute appealing anthropomorphic kitten,looking at the fruit,big grin,happy,sunshine,,droplets,macro,fog,(holding a sign that says "404"):1.,cartoon art,dynamic composition,dramatic lighting,epic realistic,award winning illustration

I already have some prompts and their critcs and scores: \n
"""

END_META_PROMPT = """
Give me a total of {num_of_prompt} prompts that address all the critcs above if not empty.
And different from the prompts above. As well as try to increase the score.
Emphezise on solving the critics
The followings is an example of using prompt to help the AI model generate 
images in the format of [prompt]:
[masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, (1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)]
Remember to genreate exact {num_of_prompt} prompts.
No need to add quote around the words in the prompts and make sure you use () to adjust the importance of certain elements in your prompt using the (keyword: factor) syntax. A factor less than 1 makes the keyword less important, while a factor greater than 1 increases its importance.

"""

EVALUATION_PROMPT = """
Given the prompts that will be used to generate stable diffusion image from 0(bad) to 1(good):
A good prompt typically following:
Define Subject: Start with a clear subject, like "A sorceress casting lightning magic."
Medium & Style: Specify the artistic medium (e.g., digital painting) and style (e.g., hyperrealistic with fantasy influences).
Artist Influences: Mention styles of specific artists you want to emulate.
Website Style Reference: Include if you want to mimic a specific website's style (e.g., Artstation).
Resolution & Detail: Indicate your preference for detail level and resolution.
Themes & Vibes: Add desired themes (e.g., sci-fi, dystopian) and color preferences.
Lighting: Describe the lighting style (e.g., cinematic with moody undertones).
Keyword Adjustment: Use (keyword: factor) to adjust element importance.
Strength Adjustment: Use parentheses to increase keyword strength.
Consistency Across Images: Use related keywords with weights for consistent features.
Weighted Color & Lighting: Emphasize certain aspects with weighted color and lighting keywords.


Some good prompt examples:
1. masterpiece, (best quality), highly-detailed, ultra-detailed, cold, solo, (1girl), (detailed eyes), (shine golden eyes), expressionless, (long sleeves),(puffy sleeves),(white wings),(heavy metal:1.2),(metal jewelry), cross-laced footwear, (chain),(White doves:1.2)
2. watermark, (worst quality), (low quality), (normal quality), lowres, monochrome, greyscale

Below are the prompts that need to be scored, each line represents a unique prompt:

{prompts}

Return the score of the pormpts score pair in the format of
(prompt, score)

"""


def extract_prompt_and_score(input_string):

    parts = input_string.rsplit(':', 1)

    # Extracting the description and score
    prompt = parts[0].strip() if len(parts) > 1 else input_string.strip()
    current_score = float(
        parts[1].strip()
    ) if len(parts) > 1 and parts[1].strip().replace('.', '',
                                                     1).isdigit() else None
    return prompt, current_score


def extract_score(input_string):
    import re

    # Regular expression pattern to extract (prompt, score) pairs
    pattern = r'\("(.*?)"\s*,\s*(\d+\.\d+)\)'

    # Extracting all matches
    matches = re.findall(pattern, input_string)

    # Formatting the output
    extracted_pairs = [
        "{} : {}".format(match[0], match[1]) for match in matches
    ]
    return extracted_pairs


def extract_string_array(input_text):
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]

    # Extracting the string and removing outer square brackets and leading number
    string_array = [line[line.find('['):].strip('[]') for line in lines]

    return string_array


class StableDiffusionAutoPrompt:

    def __init__(self):
        self.comments = {}
        self.prompts = {}

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_prompt(self, prompt, score):
        self.prompts[prompt] = score

    def generate_initial_prompt(self, prompt, n=4):
        initial_prompt = INITIAL_PROMPT.format(number_of_prompt=n) + prompt
        messages = [{"role": "user", "content": initial_prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=messages, temperature=0.5
        )
        self.add_prompt(response["choices"][0]["message"]["content"], 0)
        return response["choices"][0]["message"]["content"]

    def score_prompts(self, prompts):
        print("score prompts")
        prompt = EVALUATION_PROMPT.format(prompts='\n'.join(prompts))
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=messages
        )
        score_pair = extract_score(
            response["choices"][0]["message"]["content"]
        )
        return score_pair

    def improve(
        self,
        previous_prompt: str,
        number_of_iterations: int = 2,
        number_of_prompts_needed: int = 4,
        comment=""
    ):
        if previous_prompt not in self.prompts:
            score_pair = self.score_prompts([previous_prompt])
            prompt, score = extract_prompt_and_score(score_pair[0])
            current_score = score_pair[0].split(':')[1].strip()
            self.add_prompt(previous_prompt, score)
        self.comments[previous_prompt] = comment
        prompt = HEAD_META_PROMPT_TEMPLATE
        end_prompt = END_META_PROMPT.format(
            num_of_prompt=number_of_prompts_needed
        )
        for p, score in self.prompts.items():
            prompt = (
                prompt + "prompt:" + p + "\n\n" + "comment:" +
                self.comments[p] + "\n\n" + "score: " + str(score) + "\n\n"
            )

        prompt += end_prompt
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=messages
        )

        res = extract_string_array(
            response["choices"][0]["message"]["content"]
        )

        while len(res) >= number_of_prompts_needed + 3 or len(
            res
        ) < number_of_prompts_needed:
            response = openai.ChatCompletion.create(
                model="gpt-4", messages=messages
            )
            #self.add_prompt(response["choices"][0]["message"]["content"])
            res = extract_string_array(
                response["choices"][0]["message"]["content"]
            )
        if number_of_iterations > 1:
            score_pairs = self.score_prompts(res)
            current_score = -100
            current_prompt = ""
            for score in score_pairs:
                prompt_f, score_f = extract_prompt_and_score(score)
                if score_f > current_score:
                    current_score = score_f
                    current_prompt = prompt_f
            self.add_prompt(current_prompt, current_score)
            res = self.improve(
                current_prompt, number_of_iterations - 1,
                number_of_prompts_needed
            )
        return res[:number_of_prompts_needed]


def main():
    # CASE 1
    sd = StableDiffusionAutoPrompt()
    ## Step 1: Generate initial prompt
    print("----- first prompt -----")

    #prompt = sd.generate_initial_prompt("tencent logo penguin")
    prompts = sd.improve(
        previous_prompt=
        "(Tencent:1.3), (high-quality, masterpiece), detailed, (3D modeling:1.2), (penguin logo:1.5), (bold colors: 1.2), modern design, clean lines, corporate style, minimalistic background.",
        comment="the penguin need to have black fur, red scarf, yellow mouth"
    )
    print(prompts)
    # Initialize the pipeline with the desired model, setting the torch dtype and variant

    #Step 2: Pass prompt and coment
    print("----- second prompt -----")
    print(
        sd.improve(
            previous_prompt=prompts[0],
            comment="the background need have a lot of snow"
        )
    )
    # print("----- 3 prompt -----")
    # print(sd.improve("it must be wooden"))
    # print("----- 4 prompt -----")
    # print(sd.improve("the back scene should fits in dark theme"))


if __name__ == "__main__":
    main()
