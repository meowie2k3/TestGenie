from dotenv import load_dotenv
import os


from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

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

class AI_Agent:
    def __init__(self) -> None:
        if load_dotenv(override=True) == False:
            raise Exception("Failed to load .env file")
        self.base_url = os.getenv('BASE_URL')
        self.model_name = os.getenv('LLM_MODEL')
        self.model = ChatOpenAI(base_url=self.base_url, model=self.model_name, temperature=0)
        
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
        
        prompt = hub.pull("hwchase17/react")
        
        agent = create_react_agent(
            llm=self.model,
            tools=tools,
            prompt=prompt,
            stop_sequence=True,
        )
        
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=True,
        )
        
        response = agent_executor.invoke({"input": "What time is it?"})
        
        print(response)
        
if __name__ == "__main__":
    ai_agent = AI_Agent()
    ai_agent.run_test()