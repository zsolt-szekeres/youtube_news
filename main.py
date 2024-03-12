import time
import streamlit as st
import youtube_parser as yp

import config

import myshare
import llms
import speech2text as s2t
import youtube_transcript as yt
import content

from media_downloader import MediaDownloader
from distutils.dir_util import copy_tree
import os


if __name__ == "__main__":
    transcript_ready = False
    media_downloader = MediaDownloader(config)

    with st.sidebar:
        st.header("Configuration")
        yt_link = st.text_input("Youtube link")
        cache_folder = st.text_input(
            "Path to folder of the previous dump. This will only be used when above youtube link is left blank."
        )
        local_config = {}
        local_config["simple_prompt"] = st.text_area(
            label="Simple prompt (without map reduce) used when prompt is short",
            value=config.params["gpt"]["simple_prompt"],
        )
        local_config["map_prompt"] = st.text_area(
            label="MAP prompt", value=config.params["gpt"]["map_prompt"]
        )
        local_config["combine_prompt"] = st.text_area(
            label="COMBINE prompt", value=config.params["gpt"]["combine_prompt"]
        )
        local_config["simple_model"] = st.selectbox(
            "Select your simple model", ("gpt-3.5-turbo", "gpt-4")
        )
        local_config["mapreduce_model"] = st.selectbox(
            "Select your mapreduce model", ("gpt-3.5-turbo", "gpt-4")
        )
        local_config["chunk_size"] = st.text_input(
            label="Chunk size", value=config.params["chunking"]["size"]
        )
        local_config["overlap"] = st.text_input(
            label="Overlap", value=config.params["chunking"]["overlap"]
        )
        email_send = st.checkbox("Send me an email with the summary")
        debug_mode = st.checkbox("Debug mode")
        yt_transcript_api_enabled = st.checkbox(
            "Use youtube transcript API",
            value=config.params["yt_transcript_api_enabled"],
        )
        local_whisper_enabled = st.checkbox(
            "Use local whisper", value=config.params["local_whisper_enabled"]
        )
        if local_whisper_enabled:
            st.markdown("*Speech-to-text model loaded*")
            ws = s2t.ws()
        else:
            st.markdown("*Speech-to-text model not loaded*")
            s2t.ws.delete()

    button1 = st.button("Get input and summarize")

    if button1:

        if yt_link:
            if yt_transcript_api_enabled:
                transcription = {}
                transcription["text"], lang_code = yt.get_transcript(yt_link=yt_link)
                if transcription["text"] is not None:
                    st.write(f"Transcript language code: '{lang_code}'")
                    transcript_ready = True

                if transcript_ready:
                    start = time.time()
                    fname, format, info = yp.get_video(
                        yt_link, download=config.params["force_download_audio"]
                    )
                    end = time.time()

                    st.write(
                        f'Downloaded youtube transcript of {os.path.basename(fname)+"."+format} in  {round((end - start) / 60, 2)}  mins'
                    )
                    st.write(f"Duration: {info['duration_string']}")
                    st.image(info["thumbnail"])

            if local_whisper_enabled and not transcript_ready:
                if yt_transcript_api_enabled:
                    st.write(
                        "No previously generated transcript found.\nUse local whisper model for speech-to-text..."
                    )
                if not config.params["force_download_audio"]:
                    start = time.time()
                    fname, format, info = yp.get_video(yt_link)
                    # fname, format, info = media_downloader._get_audio_from_youtube(yt_link)
                    end = time.time()
                    st.write(
                        f'Downloaded {os.path.basename(fname)+"."+format} in  {round((end - start) / 60, 2)}  mins'
                    )
                st.write(f"Duration: {info['duration_string']}")
                st.image(info["thumbnail"])

                st.markdown("*Speech to text...*")

                start = time.time()
                transcription = ws.transcribe(fname + "." + format)
                end = time.time()
                st.write(f"Transcribed in  {round((end - start) / 60, 2)}  mins")
                transcript_ready = True
        else:
            transcription, info = content.get_transcript(cache_folder)
            fname = (
                str.split(cache_folder, os.sep)[3]
                + os.sep
                + str.split(cache_folder, os.sep)[4]
                + os.sep
                + str.split(cache_folder, os.sep)[4]
            )
            transcript_ready = True
        if transcript_ready:
            if debug_mode:
                config.params["email"]["receiver_emails"] = [
                    config.params["email"]["sender_email"]
                ]
            ntokens = llms.get_num_tokens(transcription["text"])
            st.write(f"This has  {ntokens} tokens")

            with st.spinner("Summarizing..."):
                st.markdown("*Summarizing...*")
                start = time.time()
                summary, chunk_size, overlap = llms.get_summary(
                    [transcription["text"]], ntokens, local_config
                )
                # docs_search, context = llms.get_context_for_bot('what is knowledge', [transcription['text']], local_config)
                st.write("chunk size=" + str(chunk_size) + " , overlap=" + str(overlap))
                st.write("<html>" + summary + "</html>", unsafe_allow_html=True)
                end = time.time()
                st.write(f"Summarized in  {round((end - start) / 60, 2)}  mins")

            # Send the email
            if email_send:
                myshare.send_email(summary, info)

            content.save_all(summary, transcription, info, fname, local_config)
            if config.params["backup_folder"]:
                folder = os.path.dirname(fname)
                last_folder = str.split(folder, os.sep)[-1]
                copy_tree(
                    folder, os.path.join(config.params["backup_folder"], last_folder)
                )
