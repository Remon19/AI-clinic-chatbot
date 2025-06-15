import os
import dotenv
from uuid import uuid4
import time

from fastapi import FastAPI, UploadFile, File
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from chroma_vector import create_chroma_db

dotenv.load_dotenv()

openai_key = os.environ.get("OPENAI_API_KEY")
embedding_model = os.environ.get("EMBEDDING_MODEL")
chroma_collection = os.environ.get("CHROMA_COLLECTION")
chroma_dir = os.environ.get("CHROMA_DIR")

embeddings = OpenAIEmbeddings(model=embedding_model)

## initializing chroma db


data_path = os.environ.get("DATA_PATH")
if not os.path.exists(data_path):
    os.mkdir(data_path)
        
last_update = time.time()

app = FastAPI()

@app.post('/uploadclinicfile')
async def upload_file(uploaded_file: UploadFile = File()):
    if not uploaded_file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if uploaded_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    # print("----------------------------------->",uploaded_file.filename)
    file_path = os.path.join(data_path, uploaded_file.filename)
    try:
        with open(file_path, "wb") as f:
            content = await uploaded_file.read()
            f.write(content)

        print("File uploaded sucessfully.")
        print("Loading Document...")
        
        # loader = PyPDFDirectoryLoader(data_path)

        # documents = loader.load()

        # print("Document loaded sucessfully.")
        
        # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        # print("Splitting Document...")
        # docs = text_splitter.split_documents(documents)
        # ids = [str(uuid4()) for _ in docs]
        # print("Document Splitted sucessfully.")
        
        # print("Ingesting documents in database")
        
        # if os.path.exists(chroma_dir):
        #     vector_store = Chroma(
        #         collection_name=chroma_collection,
        #         embedding_function=embeddings,
        #         persist_directory=chroma_dir,
        #     )
        #     vector_store.add_documents(docs, ids=ids)
        # else:
        # vector_store = create_chroma_db(
        #     docs,
        #     embeddings,
        #     ids
        # )
        # print("Documents is ingested sucessfully.")
        # question = input("enter a query")
        # result = vector_store.similarity_search(question)
        # print(result)
    #     try:
    #         collection = vector_store._collection
    #         results = collection.get(include=["embeddings"])
    #         docs_in_db = len(results["ids"])
    #         print(f"✅ Docs in Chroma DB: {docs_in_db}")
    #         print("✅ Number of embeddings stored:", len(results["embeddings"]))
    #     except Exception as e:
    #         print("❌ Failed to read Chroma DB:", e)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="internal server error")

    global last_update
    last_update = time.time()
    return JSONResponse(content={"message": f"Uploaded and ready to be Ingested: {uploaded_file.filename} sucessfully."}, 
                        status_code=200)
    
@app.get("/last_updated")
def get_last_update():
    return {"timestamp": last_update}


    