from dotenv import load_dotenv
import os
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnableBranch

base_url = os.getenv('BASE_URL')
model_name = os.getenv('LLM_MODEL')

if __name__ == '__main__':
    model = ChatOpenAI(base_url=base_url, model=model_name)
    
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert product reviewer."),
            ("human", "List the main features of the product {product_name}."),
        ]
    )
    
    # Simplify branches with LCEL
    positive_feedback_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("human",
            "Generate a thank you note for this positive feedback: {feedback}."),
        ]
    )

    negative_feedback_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("human",
            "Generate a response addressing this negative feedback: {feedback}."),
        ]
    )

    neutral_feedback_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            (
                "human",
                "Generate a request for more details for this neutral feedback: {feedback}.",
            ),
        ]
    )

    escalate_feedback_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            (
                "human",
                "Generate a message to escalate this feedback to a human agent: {feedback}.",
            ),
        ]
    )

    # Define the feedback classification template
    classification_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("human",
            "Classify the sentiment of this feedback as positive, negative, neutral, or escalate: {feedback}."),
        ]
    )
    
    # Define the runnable branches for handling feedback
    branches = RunnableBranch(
        (
            lambda x: "positive" in x,
            positive_feedback_template | model | StrOutputParser()  # Positive feedback chain
        ),
        (
            lambda x: "negative" in x,
            negative_feedback_template | model | StrOutputParser()  # Negative feedback chain
        ),
        (
            lambda x: "neutral" in x,
            neutral_feedback_template | model | StrOutputParser()  # Neutral feedback chain
        ),
        escalate_feedback_template | model | StrOutputParser()
    )
        
    # create combined chain
    # Create the classification chain
    classification_chain = classification_template | model | StrOutputParser()
    
    # Combine classification and response generation into one chain
    chain = classification_chain | branches

    # result
    review = "The product is exellence. I love it."
    result = chain.invoke({"feedback": review})
    print(result)

