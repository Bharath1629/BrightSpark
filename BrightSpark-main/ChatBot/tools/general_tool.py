from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from model import get_llm
import openai
import pinecone_index
from langchain.chains import LLMChain

prompt = PromptTemplate.from_template(template="use this tool only for questions related to brightspeed. If the question is not related to brightspeed redirect user to brightspeed.")

chain = prompt | get_llm('openai')

def get_general_tool():

    tool = Tool(
        func=chain.stream,
        name="General Tool",
        description="Tool to answer the general questions",
    )
    return tool