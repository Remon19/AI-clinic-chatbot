import os
import dotenv
from uuid import uuid4

from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain_core.tools import tool

from chroma_vector import create_chroma_db, load_chroma_db


dotenv.load_dotenv()

## loading enviroment variables from .env 
chroma_db = os.environ.get("CHROMA_DIR")
openai_key = os.environ.get("OPENAI_API_KEY")
embedding_model = os.environ.get("EMBEDDING_MODEL")
data_path = os.environ.get("DATA_PATH")

embeddings = OpenAIEmbeddings(model=embedding_model)
        
def build_agent(new_files=[]):
    """Create an agent to retrieve relevant files from the vector db based 
    and answer on the user inquireies.
    inputs: a list of new files addd to data dir.
    outputs: an agent executor that perform retrieval and document based question answering"""
    
    ## no new files are added to the data dir ----> create vector db from the existing clinic files 
    if not new_files:
        loader = PyPDFDirectoryLoader(data_path)

        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

        docs = text_splitter.split_documents(documents)
        ids = [str(uuid4()) for _ in docs]
        ## create vector db if first time build agent
        if not os.path.exists(chroma_db):
            vector_store = create_chroma_db(
                    docs,
                    embeddings,
                    ids
                )
        else:
            ## otherwise load persistent vector db
            vector_store = load_chroma_db()
    else:
        ## a new clinic files uploaded to data dir. ---> add them to the persistent vector db
        print("Ingesting new clinic files")
        for file in new_files:
            loader = PyPDFLoader(os.path.join(data_path, file))

            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

            docs = text_splitter.split_documents(documents)
            ids = [str(uuid4()) for _ in docs]
            vector_store = load_chroma_db()
            vector_store.add_documents(docs, ids=ids)
    ## ensure that files are ingested in the vector db
    try:
        collection = vector_store._collection
        results = collection.get(include=["embeddings"])
        docs_in_db = len(results["ids"])
        print(f"✅ Docs in Chroma DB: {docs_in_db}")
        print("✅ Number of embeddings stored:", len(results["embeddings"]))
        print("Files ingested sucessfully.")
    except Exception as e:
        print("❌ Failed to read Chroma DB:", e)
    
    ## chatgpt as an LLM backbone of the agent
    llm = ChatOpenAI(temperature=0)
    
    prompt_url = os.environ.get("AGENT_PROMPT")

    ## default prompt importd from langchain hub
    prompt = hub.pull(prompt_url)
    
    ## a system prompt customized for clinic documents 
    agent_message = SystemMessagePromptTemplate.from_template(
        """You are a helpful assistant. You act as a customer cervice support for dental clinics.
        Your goal is to answer the questions of the users about dental clinics available in provided database.
        You can only answer from the documents in the provided database. 
        Don't make up answers if you couldn't find answers or related information about the user question in the database. 
        Don't answer quesions outside the topics of dental clinics suport.
        Don't make up answers outside the document.
        Don't mention any data not included in the provided database. 
        If after querying database, no result is found, respond that no available information about the user question. 
        Always Provide the source file in the end of your answer.
        """
    )
    
    agent_prompt = prompt.copy()
    
    ## customizing the prompt with the new system message
    agent_prompt.messages.insert(0, agent_message)

    ## a function to retrieve relevant documents and pass it as a tool to agent
    @tool(response_format="content_and_artifact")
    def retrieve(query: str):
        """Retrieve information related to a query."""
        retrieved_docs = vector_store.similarity_search(query, k=5)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs
    
    tools = [retrieve]
    agent = create_tool_calling_agent(llm, tools, agent_prompt)

    agent_excuter = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_excuter
    

