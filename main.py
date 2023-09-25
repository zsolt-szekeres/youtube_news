import time
import streamlit as st
import youtube_parser as yp

import config

import myshare
import llms
import speech2text as s2t
import content

if __name__ == '__main__': 

    st.markdown("*Loading speech-to-text model...*")
    ws = s2t.ws() 

    with st.sidebar:
        st.header("Configuration")
        yt_link = st.text_input('Youtube link')
        cache_folder = st.text_input('Path to folder of the previous dump. This will only be used when above youtube link is left blank.')    
        local_config={}
        local_config['simple_prompt'] = st.text_area(label = 'Simple prompt (without map reduce) used when prompt is short',value = config.params['gpt']['simple_prompt'])        
        local_config['map_prompt'] = st.text_area(label = 'MAP prompt',value = config.params['gpt']['map_prompt'])    
        local_config['combine_prompt'] = st.text_area(label = 'COMBINE prompt',value = config.params['gpt']['combine_prompt'])
        local_config['simple_model'] = st.selectbox('Select your simple model',('gpt-3.5-turbo','gpt-4'))
        local_config['mapreduce_model'] = st.selectbox('Select your mapreduce model',('gpt-3.5-turbo','gpt-4'))    
        local_config['chunk_size'] = st.text_input(label='Chunk size',value=config.params['chunking']['size'])
        local_config['overlap'] = st.text_input(label='Overlap', value=config.params['chunking']['overlap'])
        email_send = st.checkbox("Send me an email with the summary")
        debug_mode = st.checkbox('Debug mode')

    button1 = st.button('Get input and summarize')    

    if button1:        

        if yt_link:
            start = time.time()
            fname, format, info = yp.get_video (yt_link)
            end = time.time()

            st.write(f'Downloaded {fname+"."+format} in  {round((end - start) / 60, 2)}  mins')
            st.write (f"Duration: {info['duration_string']}")            
            st.image(info['thumbnail'])

            st.markdown("*Speech to text...*")
            start = time.time()
            transcription = ws.transcribe(fname+'.'+format)
            end = time.time()
            st.write(f'Transcribed in  {round((end - start) / 60, 2)}  mins')
        else:
            transcription, info = content.get_transcript(cache_folder)
            fname = str.split(cache_folder,'\\')[3]+'\\'+str.split(cache_folder,'\\')[4]+'\\'+str.split(cache_folder,'\\')[4]

        if debug_mode:
            config.params['email']['receiver_emails']=[config.params['email']['sender_email']]
        ntokens = llms.get_num_tokens(transcription['text'])
        st.write(f'This has  {ntokens} tokens')

        with st.spinner("Summarizing..."):
            st.markdown("*Summarizing...*")
            start = time.time()
            summary, chunk_size, overlap = \
                llms.get_summary([transcription['text']], ntokens, local_config)
            docs_search, context = llms.get_context_for_bot('what is knowledge', [transcription['text']], local_config)
            a=1
            st.write('chunk size='+str(chunk_size)+' , overlap='+str(overlap))
            st.write('<html>'+summary+'</html>', unsafe_allow_html=True)
            end = time.time()
            st.write(f'Summarized in  {round((end - start) / 60, 2)}  mins')

        # Send the email
        if email_send:                        
            myshare.send_email(summary, info)

        content.save_all(summary, transcription, info, fname, local_config)        
       



    

