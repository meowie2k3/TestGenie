from dotenv import load_dotenv
import os
load_dotenv()

from langchain_openai import ChatOpenAI


base_url = os.getenv('BASE_URL')
# print('base_url:', base_url)

llm = ChatOpenAI(base_url=base_url)

prompt = "What is 81 divided by 9?"

result = llm.invoke(prompt)

content = result.content

print(content)



