import logging
import argparse

import youtube_parser as yp
import youtube_transcript as yt
import speech2text as s2t
import llms
import content
import config
import os
from tqdm import tqdm


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Build knowledge base.")
    # Add arguments
    parser.add_argument(
        "-c",
        "--channel_id",
        type=str,
        default="UC2D2CMWXMOVWx7giW1n3LIg",
        help="Youtube channel ID to collect videos from.",
    )
    parser.add_argument(
        "-n", "--num_vid", type=int, default=100, help="Number of videos to collect."
    )

    # Parse arguments
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if config.params["run_mode"] == "DEBUG" else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(config.params["log_folder"], "batch_channel.log"),
        filemode="w",
    )
    logger = logging.getLogger()

    if not config.params["yt_transcript_api_enabled"]:
        ws = s2t.ws()  # initialize speech to text model

    channel_ids = [args.channel_id]
    exception_list = ["dZWngkjrFxw"]  # videos that fail for some reason

    for channel_id in channel_ids:
        try:
            video_ids = yp.get_videos_from_channel(channel_id, args.num_vid)
            video_ids = [item for item in video_ids if item not in exception_list]
            for v in tqdm(video_ids):
                logger.info(channel_id + " _ " + v)
                do_skip_rest = False
                try:
                    url = "https://www.youtube.com/watch?v=" + v
                    fname, format, info = yp.get_video(
                        url, format="mp3", download=False
                    )
                    if not os.path.exists(fname + "_transcript.json"):
                        logger.debug(
                            "Recent="
                            + str(yp.is_recent(info["upload_date"], lookback=2530))
                        )
                        if yp.is_recent(info["upload_date"], lookback=2530):
                            logger.debug(
                                info["channel"]
                                + " | "
                                + info["title"]
                                + " | "
                                + info["upload_date"]
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
                                logger.debug(f"This has  {ntokens} tokens")
                                info["ntokens"] = ntokens
                                summary, chunk_size, overlap = llms.get_summary(
                                    [transcription["text"]], ntokens
                                )
                                # myshare.send_email(summary, info)
                                logger.info("email sent")
                                content.save_all(summary, transcription, info, fname)
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
