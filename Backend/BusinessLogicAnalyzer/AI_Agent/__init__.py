from dotenv import load_dotenv
import os


from langchain import hub
import shutil
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
    create_structured_chat_agent,
)
from langchain_core.messages import (
    AIMessage, 
    HumanMessage, 
    SystemMessage,
)
from langchain.memory import (
    ConversationBufferMemory,
)
from langchain.chains import (
    create_history_aware_retriever, 
    create_retrieval_chain,
)
from langchain.chains.combine_documents import (
    create_stuff_documents_chain,
)
from langchain_community.vectorstores import (
    Chroma,
)

from langchain_core.documents import (
    Document,
)

from typing import (
    Dict, 
    List, 
    Optional,
)

from langchain_community.document_loaders import (
    TextLoader,
    Docx2txtLoader,
    PyPDFLoader,
)

from langchain.text_splitter import (
    SentenceTransformersTokenTextSplitter,
)

from langchain_core.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder,
)
from langchain_core.tools import (
    Tool,
)
from langchain_openai import (
    ChatOpenAI, 
    OpenAIEmbeddings,
)

########################## trash section #############################
def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    import datetime  # Import datetime module to get current time

    now = datetime.datetime.now()  # Get current time
    return now.strftime("%I:%M %p")

def search_wikipedia(query):
    """Searches Wikipedia and returns the summary of the first result."""
    from wikipedia import summary

    try:
        # Limit to two sentences for brevity
        return summary(query, sentences=2)
    except:
        return "I couldn't find any information on that."

#######################################################################

currentDir = os.path.dirname(os.path.realpath(__file__))
db_dir = os.path.join(currentDir, 'db')
docs_dir = os.path.join(currentDir, 'docs')

class AI_Agent:
    def __init__(self) -> None:
        if load_dotenv(override=True) == False:
            raise Exception("Failed to load .env file")
        self.base_url = os.getenv('BASE_URL')
        self.model_name = os.getenv('LLM_MODEL')
        self.embed_model = os.getenv('EMBED_MODEL')
        self.model = ChatOpenAI(base_url=self.base_url, model=self.model_name, temperature=0)
        self.embeddings = OpenAIEmbeddings(
            base_url=self.base_url, 
            model=self.embed_model,
            # critical for LM studio mod
            check_embedding_ctx_length=False
        )
        # load vector store
        
        
    # Function to create and persist vector store
    def _create_vector_store(self, docs, store_name, is_overwrite=False):
        persistent_directory = os.path.join(db_dir, store_name)
        # delete the directory if it exists and needed
        if is_overwrite and os.path.exists(persistent_directory):
            shutil.rmtree(persistent_directory) # remove the directory
            
        if not os.path.exists(persistent_directory):
            print(f"\n--- Creating vector store {store_name} ---")
            db = Chroma.from_documents(
                docs, self.embeddings, persist_directory=persistent_directory
            )
            print(f"--- Finished creating vector store {store_name} ---")
        else:
            print(
                f"Vector store {store_name} already exists. No need to initialize.")
    
    def _load_document(self, doc_name) -> List[Document]:
        file_path = os.path.join(docs_dir, doc_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"_load_document: The file {file_path} does not exist. Please check the path."
            )
        loader = TextLoader(file_path=file_path, autodetect_encoding=True)
        return loader.load()
    
    def _split_document(documents, chunk_size=1000, chunk_overlap=100):
        text_splitter = SentenceTransformersTokenTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        return text_splitter.split_documents(documents)
    
    def query_vector_store(self, query, store_name) -> List[Document]:
        persistent_directory = os.path.join(db_dir, store_name)
        if os.path.exists(persistent_directory):
            print(f"\n--- Querying the Vector Store {store_name} ---")
            db = Chroma(
                persist_directory=persistent_directory, 
                embedding_function=self.embeddings
            )
            retriever = db.as_retriever(
                # search_type="similarity",
                # search_kwargs={"k": docs_num},
                # search_type="mmr",
                # search_kwargs={"k": docs_num, "fetch_k": 20, "lambda_mult": 0.5}
                search_type="similarity_score_threshold",
                search_kwargs={
                    'score_threshold': 0.4,
                    'k': 3,
                }
            )
            relevant_docs = retriever.invoke(query)
            return relevant_docs
        else:
            raise FileNotFoundError(
                f"query_vector_store: The vector store {store_name} does not exist. Please create it first."
            )

    def run_test(self) -> None:
        tools = [
            Tool(
                name="Time",  # Name of the tool
                func=get_current_time,  # Function that the tool will execute
                # Description of the tool
                description="Useful for when you need to know the current time",
            ),
            Tool(
                name="Wikipedia",
                func=search_wikipedia,
                description="Useful for when you need to know information about a topic.",
            ),
        ]
        
        prompt = hub.pull("hwchase17/structured-chat-agent")
        
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True)
        
        agent = create_structured_chat_agent(
            llm=self.model,
            tools=tools,
            prompt=prompt,
        )
        
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=True,
            memory=memory,  # Use the conversation memory to maintain context
            handle_parsing_errors=True,  # Handle any parsing errors gracefully
        )
        
        initial_message = "You are an AI assistant that can provide helpful answers using available tools.\nIf you are unable to answer, you can use the following tools: Time and Wikipedia."
        memory.chat_memory.add_message(SystemMessage(content=initial_message))
        
        # Chat Loop to interact with the user
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break

            # Add the user's message to the conversation memory
            memory.chat_memory.add_message(HumanMessage(content=user_input))

            # Invoke the agent with the user input and the current chat history
            response = agent_executor.invoke({"input": user_input})
            print("Bot:", response["output"])

            # Add the agent's response to the conversation memory
            memory.chat_memory.add_message(AIMessage(content=response["output"]))
        
        
        
if __name__ == "__main__":
    ai_agent = AI_Agent()
    ai_agent.run_test()