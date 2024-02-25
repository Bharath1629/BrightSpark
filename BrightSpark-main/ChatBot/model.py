from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.llms import OpenAI
from dotenv import load_dotenv
from langchain.llms.deepinfra import DeepInfra
from langchain_experimental.chat_models import Llama2Chat
import os
load_dotenv()
key= os.getenv("openai_api_key")
client = OpenAI(api_key=key)
def get_chat_model(model: str):
    if model == "llama2":
        llm = DeepInfra(
            deepinfra_api_token='3mjwuXqOF8xOZqrJ8gzzNAqO0gW6BB33',
            model_id="meta-llama/Llama-2-70b-chat-hf",
            model_kwargs={"temperature": 0.0}
        )
        model = Llama2Chat(llm=llm)
    if model == "openai":
        model = ChatOpenAI()
    return model

def get_llm(llm: str):
    if llm == "llama2":
        llm = DeepInfra(
            deepinfra_api_token='3mjwuXqOF8xOZqrJ8gzzNAqO0gW6BB33',
            model_id="meta-llama/Llama-2-70b-chat-hf",
            model_kwargs={"temperature": 0.0}
        )
    if llm == "openai":
        llm = ChatOpenAI()
    return llm

