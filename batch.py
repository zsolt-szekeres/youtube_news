import logging

import youtube_parser as yp
import myshare
import speech2text as s2t
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
        filename="batch.log",
        filemode="w",
    )
    logger = logging.getLogger()

    ws = s2t.ws()  # initialize speech to text model

    channel_ids = [item["id"] for item in config.params["youtube_channels"]]

    for channel_id in channel_ids:
        try:
            video_ids = yp.get_videos_from_channel(channel_id, 2)
            for v in video_ids[:2]:
                logger.info(channel_id + " _ " + v)
                try:
                    url = "https://www.youtube.com/watch?v=" + v
                    fn, format, info = yp.get_video(url, format="mp3", download=False)
                    logger.debug(yp.is_recent(info["upload_date"]))
                    if yp.is_recent(info["upload_date"]):
                        logger.debug(
                            f"{info['channel']} | {info['title']} | {info['upload_date']}"
                        )
                        fname, format, info = yp.get_video(
                            "https://www.youtube.com/watch?v=" + v, format="mp3"
                        )
                        logger.debug(f"Duration: {info['duration_string']}")
                        transcription = ws.transcribe(fname + "." + format)
                        ntokens = llms.get_num_tokens(transcription["text"])
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
                                folder, config.params["backup_folder"] + "//" + folder
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
