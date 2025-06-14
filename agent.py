import os
import dotenv
import streamlit as st
import requests

from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain import hub
from langchain_core.tools import tool
from langchain.prompts import SystemMessagePromptTemplate

dotenv.load_dotenv()

openai_key = os.environ.get("OPENAI_API_KEY")
embedding_model = os.environ.get("EMBEDDING_MODEL")
chroma_collection = os.environ.get("CHROMA_COLLECTION")
chroma_dir = os.environ.get("CHROMA_DIR")

embeddings = OpenAIEmbeddings(model=embedding_model)
    
def build_agent():
    
    
    llm = ChatOpenAI(temperature=0)

    agent_prompt = os.environ.get("AGENT_PROMPT")

    prompt = hub.pull(agent_prompt)
    custom_message = SystemMessagePromptTemplate.from_template(
        """You are a helpful assistant. You act as a customer cervice support for dental clinics.
        Your goal is to answer the questions of the users about dental clinics available in provided database.
        You can only answer from the documents in the provided database. Don't make up answers if you couldn't find answers or related 
        information about the user question in the database. Only provide relevant information from the database.
        Don't answer quesions outside the topics of dental clinics suport.Don't make up answers outside the document.
        Don't mention any data not included in the provided database. If after querying database, no result is found, respond 
        that no available information about the user question. 
        """
    )
    custom_prompt = prompt.copy()
    custom_prompt.messages.insert(0, custom_message)
# print(prompt)
    vector_store = Chroma(
    collection_name=chroma_collection,
    embedding_function=embeddings,
    persist_directory=chroma_dir,  # Where to save data locally, remove if not necessary
    )
    try:
        collection = vector_store._collection
        results = collection.get(include=["embeddings"])
        docs_in_db = len(results["ids"])
        print(f"✅ Docs in Chroma DB: {docs_in_db}")
        print("✅ Number of embeddings stored:", len(results["embeddings"]))
    except Exception as e:
        print("❌ Failed to read Chroma DB:", e)
    @tool(response_format="content_and_artifact")
    def retrieve(query: str):
        """Retrieve information related to a query."""
        retrieved_docs = vector_store.similarity_search(query, k=2)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    tools = [retrieve]
    agent = create_tool_calling_agent(llm, tools, custom_prompt)

    agent_excuter = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_excuter

def should_rebuild_agent():
    url = "http://localhost:8000/last_updated/"
    try:
        res = requests.get(url)
        ts = res.json()["timestamp"]
        if "last_ts" not in st.session_state:
            st.session_state.last_ts = 0
        if ts > st.session_state.last_ts:
            st.session_state.last_ts = ts
            return True
    except:
        pass
    return False