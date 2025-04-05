# agent_setup.py
from langchain.agents import initialize_agent, AgentType
#from langchain.llms import OpenAI
from langchain_openai import ChatOpenAI
from tools import train_model_tool, detect_anomaly_tool


llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")  # or gpt-4-0613 if needed

tools = [train_model_tool, detect_anomaly_tool]

agent = initialize_agent(
    tools=tools,
    llm=llm,
     agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

