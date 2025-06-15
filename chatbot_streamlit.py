import os
import dotenv
import streamlit as st


from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent, should_rebuild_agent

dotenv.load_dotenv()

data_path = os.environ.get("DATA_PATH")
if not os.path.exists(data_path):
    os.mkdir(data_path)

st.set_page_config(page_title="Dental Clinics Chatbot", page_icon="🦜")
st.title("🦜 Dental Clinics Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "last_ts" not in st.session_state:
    st.session_state.last_ts = 0
    
if "agent" not in st.session_state:
    st.session_state.agent = None
    
if "clinic_files" not in st.session_state:
        st.session_state.clinic_files = os.listdir(data_path)
agent = None
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

user_question = st.chat_input("Ask a question")
if len(os.listdir(data_path)) == 0:
    error_no_file_message = "No clinic files uploaed, please add clinic files to proceed"
    st.session_state.messages.append(AIMessage(error_no_file_message))
else:
    if st.session_state.agent is None:
        print("********************************************")
        st.session_state.agent = build_agent()
    if user_question:
        with st.chat_message("user"):
            st.markdown(user_question)
            st.session_state.messages.append(HumanMessage(user_question))
        result = st.session_state.agent.invoke({"input": user_question, "chat_history":st.session_state.messages})
        ai_message = result["output"]
        
        with st.chat_message("assistant"):
            st.markdown(ai_message)
            st.session_state.messages.append(AIMessage(ai_message))
        new_files = list(set(os.listdir(data_path)).difference(set(st.session_state.clinic_files)))
        print(new_files)
        if new_files:
            print("_________________________________________________________")
            st.session_state.agent = build_agent(new_files)
        st.session_state.clinic_files = os.listdir(data_path)
# while True:
#     agent = build_agent()
#     question = input("Ask your question: (press q to quit)")
#     if question == 'q':
#         break
#     response = agent.invoke({"input": question})
#     print(response)
    
