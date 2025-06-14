import os
import dotenv
import streamlit as st


from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent, should_rebuild_agent

dotenv.load_dotenv()

st.set_page_config(page_title="Dental Clinics Chatbot", page_icon="🦜")
st.title("🦜 Dental Clinics Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "agent" not in st.session_state:
    st.session_state.agent = build_agent()
    
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

user_question = st.chat_input("Ask a question")

if user_question:
    if should_rebuild_agent():
        st.session_state.agent = build_agent()
    with st.chat_message("user"):
        st.markdown(user_question)
        st.session_state.messages.append(HumanMessage(user_question))
    result = st.session_state.agent.invoke({"input": user_question, "chat_history":st.session_state.messages})
    ai_message = result["output"]
    
    with st.chat_message("assistant"):
        st.markdown(ai_message)
        st.session_state.messages.append(AIMessage(ai_message))

    
# while True:
#     question = input("Ask your question: (press q to quit)")
#     if question == 'q':
#         break
#     response = agent_excuter.invoke({"input": question})
#     print(response)
