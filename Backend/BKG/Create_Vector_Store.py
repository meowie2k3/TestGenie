from dotenv import load_dotenv
import os
load_dotenv()

base_url = os.getenv('BASE_URL')
embed_model = os.getenv('EMBED_MODEL')

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


# Define the directory containing the text file and the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "knowledge", "odyssey.txt")
persistent_directory = os.path.join(current_dir, "db", "chroma_db")

# Check if the Chroma vector store already exists
if not os.path.exists(persistent_directory):
    print("Persistent directory does not exist. Initializing vector store...")

    # Ensure the text file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"The file {file_path} does not exist. Please check the path."
        )

    # Read the text content from the file
    loader = TextLoader(file_path=file_path, autodetect_encoding=True)
    documents = loader.load()

    # Split the document into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    # chunk_size: The number of characters in each chunk
    # chunk_overlap: The number of characters that overlap between
    docs = text_splitter.split_documents(documents)

    # Display information about the split documents
    print("\n--- Document Chunks Information ---")
    print(f"Number of document chunks: {len(docs)}")
    # print(f"Sample chunk:\n{docs[0].page_content}\n")
    
    # Create embeddings
    print("\n--- Creating embeddings ---")
    embeddings = OpenAIEmbeddings(
        base_url=base_url, 
        model=embed_model,
        # critical for LM studio mod
        check_embedding_ctx_length=False
    ) 
    
    print("\n--- Finished creating embeddings ---")

    # Create the vector store and persist it automatically
    print("\n--- Creating vector store ---")

    db = Chroma.from_documents(
        docs, embeddings, persist_directory=persistent_directory)
    
    print("\n--- Finished creating vector store ---")

else:
    print("Vector store already exists. No need to initialize.")
    