from RAG.RAG import query_vector_store
from LLM.LLM import invoke

store_name = "romeo_and_juliet"
query = "How did Juliet die?"

relevant_docs = query_vector_store(store_name, query, docs_num=3)
# print(relevant_docs)
response = invoke(query, relevant_docs=relevant_docs)
print(response)