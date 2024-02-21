import os
import time
import streamlit as st

import json

import config

import content
import llms
import openai

# Adaptation of https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
if __name__ == "__main__":

    with st.sidebar:
        st.header("Configuration")
        cache_folder = st.text_input("Path to folder of the previous dump")
        context_num = st.text_input(label="Number of relevant contexts", value=3)
        context_len = st.text_input(label="Length of contexts (chars)", value=1000)
        context_overlap = st.text_input(label="Overlap of contexts (chars)", value=50)
        button1 = st.button("Get context")

    # query = st.chat_input("Ask a question about the video")

    if "transcription" not in st.session_state:
        st.session_state.transcription = None
        st.session_state.info = None
        st.session_state.fname = None

    if button1:
        st.session_state.transcription, st.session_state.info = content.get_transcript(
            cache_folder
        )
        st.session_state.fname = (
            str.split(cache_folder, os.sep)[3]
            + os.sep
            + str.split(cache_folder, os.sep)[4]
            + os.sep
            + str.split(cache_folder, os.sep)[4]
        )
        st.session_state.history_file = (
            cache_folder + str.split(cache_folder, os.sep)[4] + "_history.json"
        )
        st.write("*Content has been loaded*")

    openai.api_key = config.params["auth_codes"]["OpenAI_API_key"]

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo-16k"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask this video a question."):

        docs, context = llms.get_context_for_bot(
            prompt,
            [st.session_state.transcription["text"]],
            None,
            int(context_num),
            int(context_len),
            int(context_overlap),
        )
        prompt = (
            "Answer the question based on the "
            + context_num
            + " contexts after the question, and our prior conversation history (if we have one). \n"
            + "QUESTION: "
            + prompt
        )
        for i in range(int(context_num)):
            prompt = (
                prompt + "\n CONTEXT" + str(i + 1) + ": " + str(context[i].page_content)
            )

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                # for response in openai.ChatCompletion.create(
                for response in openai.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                ):
                    # full_response += response.choices[0].delta.get("content", "")
                    res = dict(response.choices[0].delta).get("content")
                    if res:
                        full_response += res
                    message_placeholder.markdown(full_response + " ")
                message_placeholder.markdown(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
            # with open(st.session_state.fname+"_history.json", "w",encoding='utf-8') as json_file:
            with open(
                st.session_state.history_file, "w", encoding="utf-8"
            ) as json_file:
                json.dump(st.session_state.messages, json_file, indent=4)
        except Exception as e:
            with st.chat_message("assistant"):
                st.markdown(
                    "I am stuck. This conversation likely went beyond max tokens. Start a new conversation?"
                )
