from dotenv import load_dotenv
import os
from langchain import hub
import shutil
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
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
from langchain.text_splitter import (
    SentenceTransformersTokenTextSplitter,
)
from langchain_core.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.tools import (
    Tool,
)
from langchain_openai import (
    ChatOpenAI, 
    OpenAIEmbeddings,
)
import re

currentDir = os.path.dirname(os.path.realpath(__file__))
db_dir = os.path.join(currentDir, 'db')
docs_dir = os.path.join(currentDir, 'docs')

file_loader_map = {
    ".docx": Docx2txtLoader,
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
}

class Test_Generator:
    def __init__(self) -> None:
        if load_dotenv(override=True) == False:
            raise Exception("Failed to load .env file")
        base_url = os.getenv('BASE_URL')
        model_name = os.getenv('TG_LLM_MODEL')
        embed_model = os.getenv('EMBED_MODEL')
        self.model = ChatOpenAI(base_url=base_url, model=model_name, temperature=0) # type: ignore
        self.embeddings = OpenAIEmbeddings(
            base_url=base_url, 
            model=embed_model, # type: ignore
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
        
        self.dbs = []
        for store_name in self.store_names.keys():
            self.dbs.append(Chroma(persist_directory=os.path.join(db_dir, store_name), embedding_function=self.embeddings))
        
        self.retrievers = []
        for db in self.dbs:
            self.retrievers.append(
                db.as_retriever(
                    search_type="similarity_score_threshold",
                    search_kwargs={
                        'score_threshold': 0.2,
                        'k': 1,
                    }
                )
            )
        
    def generate_test_case(
        self,
        package_name: str,
        code_location: str,
        function_name_and_arguments: str,
        prediction: str,
    ) -> str:
        """
        Generate a test case for a function based on the prediction and code details.
        
        Args:
            package_name: Name of the package (for import statements)
            code_location: Location of the code file to test (path within the package)
            function_name_and_arguments: Function signature with arguments
            prediction: Description of what the function does
            
        Returns:
            Generated test case as a string (clean Dart source code only)
        """
        try:
            # Generate the test case directly
            raw_output = self._generate_clean_test(package_name, code_location, function_name_and_arguments, prediction)
            
            # Clean up any markdown formatting that might be present
            cleaned_output = self._clean_code_output(raw_output)
            
            return cleaned_output
        except Exception as e:
            print(f"Error generating test case: {str(e)}")
            return f"// Error generating test case: {str(e)}"
        
    def fix_generated_code(
        self, 
        error_message: str,
        current_test_code: str,
        prediction: str,
    ): 
        
        pass
        
    def _clean_code_output(self, raw_output: str) -> str:
        """
        Clean the raw output to remove any markdown or formatting characters.
        
        Args:
            raw_output: The raw output from the LLM
            
        Returns:
            Cleaned code ready to be used directly
        """
        # Remove markdown code block markers
        clean_code = re.sub(r'```dart|```', '', raw_output)
        
        # Remove any HTML-like comments that might be present
        clean_code = re.sub(r'/\*\s*Test Coverage Evaluation:', '// Test Coverage Evaluation:', clean_code)
        clean_code = re.sub(r'\*/', '', clean_code)
        
        # Ensure proper imports 
        if "import 'package:test/test.dart';" not in clean_code:
            # Add test package import if missing
            import_section = clean_code.split('\n\n')[0]
            clean_code = clean_code.replace(import_section, 
                                          import_section + "\nimport 'package:test/test.dart';")
        
        return clean_code.strip()
        
    def _generate_clean_test(self, package_name: str, code_location: str, function_name_and_arguments: str, prediction: str) -> str:
        """
        Generate a clean test case with just the Dart source code and coverage evaluation comment.
        
        Args:
            package_name: Name of the package (for import statements)
            code_location: Location of the code file to test (path within the package)
            function_name_and_arguments: Function signature with arguments
            prediction: Description of what the function does
            
        Returns:
            Clean Dart source code with coverage evaluation comment
        """
        clean_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are a Test Generator system specialized in Dart test cases.\n"
             "Generate a clean Dart test file with NO formatting markers, just the raw code that can be directly saved to a .dart file.\n\n"
             "Details for generation:\n"
             "- Package name: {package_name}\n"
             "- Function name and arguments: {function_name_and_arguments}\n"
             "- Code location: {code_location}\n"
             "- Function description: {prediction}\n\n"
             "Essential requirements:\n"
             "1. Start with import statements:\n"
             "   - import 'package:{package_name}/{code_location}';\n"
             "   - import 'package:test/test.dart';\n"
             "2. Include main() function with appropriate test groups and cases\n"
             "3. Cover normal cases, edge cases, and error cases when relevant\n"
             "4. Use the Arrange-Act-Assert pattern with comments\n"
             "5. End with regular comments (not block comments) for test coverage evaluation\n\n"
             "DO NOT include any markdown formatting (```dart, ```), explanation text, or block comments /* */. "
             "Your output should be pure Dart code that can be directly saved to a .dart file and executed.\n\n"
             "Use regular line comments // for the coverage evaluation at the end."
            ),
            ("human", "Generate a complete test case file for {function_name_and_arguments}")
        ])
        
        chain = clean_prompt | self.model
        
        response = chain.invoke({
            "package_name": package_name,
            "function_name_and_arguments": function_name_and_arguments,
            "code_location": code_location,
            "prediction": prediction
        })
        
        return response.content
            
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
        
        # Use the appropriate loader based on file extension
        loader_class = file_loader_map.get(file_extension)
        if loader_class:
            loader = loader_class(file_path=file_path)
        else:
            # Fallback to PyPDFLoader (as in your original code)
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
    package_name = 'sample'
    code_location = 'lib/widgets/screens/Homepage/homepage.dart'
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
    print(tg.generate_test_case(
        package_name=package_name,
        code_location=code_location,
        function_name_and_arguments=function_name_and_arguments, 
        prediction=prediction,
    ))