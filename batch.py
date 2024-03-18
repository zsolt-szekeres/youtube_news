import logging

import youtube_parser as yp
import myshare
import speech2text as s2t
import youtube_transcript as yt
import llms
import content
import config
from distutils.dir_util import copy_tree
import os


if __name__ == "__main__":

    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if config.params["run_mode"] == "DEBUG" else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(config.params["log_folder"], "batch.log"),
        filemode="w",
    )
    logger = logging.getLogger()

    if config.params["local_whisper_enabled"]:
        ws = s2t.ws()  # initialize speech to text model

    channel_ids = [item["id"] for item in config.params["youtube_channels"]]

    for channel_id in channel_ids:
        try:
            video_ids = yp.get_videos_from_channel(channel_id, 2)
            for v in video_ids[:2]:
                logger.info(channel_id + " _ " + v)
                transcript_ready = False
                try:
                    url = "https://www.youtube.com/watch?v=" + v
                    fname, format, info = yp.get_video(
                        url,
                        format="mp3",
                        download=False,
                    )
                    logger.debug(yp.is_recent(info["upload_date"]))
                    if yp.is_recent(info["upload_date"]):
                        logger.debug(
                            f"{info['channel']} | {info['title']} | {info['upload_date']}"
                        )
                        logger.debug(f"Duration: {info['duration_string']}")
                        info["youtube_transcript_api_enabled"] = config.params[
                            "yt_transcript_api_enabled"
                        ]
                        info["transcript_received"] = False
                        info["lang_code"] = None
                        if config.params["yt_transcript_api_enabled"]:
                            logger.debug(
                                f"Youtube transcript API enabled. url: {url}, title: {info['title']}"
                            )
                            transcription = {}
                            transcription["text"], info["lang_code"] = (
                                yt.get_transcript(url)
                            )
                            if transcription["text"] is not None:
                                transcript_ready = True
                                if config.params["force_download_audio"]:
                                    fname, format, _ = yp.get_video(url, format="mp3")
                            info["transcript_received"] = transcript_ready
                        if (
                            config.params["local_whisper_enabled"]
                            and not transcript_ready
                        ):
                            fname, format, _ = yp.get_video(url, format="mp3")
                            transcription = ws.transcribe(fname + "." + format)
                            transcript_ready = True
                        if transcript_ready:
                            ntokens = llms.get_num_tokens(transcription["text"])
                            info["ntokens"] = ntokens
                            logger.debug(f"This has  {ntokens} tokens")
                            summary, chunk_size, overlap = llms.get_summary(
                                [transcription["text"]], ntokens
                            )
                            myshare.send_email(summary, info)
                            logger.info("email sent")
                            content.save_all(summary, transcription, info, fname)
                            if config.params["backup_folder"]:
                                folder = os.path.dirname(fname)
                                last_folder = str.split(folder, os.sep)[-1]
                                copy_tree(
                                    folder,
                                    os.path.join(
                                        config.params["backup_folder"], last_folder
                                    ),
                                )
                    else:
                        break
                except Exception as e:
                    logger.info(
                        "An exception occurred while sending the email: {}".format(
                            str(e)
                        )
                    )
                    continue
        except Exception as e2:
            logger.info(
                "An exception occurred with the channel: {}".format(str(channel_id))
            )
            logger.info("Details: {}".format(str(e2)))
            continue
