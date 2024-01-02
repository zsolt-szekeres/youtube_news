import time
import streamlit as st

import json

import config

import content
import llms
import openai
from pathlib import Path

import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

# Adaptation of https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
if __name__ == '__main__': 

    # if 'db' not in st.session_state:
    #    st.session_state.db = None

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo-16k"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Configuration")       
        p = Path(config.params['vector_store'])
        subfolders = [str(x) for x in p.iterdir() if x.is_dir()]
        vector_store = st.selectbox('Select vector store', subfolders)            
        fetch_k = st.number_input(label='MMR fetch_k',value=15)        
        top_k = st.number_input(label='MMR top_k', value=5) 
        button1 = st.button('Set search parameters and load content')
        prompt0 = 'Answer the question based on the contexts after the question, and our prior conversation history (if we have one). \n'+\
        'Organize your response into sections where the section is titled by the SOURCE, and the points are organized into numbered bullets. \n'+\
        'Before the bullets and after each SOURCE give a one sentence bio of who the source is. \n'+\
            'QUESTION: '
        prompt_template = st.text_area(label = 'MAP prompt',value = prompt0)           
        backup = st.text_input(label='Chat log name')
        button2 = st.button('Save this chat')       

    if button1:   
        st.session_state.db = Chroma(persist_directory= vector_store, embedding_function= OpenAIEmbeddings())
        st.write(vector_store+' has been loaded.')
        collection = st.session_state.db._collection
        metadata = collection.get(0)['metadatas']
        upload_dates = [x['upload_date'] for x in metadata]
        ids = [x['id'] for x in metadata]
        st.write('It has '+str(collection.count()) + ' sections and '+str(len(set(ids)))+' videos.')
        st.write('Min upload date: '+str(min(upload_dates))+', max upload date: '+str(max(upload_dates)))
        
        
        
    
    if button2:   
        with open(backup+'.json', "w",encoding='utf-8') as json_file:
            json.dump(st.session_state.messages, json_file, indent=4)

    openai.api_key = config.params['auth_codes']['OpenAI_API_key']

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # '+str(top_k) +'
    if prompt := st.chat_input("Ask this corpus a question."):
        context = st.session_state.db.max_marginal_relevance_search(prompt, k=top_k, fetch_k=fetch_k)
        prompt =  prompt_template + prompt
        for i in range(top_k):
            prompt = prompt + '\n CONTEXT'+str(i+1)+'(SOURCE: '+context[i].metadata['guest']+') '+context[i].page_content
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
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
            with open("history.json", "w",encoding='utf-8') as json_file:
                 json.dump(st.session_state.messages, json_file, indent=4)
        except:
            with st.chat_message("assistant"):
                st.markdown('I am stuck. This conversation likely went beyond max tokens. Start a new conversation?')

