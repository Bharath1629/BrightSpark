from pinecone_index import *
from langchain.agents import Tool
from embedding_model import get_embedding_model
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from model import get_llm
from langchain.vectorstores.pinecone import Pinecone
import openai

vectordb = Pinecone(index=get_index("gen-ai"), embedding=get_embedding_model().embed_query, text_key="text",namespace="brightspeed")
prompt = PromptTemplate.from_template(template="use this tool only for questions related to brightspeed")

chain = LLMChain(
    prompt=prompt,
    llm=get_llm('openai')
)

def get_vectordb_tool():
    tool = Tool(
        func=vectordb.similarity_search,
        name="BrightSpeed Documents Vector DB Tools",
        description="Contains all information that are related to Brightspeed,use this tool only when the questions are related to brightspeed",
        retriever_top_k=3,
        verbose=True
    )
    return tool