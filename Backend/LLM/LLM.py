from dotenv import load_dotenv
import os
load_dotenv(dotenv_path='.env', override=True)

base_url = os.getenv('BASE_URL')
model_name = os.getenv('LLM_MODEL')

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(base_url=base_url, model=model_name)

def invoke(query, relevant_docs = None) -> str:
    
    combined_input = (
        "Here are some documents that might help answer the question: "
        + query
        + "\n\nRelevant Documents:\n"
        + "\n\n".join([doc.page_content for doc in relevant_docs])
        + "\n\nPlease provide an answer based only on the provided documents. If the answer is not found in the documents, respond with 'I'm not sure'."
    )
    
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=combined_input),
    ]
    result = model.invoke(messages)
    return result.content