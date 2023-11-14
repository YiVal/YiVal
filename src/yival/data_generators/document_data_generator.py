"""
This module provides an implementation for generating question data from documents.
Supported types of document sources include:
    - plain text
    - unstructured files: Text, PDF, PowerPoint, HTML, Images, 
        Excel spreadsheets, Word documents, Markdown, etc.
    - documents from Google Drive (provide file id).
Currently support only one document a time.
"""
import ast
import asyncio
import csv
import os
import pickle
import re
from typing import Any, Dict, Iterator, List

from langchain.document_loaders import UnstructuredFileLoader, UnstructuredFileIOLoader, GoogleDriveLoader, GCSFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from tqdm import tqdm

from yival.common import utils
from yival.common.model_utils import llm_completion
from yival.data_generators.base_data_generator import BaseDataGenerator
from yival.schemas.data_generator_configs import DocumentDataGeneratorConfig
from yival.schemas.model_configs import Request

PROMPT_TEMPLATE = """
    Context information is below.
    ---------------------
    {CONTEXT}
    ---------------------
    Please do not introduce priori knowledge, 
    only consider the content of the previous context information, 
    generate 5 questions based on the following query. 
    Answer ONLY a python list containing all the questions generated.
    Keep your output crisp, with only a '[]' bracketed list.
    {QUERY}
"""

class DocumentDataGenerator(BaseDataGenerator):
    config: DocumentDataGeneratorConfig
    default_config: DocumentDataGeneratorConfig = DocumentDataGeneratorConfig(
        prompt = PROMPT_TEMPLATE,
        document = "",
        source = "text",
        num_questions_per_chunk = 5,
        text_question_template = None,
        document_chunk_size = 512,
        number_of_examples = 1,
        question_gen_query = f"You are a Teacher/Professor. Your task is to setup \
                        5 questions for an upcoming quiz/examination. The questions \
                        should be diverse in nature across the document. Restrict \
                        the questions to the context information provided."
    )

    def __init__(self, config: DocumentDataGeneratorConfig):
        super().__init__(config)
        self.config = config
        
    def load_document(self, source: str, document: str) -> Document:
        if source == 'text':
            doc = Document(page_content = document)
            return doc
        elif source == 'file':
            loader = UnstructuredFileLoader(document)
            doc = loader.load()[0]
            return doc
        elif source == 'drive':
            loader = GoogleDriveLoader(file_ids=[document],
                                       file_loader_cls=UnstructuredFileIOLoader,
                                       file_loader_kwargs={"mode": "elements"},)  
            doc = loader.load()[0]
            return doc
        else:
            return None

    def get_doc_context(self, doc: Document, chunk_size: int) -> List[str]:
        # Split Document into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size) 
        splits = splitter.split_documents([doc])
        
        # Generate contexts from splits
        contexts = [str(split.page_content) for split in splits]
        return contexts

    def prepare_messages(self) -> List[Dict[str, Any]]:
        """Prepare the messages for GPT API based on configurations."""
        if not self.config.prompt:
            self.config.prompt = PROMPT_TEMPLATE
        document = self.load_document(self.config.source, self.config.document)
        if document:
            contexts = self.get_doc_context(document, self.config.chunk_size)
        else:
            raise TypeError
        
        contents = []
        for context in contexts:
            content = "Context information is below.\n---------------------\n\n" + context + "\n"
            content = content + "---------------------\nPlease do not introduce priori knowledge,\n"
            content = content + "only consider the content of the previous context information,\n generate "
            content = content + str(self.config.num_questions_per_chunk) + " questions based on the following query."
            content = content + "Answer ONLY a python list containing all the questions generated.\n"
            content = content + "Context information is below.\n---------------------\n\n"
            content = content + "Keep your output crisp, with only a '[]' bracketed list.\n"
            content = content + self.config.question_gen_query + "\n"
            if self.config.text_question_template:
                content = content + "Please generate the questions according to the following template:\n" + self.config.text_question_template + "\n"
            contents.append(content)
        return [{"role": "user", "content": content} for content in contents]

    def process_output(
        self, output_content: str, all_data: List[List[str]],
        chunk: List[List[str]]
    ):
        """Process the output from GPT API and update data lists."""
        all_data.append(eval(output_content))
        chunk.append(eval(output_content))

    def generate_examples(self) -> Iterator[List[List[str]]]:
        all_data: List[List[str]] = []
        # Loading data from existing path if exists
        if self.config.output_path and os.path.exists(self.config.output_path):
            with open(self.config.output_path, 'rb') as file:
                all_data = pickle.load(file)
                for i in range(0, len(all_data), self.config.chunk_size):
                    yield all_data[i:i + self.config.chunk_size]
            return
        
        chunk: List[List[str]] = []

        while len(all_data) < self.config.number_of_examples:
            messages = self.prepare_messages()
            message_batches = [
                messages
            ] * (self.config.number_of_examples - len(all_data))
            with tqdm(
                total=self.config.number_of_examples,
                desc="Generating Examples",
                unit="example"
            ) as pbar:
                responses = asyncio.run(
                    utils.parallel_completions(
                        message_batches,
                        self.config.model_name,
                        self.config.max_token,
                        pbar=pbar
                    )
                )
            for r in responses:
                self.process_output(
                    r["choices"][0]["message"]["content"], all_data, chunk
                )
            if chunk and len(chunk) >= self.config.chunk_size:
                yield chunk
                chunk = []
        if self.config.output_path:
            with open(self.config.output_path, 'wb') as file:
                pickle.dump(all_data, file)
                print(
                    f"Data succesfully generated and saved to {self.config.output_path}"
                )
        if self.config.output_csv_path:
            with open(self.config.output_csv_path, 'w', newline='') as csvfile:
                rows = [
                    BaseDataGenerator.input_data_to_csv_row(data)
                    for data in all_data
                ]
                header = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=header)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
                print(
                    f"Data succesfully generated and saved to {self.config.output_csv_path}"
                )
        if chunk:
            yield chunk


BaseDataGenerator.register_data_generator(
    "document_data_generator", DocumentDataGenerator,
    DocumentDataGeneratorConfig
)


def main():
    import time
    start_time = time.time()
    generator = DocumentDataGenerator(
        DocumentDataGenerator.default_config
    )
    res = generator.generate_examples()

    for d in res:
        print(d)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
