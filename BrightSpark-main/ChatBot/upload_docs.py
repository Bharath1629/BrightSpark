# upload pdfs to pinecone
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import pinecone
from langchain.vectorstores import Pinecone


def load_docs(directory):
    loader = PyPDFDirectoryLoader(directory)
    documents = loader.load()
    return documents

def split_docs(documents,chunk_size=500,chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    return docs

directory = './Assets'
documents = load_docs(directory)
docs = split_docs(documents)
embeddings = HuggingFaceEmbeddings(model_name="thenlper/gte-large",encode_kwargs={"normalize_embeddings": True},)

# Create an instance of the Pinecone class
pc = pinecone.Pinecone(
    api_key="PINECONE_API_KEY",  # find at app.pinecone.io
    environment="gcp-starter"  # next to api key in console
)

index_name = "gen-ai"
index = Pinecone.from_documents(docs, embeddings, index_name=index_name,namespace='brightspeed')