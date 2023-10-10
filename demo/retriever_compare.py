from yival.common.model_utils import llm_completion
from yival.logger.token_logger import TokenLogger
from yival.schemas.experiment_config import MultimodalOutput
from yival.schemas.model_configs import Request
from yival.states.experiment_state import ExperimentState
from yival.wrappers.string_wrapper import StringWrapper


from langchain.vectorstores import Chroma
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.document_loaders import PyPDFLoader
from langchain.retrievers import BM25Retriever, EnsembleRetriever
import time
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
import uuid
import copy
from langchain.retrievers import ParentDocumentRetriever

retriever_from_llm=None
compression_retriever=None
ensemble_retriever=None
MultiVector_retriever=None
PDR_retriever=None
def retriever_method(input: str, method: str)-> str:
    res=""
    global retriever_from_llm
    global compression_retriever
    global ensemble_retriever
    global MultiVector_retriever
    global PDR_retriever
    if method[0] == 'MultiQueryRetriever' and retriever_from_llm==None:
        retriever_from_llm=False

        data = PyPDFLoader("../try/2307.03109.pdf").load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        splits = text_splitter.split_documents(data)

        embedding = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(documents=splits, embedding=embedding).as_retriever()
        llm = ChatOpenAI(temperature=0)
        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=vectordb, llm=llm
        )
        pass
    elif method[0] == 'Contextual_compression' and compression_retriever==None:
        compression_retriever=False

        data = PyPDFLoader("../try/2307.03109.pdf").load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        splits = text_splitter.split_documents(data)
        
        retriever = FAISS.from_documents(splits, OpenAIEmbeddings()).as_retriever()
        llm = OpenAI(temperature=0)
        compressor = LLMChainExtractor.from_llm(llm)
        compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
        pass
    elif method[0] == 'Ensemble_Retriever' and ensemble_retriever==None:
        ensemble_retriever=False

        data = PyPDFLoader("../try/2307.03109.pdf").load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        splits = text_splitter.split_documents(data)
        
        doc_list = [i.page_content for i in splits]
        bm25_retriever = BM25Retriever.from_texts(doc_list)
        bm25_retriever.k = 2

        embedding = OpenAIEmbeddings()
        faiss_vectorstore = FAISS.from_texts(doc_list, embedding)
        faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 2})
        ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5])
        pass
    elif method[0] == 'MultiVector_Retriever' and MultiVector_retriever==None:
        MultiVector_retriever=False
        
        loaders=[ PyPDFLoader("../try/2307.03109.pdf")
         ,PyPDFLoader("../try/2307.03109_1.pdf")]
        docs = []
        for l in loaders:
            docs.extend(l.load())
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma(
            collection_name="full_documents",
            embedding_function=OpenAIEmbeddings()
        )
        store = InMemoryStore()
        id_key = "doc_id"
        retriever = MultiVectorRetriever(
            vectorstore=vectorstore, 
            docstore=store, 
            id_key=id_key,
        )
        doc_ids = [str(uuid.uuid4()) for _ in docs]
        child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
        sub_docs = []
        for i, doc in enumerate(docs):
            _id = doc_ids[i]
            _sub_docs = child_text_splitter.split_documents([doc])
            for _doc in _sub_docs:
                _doc.metadata[id_key] = _id
            sub_docs.extend(_sub_docs)
        retriever.vectorstore.add_documents(sub_docs)
        retriever.docstore.mset(list(zip(doc_ids, docs)))
        MultiVector_retriever=copy.copy(retriever)
        pass
    elif method[0] == 'Parent_Document_Retriever' and PDR_retriever==None:
        PDR_retriever=False
        loaders=[ PyPDFLoader("../try/2307.03109.pdf")
         ,PyPDFLoader("../try/2307.03109_1.pdf")]
        docs = []
        for l in loaders:
            docs.extend(l.load())
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
        vectorstore = Chroma(
            collection_name="full_documents",
            embedding_function=OpenAIEmbeddings()
        )
        store = InMemoryStore()
        retriever = ParentDocumentRetriever(
            vectorstore=vectorstore, 
            docstore=store, 
            child_splitter=child_splitter,
        )
        retriever.add_documents(docs, ids=None)
        PDR_retriever=copy.copy(retriever)


    if method[0] == 'MultiQueryRetriever':
        while not isinstance(retriever_from_llm,MultiQueryRetriever):
            time.sleep(1)
        docs = retriever_from_llm.get_relevant_documents(query=input)
        res=f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])
        pass
    elif method[0] == 'Contextual_compression':
        while not isinstance(compression_retriever,ContextualCompressionRetriever):
            time.sleep(1)
        docs = compression_retriever.get_relevant_documents(input)
        res=f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])
        pass
    elif method[0] == 'Ensemble_Retriever':
        while not isinstance(ensemble_retriever,EnsembleRetriever):
            time.sleep(1)
        docs = ensemble_retriever.get_relevant_documents(input)
        res=f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])
        pass
    elif method[0] == 'MultiVector_Retriever':
        while not isinstance(MultiVector_retriever,MultiVectorRetriever):
            time.sleep(1)
        docs=MultiVector_retriever.vectorstore.similarity_search(input)
        res=f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])
        pass
    elif method[0] == 'Parent_Document_Retriever':
        while not isinstance(PDR_retriever,ParentDocumentRetriever):
            time.sleep(1)
        docs=PDR_retriever.vectorstore.similarity_search(input)
        res=f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])
    if res=='':
        res='No result!'
    return res

def retriever_compare(input: str, state: ExperimentState) -> MultimodalOutput:
    res=""
    if state.current_variations['retriever_name']:
        res=retriever_method(input,state.current_variations['retriever_name'])
    result=MultimodalOutput(
        text_output=res
    )

    return result

