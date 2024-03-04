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

    if not config.params["yt_transcript_api_enabled"]:
        ws = s2t.ws()  # initialize speech to text model

    channel_ids = [item["id"] for item in config.params["youtube_channels"]]

    for channel_id in channel_ids:
        try:
            video_ids = yp.get_videos_from_channel(channel_id, 2)
            for v in video_ids[:2]:
                logger.info(channel_id + " _ " + v)
                do_skip_rest = False
                try:
                    url = "https://www.youtube.com/watch?v=" + v
                    fname, format, info = yp.get_video(
                        url, format="mp3", download=False
                    )
                    logger.debug(yp.is_recent(info["upload_date"]))
                    if yp.is_recent(info["upload_date"]):
                        logger.debug(
                            f"{info['channel']} | {info['title']} | {info['upload_date']}"
                        )
                        info["youtube_transcript_api_enabled"] = config.params[
                            "yt_transcript_api_enabled"
                        ]
                        info["transcript_received"] = False
                        if config.params["yt_transcript_api_enabled"]:
                            logger.debug(
                                f"Youtube transcript API enabled. url: {url}, title: {info['title']}"
                            )
                            transcription = {}
                            transcription["text"], _ = yt.get_transcript(
                                yt_link=url, do_assert=False
                            )
                            if transcription["text"] is None:
                                do_skip_rest = True
                                logger.debug(
                                    f"No youtube transcript found for video url: {url}, title: {info['title']}"
                                )
                            info["transcript_received"] = True
                        else:
                            fname, format, info = yp.get_video(url, format="mp3")
                            logger.debug(f"Duration: {info['duration_string']}")
                            transcription = ws.transcribe(fname + "." + format)
                        if not do_skip_rest:
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
                                os.chdir("videos")
                                folder = str.split(fname, os.sep)[1]
                                copy_tree(
                                    folder,
                                    config.params["backup_folder"] + "//" + folder,
                                )
                                os.chdir("..")
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
