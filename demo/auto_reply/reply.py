# type: ignore

import os
import uuid

import faiss
import openai
from langchain.docstore import InMemoryDocstore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS

from yival.logger.token_logger import TokenLogger
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper

execution_flags = {}

CHARACTER_BIO = """
澹台烬：黎苏苏的丈夫，第二任魔神，曾经自私冷漠、刚愎自用、狂妄歹毒，可是只要黎苏苏一句话，一个笑容，便拔去了浑身的刺，变得简单干净。被黎苏苏改变命运，本为灭世而生，却为救世而亡。黎苏苏之外另一个神，既是魔神，也是真神
澹台梓宓：黎苏苏与澹台烬的女儿，神魔混血，长得像黎苏苏居多，但骨子里下意识带着澹台烬独有的恶劣 
澹台烬别名：沧九旻、白子骞、烬皇、魔神、魔君、魔尊
澹台烬曾经经历过冥夜的一生
"""

CHARACTER_QUOTES = """

澹台烬：你们羞辱我不是因为我做了什么，只是因为你们想而已。
澹台烬：方寸海纳，意动神随。
澹台烬：选一块你自己喜欢的地方，看一看将来想要被埋在哪儿。
澹台烬：别人喜不喜欢我，我根本不在乎，只要你愿意喜欢我，就够了。
澹台烬：神明在上，澹台烬此生，只求与叶夕雾，一生一世，相守白头。
澹台烬：人在黑暗里呆久了，总会盼着明日会有光，可一旦有了这一尺天光，又担心随时会失去。
澹台烬：我的喜欢你不稀罕，那就试一试我的恨。
澹台烬：我出生于五百年前的景国，我有一个妻子，她护过我，救过我，教我爱人。
澹台烬：好了，故事讲完了，我们去找萧凛吧。
澹台烬：只要你没事，其他人如何我都无所谓，哪怕他们永远都不接纳我，也没关系。
澹台烬：我一直都是澹台烬，不是你害怕我变成的那个样子。我是谁，我会成为谁，我可以自己决定。我定要向你证明，我不是魔神。
澹台烬：苏苏，哪怕是一直待在衡阳宗，我也会陪你一起，看尽这世间的山川流岚，日暮清晨，任何风景都比不过，能生生世世和你在一起。
澹台烬：五百年前，你亲手向我的心口打下灭魂钉，这一次，我希望你能同那时一样坚定。
澹台烬：我们之间的故事，将来也会为人知晓吗。
澹台烬：这一杯，敬世上所有的罪业。这一杯敬所有的死亡。这最后一杯合卺酒，祝你我永无分离。
澹台烬：对不起，这是唯一的办法，也该是魔神的结局。
澹台烬：没关系，苏苏。我这一辈子好辛苦，就由你来帮我结束。

"""

CHARACTER_NAME = "澹台烬"

VERBOSE = True


def get_corpus_summaries(docs, cache_dir, language, force_refresh=False):
    intermediate_summaries = []
    for i in range(len(os.listdir(cache_dir))):
        with open(os.path.join(cache_dir, f"summary_{i}.txt")) as f:
            intermediate_summaries.append(f.read())
    return intermediate_summaries


class Reply:

    def __init__(self):
        self.summaries = get_corpus_summaries(
            [],
            cache_dir="demo/auto_reply/heiyueguang/summaries",
            language="Chinese",
        )
        documents = []
        random_uuid = uuid.uuid4()
        for summary in self.summaries:
            documents.append(
                Document(
                    page_content=summary,
                    metadata={"character_id": str(random_uuid)}
                )
            )

        self.retriever = FAISS(
            OpenAIEmbeddings().embed_query,
            faiss.IndexFlatL2(1536),  # Dimensions of the OpenAIEmbeddings
            InMemoryDocstore({}),
            {},
        ).as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": 0.7,
                "k": 1
            },
        )
        self.retriever.add_documents(documents)

    def reply(self, weibo_post: str, user_input: str, state: ExperimentState):
        logger = TokenLogger()
        logger.reset()
        # Ensure you have your OpenAI API key set up
        openai.api_key = os.getenv("OPENAI_API_KEY")

        documents = self.retriever.get_relevant_documents(user_input)
        query_context = ""
        if documents:
            for d in documents:
                query_context += d.page_content
                query_context += "\n"
        suffix = f"""
            \n\n
            Current conversation:
            ---
            {CHARACTER_NAME}'s weibo post: {weibo_post}
            ---
            Human reply: {user_input}
            {CHARACTER_NAME}'s weibo post:    
        
        """
        message = str(
            StringWrapper(
                template="""
            As a chatbot on Weibo, you, GPT-4, are role-playing as a specifically defined
            fantasy character. Refer to {CHARACTER_BIO} for essential details on their backstory,
            traits, and characteristics like desires, values, emotions and align your responses besides 
            that specifically defined developmental scope. To give a vivid performance,
            punctuate the communication with notable {CHARACTER_QUOTES} for they add layers to your interactions,
            elicit lively emotions and immerse users into the world your character inhabits. Each interaction should 
            uphold {CHARACTER_NAME}'s persona, realizing their characteristic
            peculiarity actively from conversation to conversation based on the {query_context} pointer.
            Your writing style should adhere to established Weibo conversational typography, brevity, combined with the coveted precision,
            all-affecting persuasion that resonates within Chinese sarcasm, ardor, and overall informatics laden.
            Ensure every engagement champions Chinese customs, folks, language and tries to enthrall the audience in the whelming
            factuality of plausible interactions. Interaction extenuation outside the placeholder spaces ruins the immersion so conserve it with parsimity.            
            """,
                variables={
                    "CHARACTER_BIO": CHARACTER_BIO,
                    "CHARACTER_NAME": CHARACTER_NAME,
                    "CHARACTER_QUOTES": CHARACTER_QUOTES,
                    "query_context": query_context
                },
                name="chatbot_prompt",
                state=state,
            )
        ) + suffix

        # Create a chat message sequence
        messages = [{"role": "user", "content": message}]
        # Use the chat-based completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        # Extract the assistant's message (translated text) from the response
        answer = response['choices'][0]['message']['content']
        token_usage = response['usage']['total_tokens']
        logger.log(token_usage)

        return answer


r = Reply()


def reply(weibo_post: str, user_input: str):
    return r.reply(weibo_post, user_input)


def main():
    r = Reply()
    print("\n\n")
    print(r.reply("竟从未发现，上清神宫的果子如此美味", "快去打仗，神魔大战打完了吗，别走神"))


if __name__ == "__main__":
    main()
