from dotenv import load_dotenv
import os
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

base_url = os.getenv('BASE_URL')

if __name__ == '__main__':
    model = ChatOpenAI(base_url=base_url)
    
    chat_history=[]

    # Set an initial system message (optional)
    system_message = SystemMessage(content="You are a helpful AI assistant.")
    chat_history.append(system_message)  # 
    
    
# Chat loop
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        chat_history.append(HumanMessage(content=query))  # Add user message

        # Get AI response using history
        result = model.invoke(chat_history)
        response = result.content
        chat_history.append(AIMessage(content=response))  # Add AI message

        print(f"AI: {response}")


    print("---- Message History ----")
    print(chat_history)
