from dotenv import load_dotenv
import os
load_dotenv(dotenv_path='.env', override=True)

base_url = os.getenv('BASE_URL')
embed_model = os.getenv('EMBED_MODEL')

# print(base_url)
# print(embed_model)
# exit()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "knowledge", "odyssey.txt")
persistent_directory = os.path.join(current_dir, "db", "chroma_db")

embeddings = OpenAIEmbeddings(
    base_url=base_url, 
    model=embed_model,
    # critical for LM studio mod
    check_embedding_ctx_length=False
)

# Load the existing vector store with the embedding function
db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embeddings
)

# Define the user's question
query = "Who is Odysseus' wife?"

# Retrieve relevant documents based on the query
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    # k: The number of documents to retrieve
    # score_threshold: The minimum similarity score required to retrieve
    search_kwargs={"k": 10, "score_threshold": 0.4},
)
relevant_docs = retriever.invoke(query)

# Display the relevant results with metadata
print("\n--- Relevant Documents ---")
for i, doc in enumerate(relevant_docs, 1):
    print(f"Document {i}:\n{doc.page_content}\n")
    if doc.metadata:
        print(f"Source: {doc.metadata.get('source', 'Unknown')}\n")