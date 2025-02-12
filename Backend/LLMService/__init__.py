from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import shutil
from typing import Dict, List, Optional
from langchain_core.documents import Document
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
    TextSplitter,
    TokenTextSplitter,
)

from dotenv import load_dotenv
import os
load_dotenv(dotenv_path='.env', override=True)

base_url = os.getenv('BASE_URL')
embed_model = os.getenv('EMBED_MODEL')

embeddings = OpenAIEmbeddings(
            base_url=base_url, 
            model=embed_model,
            # critical for LM studio mod
            check_embedding_ctx_length=False
)

class LLM:
    def __init__(self, model: str, purpose: str):
        self.purpose = purpose # store_name
        self.model = ChatOpenAI(base_url=base_url, model=model)
        
    def _query_vector_store(self, query: str) -> List[Document]:
        pass
        
    def add_document(self, document_source: str, source_type: str) -> None:
        pass
    
    def invoke(self, query) -> str:
        relevant_docs = self._query_vector_store(query)
        combined_input = (
            "This is the question for you: "
            + query
            + "\n\nPlease provide an answer String suitable for Python uses that only contains the answer to the question and nothing else. You can also provide a list of string answers suitale for Python uses."
            )
        messages = [
            SystemMessage(content="You are a helpful assistant about " + self.purpose),
            HumanMessage(content=combined_input),
        ]
        result = self.model.invoke(messages)
        return result.content