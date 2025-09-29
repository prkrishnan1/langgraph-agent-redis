import streamlit as st
from agent import LanggraphAgent
from thread import Thread
from langchain_core.messages.tool import ToolMessageChunk
from langchain_core.messages.ai import AIMessageChunk

st.title("🦜🔗 Langgraph Agent with Redis Persistence")
user_id = "1"

agent = LanggraphAgent()
thread_id = st.sidebar.text_input("Enter a chat ID", type="default")
thread_manager = Thread(user_id=user_id, thread_id=thread_id, agent=agent)

for message in thread_manager.populate_chat_history():
    # message [("user", content)]
    if message[0] == "tool":
        with st.chat_message("tool"):
            st.markdown("Calling tool...")
    else:
        with st.chat_message(message[0]):
            st.markdown(message[1])
    

def generate_response(input_text: str):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = """"""
        for chunk in thread_manager.stream_agent_response(input_text, config=thread_manager.config):

            if "LLM" in chunk and "messages" in chunk["LLM"] and len(chunk["LLM"]["messages"]) > 0: # case when streaming type is "updates"
                content = chunk["LLM"]["messages"][-1].content
                full_response += content
                message_placeholder.markdown(full_response + "▌")
            elif isinstance(chunk, tuple): # case when streaming type is "messages"
                if isinstance(chunk[0], AIMessageChunk):
                    content = chunk[0].content
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
                elif isinstance(chunk[0], ToolMessageChunk):
                    full_response += "Calling tool...\n"
                    message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)


if prompt := st.chat_input("What are the three key pieces of advice for learning how to code?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    generate_response(prompt)
