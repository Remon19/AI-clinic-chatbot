import os
import dotenv
from uuid import uuid4

import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


dotenv.load_dotenv()

openai_key = os.environ.get("OPENAI_API_KEY")
embedding_model = os.environ.get("EMBEDDING_MODEL")
chroma_collection = os.environ.get("CHROMA_COLLECTION")
chroma_dir = os.environ.get("CHROMA_DIR")

embeddings = OpenAIEmbeddings(model=embedding_model)

## initializing chroma db

vector_store = Chroma(
    collection_name=chroma_collection,
    embedding_function=embeddings,
    persist_directory=chroma_dir,  # Where to save data locally, remove if not necessary
)

data_path = os.environ.get("DATA_PATH")
if not os.path.exists(data_path):
    os.mkdir(data_path)

st.set_page_config("File Uploader")

uploaded_file = st.file_uploader("Upload your clinic file", type='pdf')

if uploaded_file:
        
    file_path = os.path.join(data_path, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
        st.success("Saved File:{} to Data".format(uploaded_file.name))
        
    st.write("File uploaded successfully")

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    docs = text_splitter.split_documents(documents)
    ids = [str(uuid4()) for _ in docs]

    vector_store.from_documents(
        docs,
        embeddings,
        ids = ids,
        collection_name=chroma_collection,
        persist_directory=chroma_dir
    )
    vector_store.persist()

