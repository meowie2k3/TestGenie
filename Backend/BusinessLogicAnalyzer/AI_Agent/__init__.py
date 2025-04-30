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

from langchain_chroma import (
    Chroma
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
        model_name = os.getenv('BLA_LLM_MODEL')
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
            # "dart_programming_tutorial": "dart_programming_tutorial.pdf",
            # "DartLangSpecDraft": "DartLangSpecDraft.pdf",
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
        self.retrievers = []
        for db in dbs:
            self.retrievers.append(
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
        self._agent_init()
        
        
        
    def generate_BLA_prediction(
        self, 
        source_code: str, 
        chat_history: list
    ) -> str:
        # First use the agent to analyze the code
        response = self.agent_executor.invoke(
            {
                "input": source_code,
                "chat_history": chat_history,
            }
        )
        
        # Then use a direct call to the LLM to structure the output properly
        structured_prompt = (
            "Based on the following analysis of code, create a structured response with the following sections:\n"
            "1. Brief explanation of what the code does\n"
            "2. Testability assessment\n"
            "3. TESTING SCENARIOS in the exact format shown below:\n\n"
            "TESTING SCENARIOS:\n"
            "1. [Descriptive Test Name]: Verify that [functionality]. Input: [specific input values]. Expected: [specific output/behavior].\n"
            "2. [Descriptive Test Name]: Verify that [functionality]. Input: [specific input values]. Expected: [specific output/behavior].\n"
            "3. [Descriptive Test Name]: Verify that [functionality]. Input: [specific input values]. Expected: [specific output/behavior].\n\n"
            "For test names, use descriptive names that clearly indicate the purpose of the test, such as:\n"
            "- 'ValidPalindromeCheck' instead of 'Scenario Name'\n"
            "- 'EmptyStringHandling' instead of generic names\n"
            "- 'BoundaryConditionTest' for edge cases\n"
            "- 'SpecialCharactersTest' for specific input types\n\n"
            "Include at least 4-5 different test scenarios covering normal cases, edge cases, and special conditions.\n"
            "Analysis to structure: " + response["output"]
        )
        
        structured_response = self.model.invoke(structured_prompt)
        return structured_response.content
            
        
        
    def _agent_init(self) -> None:
        contextualize_q_system_prompt = (
            "Given a chat history, user request and the latest piece of user source code, "
            "which might reference context in the chat history, "
            "formulate a statement that can be used to query the model for useful reference."
            "Do NOT include the user request in the query."
            # "DO NOT add the sentence 'Without more context or specific questions about the code, I can't provide a more detailed explanation' in the answer."
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
        
        bla_system_prompt = (
            "You are an AI assistant that analyzes Flutter/Dart source code to identify its business logic for test generation.\n"
            "You can provide helpful answers using available tools.\n"
            "For the given code snippet:\n\n"
            "1. FUNCTION ANALYSIS:\n"
            "   - What is the purpose of this function/class?\n"
            "   - What are the inputs (parameters) and their types?\n"
            "   - What is the expected output (return value) and its type?\n"
            "   - What algorithm or logic does it implement?\n\n"
            "2. TESTABILITY ASSESSMENT:\n"
            "   - Can this code be tested? If yes, what type of test is appropriate (unit/widget/integration)?\n"
            "   - Are there any dependencies that might complicate testing?\n\n"
            "3. TESTING SCENARIOS:\n"
            "   ALWAYS include at least 3-5 specific test scenarios using EXACTLY this format:\n\n"
            "   TESTING SCENARIOS:\n"
            "   1. [Scenario Name]: Verify that [functionality]. Input: [specific input values]. Expected: [specific output/behavior].\n"
            "   2. [Scenario Name]: Verify that [functionality]. Input: [specific input values]. Expected: [specific output/behavior].\n"
            "   3. [Scenario Name]: Verify that [functionality]. Input: [specific input values]. Expected: [specific output/behavior].\n\n"
            "Keep your analysis concise but precise. DO NOT include the source code in your answer.\n"
            "The TESTING SCENARIOS section MUST follow the exact format shown above, with specific input values and expected outputs.\n"
            "If the code's purpose is unclear, make your best inference based on the implementation details.\n"
            "{context}"
        )
        
        bla_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", bla_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        bla_chain = create_stuff_documents_chain(self.model, bla_prompt)
        
        rag_chains = []
        
        for retriever in history_aware_retrievers:
            rag_chains.append(create_retrieval_chain(retriever, bla_chain))
            
        react_docstore_prompt = hub.pull("hwchase17/react")
        
        tools = []
        
        store_names = []
        for store_name, doc_name in self.store_names.items():
            store_names.append(store_name)
        
        for i in range(len(store_names)):
            # print(f"{store_names[i]}")
            tools.append(
                Tool(
                    name=f"Get code explaination from {store_names[i]}",
                    func=lambda input, **kwargs: rag_chains[i].invoke(
                        {
                            "input": input, 
                            "chat_history": kwargs.get("chat_history", [])
                        }
                    ),
                    description=f"Retrieve documents from the vector store {store_names[i]}",
                )
            )
            
        agent = create_react_agent(
            llm=self.model,
            tools=tools,
            prompt=react_docstore_prompt,
        )
        
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent, 
            tools=tools, 
            handle_parsing_errors=True, 
            verbose=True,
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
        
        
if __name__ == "__main__":
    ai_agent = AI_Agent()
    # ai_agent.run_test()
    source_code = """
        bool isPalindrome(String str) {
            int left = 0;
            int right = str.length - 1;
            while (left < right) {
                if (str[left] != str[right]) {
                    return false;
                }
                left++;
                right--;
            }
            return true;
        }
    """
    chat_history = []
    response = ai_agent.generate_BLA_prediction(source_code, chat_history)
    print("Bot:", response)