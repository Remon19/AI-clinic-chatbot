import os
import dotenv

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from chromadb import PersistentClient

dotenv.load_dotenv()

penai_key = os.environ.get("OPENAI_API_KEY")
embedding_model = os.environ.get("EMBEDDING_MODEL")
chroma_collection = os.environ.get("CHROMA_COLLECTION")
chroma_dir = os.environ.get("CHROMA_DIR")

embeddings = OpenAIEmbeddings(model=embedding_model)
    

def load_chroma_db():
   return Chroma(
    collection_name=chroma_collection,
    embedding_function=embeddings,
    persist_directory=chroma_dir,  # Where to save data locally, remove if not necessary
    )
   
def create_chroma_db(docs, embeddings, ids):
    vectore_store = Chroma.from_documents(
        docs,
        embeddings,
        ids,
        collection_name=chroma_collection,
        persist_directory=chroma_dir,  # Where to save data locally, remove if not necessar
        )
    vectore_store.persist()
    return vectore_store
    