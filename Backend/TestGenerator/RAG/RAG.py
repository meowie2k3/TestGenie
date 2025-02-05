from dotenv import load_dotenv
import os
load_dotenv(dotenv_path='.env', override=True)

base_url = os.getenv('BASE_URL')
embed_model = os.getenv('EMBED_MODEL')

# print(base_url)
# print(embed_model)

from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
    TextSplitter,
    TokenTextSplitter,
)
from langchain_core.documents import Document
from typing import Dict, List, Optional
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import shutil

current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "db")

# embed model
embeddings = OpenAIEmbeddings(
        base_url=base_url, 
        model=embed_model,
        # critical for LM studio mod
        check_embedding_ctx_length=False
    ) 

# Function to create and persist vector store
def _create_vector_store(docs, store_name, is_overwrite=False):
    persistent_directory = os.path.join(db_dir, store_name)
    # delete the directory if it exists and needed
    if is_overwrite and os.path.exists(persistent_directory):
        shutil.rmtree(persistent_directory)
        
    if not os.path.exists(persistent_directory):
        print(f"\n--- Creating vector store {store_name} ---")
        db = Chroma.from_documents(
            docs, embeddings, persist_directory=persistent_directory
        )
        print(f"--- Finished creating vector store {store_name} ---")
    else:
        print(
            f"Vector store {store_name} already exists. No need to initialize.")
        
def _load_document(file_path):
    file_path = os.path.join(current_dir, file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"The file {file_path} does not exist. Please check the path."
        )
    loader = TextLoader(file_path=file_path, autodetect_encoding=True)
    return loader.load()

def _split_document(documents, chunk_size=1000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

# just in case
class CustomTextSplitter(TextSplitter):
    def split_text(self, text):
        # Custom logic for splitting text
        return text.split("\n\n")  # Example: split by paragraphs


# Function to query a vector store
def query_vector_store(store_name, query, docs_num=1) -> List[Document]:
    persistent_directory = os.path.join(db_dir, store_name)
    if os.path.exists(persistent_directory):
        print(f"\n--- Querying the Vector Store {store_name} ---")
        db = Chroma(
            persist_directory=persistent_directory, embedding_function=embeddings
        )
        retriever = db.as_retriever(
            # search_type="similarity",
            # search_kwargs={"k": docs_num},
            # search_type="mmr",
            # search_kwargs={"k": docs_num, "fetch_k": 20, "lambda_mult": 0.5}
            search_type="similarity_score_threshold",
            search_kwargs={'score_threshold': 0.4}
        )
        relevant_docs = retriever.invoke(query)
        return relevant_docs
    else:
        raise FileNotFoundError(
            f"The vector store {store_name} does not exist. Please create it first."
        )
        
        
if __name__ == "__main__":
    # Load the documents
    docs = _load_document("Documents/romeo_and_juliet.txt")
    # # Split the documents into chunks
    chunks = _split_document(docs)
    # # Create and persist the vector store
    _create_vector_store(chunks, "romeo_and_juliet", is_overwrite=True)
    # Query the vector store
    store_name = "romeo_and_juliet"
    query = "How did Juliet die?"
    relevant_docs = query_vector_store(store_name, query)
    
    print(f"\n--- Relevant Documents for {store_name} ---")
    for i, doc in enumerate(relevant_docs, 1):
        print(f"Document {i}:\n{doc.page_content}\n")
        if doc.metadata:
            print(f"Source: {doc.metadata.get('source', 'Unknown')}\n")