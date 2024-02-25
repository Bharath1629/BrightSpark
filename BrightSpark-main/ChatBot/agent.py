# Agent
from langchain.agents import ConversationalChatAgent, AgentExecutor
from tools.vectordb_tool import get_vectordb_tool
from model import get_chat_model
from agent_chat_memory import get_memory
from agent_prompt import *
from langchain.agents import load_tools
from model import get_llm
from tools.general_tool import get_general_tool


def get_tools():
    tools = load_tools([], llm=get_llm('openai'))
    tools.append(get_vectordb_tool())
    # tools.append(get_general_tool())
    return tools


model = get_chat_model('openai')
memory = get_memory()
system_message = ""
def get_agent_type(input):
    type_of_agent=""
    if type_of_agent == "general":
        system_message = general_agent_prompt
    elif type_of_agent == "sales":
        system_message = sales_agent_prompt
    else:
        system_message = service_agent_prompt



agent_definition = ConversationalChatAgent.from_llm_and_tools(
    llm = model,
    tools  = get_tools(),
    verbose =True,
    system_message=system_message,
    handle_parsing_errors=True

)
agent_execution = AgentExecutor.from_agent_and_tools(
    agent=agent_definition,
    llm=model,
    tools= get_tools(),
    verbose = True,
    max_iterations=3,
    memory = memory,
    handle_parsing_errors= True

)



