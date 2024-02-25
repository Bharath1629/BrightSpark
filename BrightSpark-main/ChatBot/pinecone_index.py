# pinecone index
from pinecone import Pinecone
import os
import pinecone

key = os.getenv('PINECONE_API_KEY')
client = Pinecone(api_key=key)

index_name = "gen-ai"
def get_index(index_name:str):
    index = client.Index(index_name)
    return index