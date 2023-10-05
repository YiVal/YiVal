
# type: ignore
import openai
import streamlit as st
import os
import pickle


def run_streamlit():
    with open("data.pkl", "rb") as f:
        data = pickle.load(f)
    print(f"[DEBUG]data: {data}")
    experiment_data = data["experiment_data"]
    experiment_config = data["experiment_config"]
    function_args = data["function_args"]
    all_combinations = data["all_combinations"]
    state = data["state"]
    logger = data["logger"]
    evaluator = data["evaluator"]
    interactive = data["interactive"]

    st.title("ChatGPT-like clone")

    openai.api_key = os.getenv("OPENAI_API_KEY")

    print(f"[DEBUG]st.session_state: {st.session_state}")

    if 'openai_model' not in st.session_state:
        st.session_state['openai_model'] = 'gpt-3.5-turbo'


    if 'messages' not in st.session_state:
        st.session_state.messages = []

    print(f"[DEBUG]st.session_state: {st.session_state}")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    run_streamlit()
