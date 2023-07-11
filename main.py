import youtube_parser as yp
import streamlit as st
import myshare

import time
import llms
import pickle

import speech2text as s2t

if __name__ == '__main__': 

    st.markdown("*Loading model...*")
    ws = s2t.ws() 
    yt_link = st.text_input('Youtube link')
    pickle_link = st.text_input('Path to previous dump (pickle file). This will only be used when above youtube link if left blank.')
    simple_prompt = st.text_area(label = 'Simple prompt (without map reduce) used when prompt is short',value = llms.SIMPLE_PROMPT)
    st.markdown("Using lvl 3 summary by Greg at http://www.youtube.com/watch?v=qaPMdcCqtWk")
    map_prompt = st.text_area(label = 'MAP prompt',value = llms.MAP_PROMPT)
    combine_prompt = st.text_area(label = 'COMBINE prompt',value = llms.COMBINE_PROMPT)
    chunk_size = st.text_input(label='Chunk size',value=3600)
    overlap = st.text_input(label='Overlap', value=100)
    email_send = st.checkbox("Send me an email with the summary")
    button1 = st.button('Get video, convert and summarize')
    

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
            response = ws.transcribe(fname+'.'+format)
            end = time.time()
            st.write(f'Transcribed in  {round((end - start) / 60, 2)}  mins')
        else:
            with open(pickle_link, "rb") as file:
                (output, response, info, fname) = pickle.load(file)

        ntokens = llms.get_num_tokens(response['text'])
        st.write(f'This has  {ntokens} tokens')

        st.markdown("*Summarizing...*")
        start = time.time()
        output, chunk_size, overlap = \
            llms.get_bullets([response['text']], ntokens, map_prompt=map_prompt, \
                             combine_prompt=combine_prompt, chunk_size=int(chunk_size), overlap=int(overlap))
        st.write('chunk size='+str(chunk_size)+' , overlap='+str(overlap))
        st.write('<html>'+output+'</html>', unsafe_allow_html=True)
        end = time.time()
        st.write(f'Summarized in  {round((end - start) / 60, 2)}  mins')

        with open(fname+'.html', "w") as f:
            f.write(output)

        # Send the email
        if email_send:
            myshare.send_email(output, info['title'], yt_link)

        data = (output, response, info, fname)
        with open(fname+'_sum.p', "wb") as file:
            pickle.dump(data, file)
       



    

