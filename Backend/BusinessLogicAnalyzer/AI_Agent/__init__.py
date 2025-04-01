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

file_loader_map = {
    ".docx": Docx2txtLoader,
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
}

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

currentDir = os.path.dirname(os.path.realpath(__file__))
db_dir = os.path.join(currentDir, 'db')
docs_dir = os.path.join(currentDir, 'docs')

class AI_Agent:
    def __init__(self) -> None:
        if load_dotenv(override=True) == False:
            raise Exception("Failed to load .env file")
        base_url = os.getenv('BASE_URL')
        model_name = os.getenv('LLM_MODEL')
        embed_model = os.getenv('EMBED_MODEL')
        self.model = ChatOpenAI(base_url=base_url, model=model_name, temperature=0)
        self.embeddings = OpenAIEmbeddings(
            base_url=base_url, 
            model=embed_model,
            # critical for LM studio mod
            check_embedding_ctx_length=False
        )
        # load vector store
        self.store_names = {
            "dart_programming_tutorial": "dart_programming_tutorial.pdf",
            "DartLangSpecDraft": "DartLangSpecDraft.pdf",
            "flutter_tutorial": "flutter_tutorial.pdf",
        }
        for store_name, doc_name in self.store_names.items():
            if not self._check_if_vector_store_exists(store_name):
                docs = self._load_document(doc_name)
                chunks = self._split_document(docs)
                self._create_vector_store(chunks, store_name)
                
        dbs = []
        for store_name in self.store_names:
            dbs.append(
                Chroma(persist_directory=os.path.join(db_dir, store_name),
                       embedding_function=self.embeddings)
            )
        retrievers = []
        for db in dbs:
            retrievers.append(
                db.as_retriever(
                    # search_type="similarity",
                    # search_kwargs={"k": docs_num},
                    # search_type="mmr",
                    # search_kwargs={"k": docs_num, "fetch_k": 20, "lambda_mult": 0.5}
                    search_type="similarity_score_threshold",
                    search_kwargs={
                        'score_threshold': 0.4,
                        'k': 1,
                    }
                )
            )
            
        
        
    def generate_prediction(self, source_code: str, chat_history: list) -> str:
        contextualize_q_system_prompt = (
            "Given a chat history, user request and the latest piece of user source code "
            "which might reference context in the chat history, "
            "formulate a statement that can be used to query the model for useful reference."
            "Do NOT include the user request in the query."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        # Create a history-aware retriever
        # This uses the LLM to help reformulate the question based on chat history
        history_aware_retrievers = [] 
        
        for retriever in self.retrievers:
            history_aware_retrievers.append(
                create_history_aware_retriever(
                    self.model, retriever, contextualize_q_prompt
                )
            )
        
        pass
    
    
        
    # Function to create and persist vector store
    def _create_vector_store(self, docs, store_name, is_overwrite=False) -> None:
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
    
    def _load_document(self, doc_name):
        file_path = os.path.join(docs_dir, doc_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"_load_document: The file {file_path} does not exist. Please check the path."
            )
        file_extension = os.path.splitext(file_path)[1]
        # check if the file extension is supported
        if file_extension not in file_loader_map:
            raise Exception(f"_load_document: Unsupported file extension: {file_extension} for file: {file_path}")
        loader = PyPDFLoader(file_path=file_path)
        return loader.load()
    
    def _split_document(self, documents, chunk_size=1000, chunk_overlap=100):
        text_splitter = SentenceTransformersTokenTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        return text_splitter.split_documents(documents)
    
    def _check_if_vector_store_exists(self, store_name) -> bool:
        persistent_directory = os.path.join(db_dir, store_name)
        return os.path.exists(persistent_directory)

    def run_test(self) -> None:
        prompt = hub.pull("hwchase17/react")
        
        tools = []
        for store_name in self.store_names:
            tools.append(
                Tool(
                    name=store_name + "_retriever",
                    func=lambda query: self.query_vector_store(query, store_name),
                    description=f"Retrieve documents from the vector store {store_name}",
                )
            )
        
        bla_system_prompt = (
            "You are an AI assistant that can analyze business logic (what does each module - function do) from Flutter - Dart source code to generate unit test later.\n"
            "You can provide helpful answers using available tools.\n"
            "You will be given a Flutter - Dart source code snippet and you need to analyze the business logic of the code.\n"
            "If you are unable to answer or not sure about the syntax, you can use provided Flutter - Dart document retrieval tools.\n\n"
        )
        
        bla_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", bla_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        agent = create_structured_chat_agent(
            llm=self.model,
            tools=tools,
            prompt=bla_prompt,
        )
        
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
        )
        
        source_code = """
        void main() {
            runApp(MyApp());
        }
        """
        
        response = agent_executor.invoke({'input': source_code})
        print("Bot:", response["output"])
        
        
if __name__ == "__main__":
    ai_agent = AI_Agent()
    ai_agent.run_test()