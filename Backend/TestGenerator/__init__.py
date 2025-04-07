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

class Test_Generator:
    def __init__(self) -> None:
        if load_dotenv(override=True) == False:
            raise Exception("Failed to load .env file")
        base_url = os.getenv('BASE_URL')
        model_name = os.getenv('TG_LLM_MODEL')
        embed_model = os.getenv('EMBED_MODEL')
        self.model = ChatOpenAI(base_url=base_url, model=model_name, temperature=0)
        self.embeddings = OpenAIEmbeddings(
            base_url=base_url, 
            model=embed_model,
            # critical for LM studio mod
            check_embedding_ctx_length=False
        )
        # load vector store process
        self.store_names = self._getStoreList()
        for store_name, doc_name in self.store_names.items():
            if not self._check_if_vector_store_exists(store_name):
                docs = self._load_document(doc_name)
                chunks = self._split_document(docs)
                self._create_vector_store(chunks, store_name)
        dbs = []
        for store_name in self.store_names.keys():
            dbs.append(Chroma(persist_directory=os.path.join(db_dir, store_name), embedding_function=self.embeddings))
        
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
                        'score_threshold': 0.2,
                        'k': 1,
                    }
                )
            )
        self._agent_init()
        
    def generate_test_case(
        self,
        function_name_and_arguments: str,
        prediction: str,
    ) -> str:
        response = self.agent_executor.invoke(
            {
                "input": "Generate a test case for the function based on the prediction and the chat history.",
                "function_name_and_arguments": function_name_and_arguments,
                "prediction": prediction,
            }
        )
        return response.get("output", "No output generated.")

        
    def _agent_init(self) -> None:
        def _wrap_rag_tool(rag_chain):
            def wrapped(input_data):
                if isinstance(input_data, str):
                    input_data = {"input": input_data}
                return rag_chain.invoke({
                    "input": input_data.get("input", ""),
                    "prediction": input_data.get("prediction", ""),
                    "function_name_and_arguments": input_data.get("function_name_and_arguments", ""),
                })
            return wrapped

        # 1. Contextualizer prompt
        contextualize_q_system_prompt = (
            "Given the prediction of what the function does, "
            "formulate a statement that can be used to query the model for useful reference. "
            "Do NOT include the function name and function arguments in the statement. "
            "The statement should be a question that can be used to query the model for useful reference."
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("prediction"),
                ("human", "{input}"),
            ]
        )

        # 2. Wrap each retriever with history-aware logic
        history_aware_retrievers = [
            create_history_aware_retriever(self.model, retriever, contextualize_q_prompt)
            for retriever in self.retrievers
        ]

        # 3. Test generation system prompt
        tg_system_prompt = (
            "You are a Test Generator system.\n"
            "You are given the following:\n"
            "- Function name and arguments: {function_name_and_arguments}\n"
            "- A description of what the function does: {prediction}\n\n"
            "You need to generate a Dart test case file for the function based on the chat history and the prediction.\n"
            "Include:\n"
            "- Test function(s) with meaningful names\n"
            "- Comments explaining the test logic\n"
            "- A comment-based evaluation of test coverage at the end of the test case\n"
            "\n{context}"
        )

        tg_prompt = ChatPromptTemplate.from_messages([
            ("system", tg_system_prompt),
            ("human", "{input}"),
        ])

        tg_chain = create_stuff_documents_chain(self.model, tg_prompt)

        # 4. Create RAG chains
        rag_chains = [
            create_retrieval_chain(retriever, tg_chain)
            for retriever in history_aware_retrievers
        ]

        # 5. Tool setup using the safe wrapper
        react_docstore_prompt = hub.pull("hwchase17/react")

        tools = []
        store_names = list(self.store_names.keys())

        for i, store_name in enumerate(store_names):
            rag_chain = rag_chains[i]

            def make_tool_func(chain):
                return lambda input_str, **kwargs: chain.invoke({
                    "input": input_str,
                    "prediction": kwargs.get("prediction", ""),
                    "function_name_and_arguments": kwargs.get("function_name_and_arguments", ""),
                })

            tools.append(
                Tool(
                    name=f"Get Flutter test framework syntax from {store_name}",
                    func=make_tool_func(rag_chain),
                    description=f"Retrieve documents from the vector store {store_name}",
                )
            )


        # 6. Build the agent
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

        
    def _safe_rag_invoke(self, chain, input_data):
        try:
            if not isinstance(input_data, dict):
                input_data = {"input": input_data}

            input_data.setdefault("prediction", "The function behavior is unknown.")
            input_data.setdefault("function_name_and_arguments", "UnnamedFunction()")

            return chain.invoke(input_data)
        except Exception as e:
            return f"[Error during retrieval] {str(e)}"
        
    def _wrap_rag_tool(self, rag_chain):
        def wrapped(input_data):
            if isinstance(input_data, str):
                input_data = {"input": input_data}
            return self._safe_rag_invoke(
                rag_chain,
                {
                    "input": input_data.get("input", ""),
                    "function_name_and_arguments": input_data.get("function_name_and_arguments", ""),
                    "prediction": input_data.get("prediction", ""),
                }
            )
        return wrapped

        
    def _getStoreList(self) -> dict:
        """
        This function read all files in docs_dir then return a dict:
        {
            "file_name": "file_name.extension",
        }
        Ex:
        {
            "flutter_tutorial": "flutter_tutorial.pdf",
        }
        """
        files = os.listdir(docs_dir)
        store_list = {}
        for file in files:
            # check if file extension is supported
            store_name, file_extension = os.path.splitext(file)
            if file_extension not in file_loader_map:
                print(f"File {file} is not supported")
                continue
            # check if file name is valid
            if not store_name.isidentifier():
                print(f"File {file} is not valid")
                continue
            store_list[store_name] = file
        return store_list
    
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
    tg = Test_Generator()
    # print(tg.store_names)
    function_name_and_arguments = "addTwoNumbers(int a, int b)"
    prediction = """
        The function `addTwoNumbers` takes two integer parameters, `a` and `b`, and returns their sum. Here's how you can implement this in Dart:
        
        ```dart
        int addTwoNumbers(int a, int b) {
        return a + b;
        }
        ```
        
        This function simply adds the two input integers and returns the result.
    """
    print(tg.generate_test_case(function_name_and_arguments, prediction))