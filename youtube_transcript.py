from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)


def get_video_id(url):
    if "youtube.com" in url and "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be" in url or "youtube.com/shorts/" in url:
        return url.split("/")[-1]
    else:
        print("Invalid YouTube link")
        return None


def get_transcript(yt_link, do_assert=False):

    # get the video id from the link
    video_id = get_video_id(yt_link)
    if video_id is None:
        return None, None

    # retrieve the available transcripts
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        print("Transcripts are disabled for this video")
        return None, None

    try:
        # Try to fetch the "en-US" transcript
        transcript = transcript_list.find_transcript(["en-US"])
    except NoTranscriptFound:
        try:
            # If "en-US" doesn't exist, try to fetch the "en" transcript
            transcript = transcript_list.find_transcript(["en"])
        except NoTranscriptFound:
            print("Neither 'en-US' nor 'en' transcripts were found.")
            return None, None

    # fetch the actual transcript data that is a list of dictionaries
    transcript_dicts = transcript.fetch()
    # concatenate the text from the individual dictionaries into a single string and remove line breaks
    full_transcript = " ".join(
        [dict["text"].replace("\n", " ") for dict in transcript_dicts]
    )

    # transcript_dicts contains start time of each subtitle line
    # here we add for each line the start_charnum and end_charnum wrt. full transcript
    # end_charnum is non-inclusive wrt. the text line
    for i in range(len(transcript_dicts)):
        if i == 0:
            transcript_dicts[i]["text"] = transcript_dicts[i]["text"].replace("\n", " ")
            transcript_dicts[i]["start_charnum"] = 0
            transcript_dicts[i]["end_charnum"] = len(transcript_dicts[i]["text"])
        else:
            transcript_dicts[i]["text"] = " " + transcript_dicts[i]["text"].replace(
                "\n", " "
            )
            transcript_dicts[i]["start_charnum"] = transcript_dicts[i - 1][
                "end_charnum"
            ]
            transcript_dicts[i]["end_charnum"] = transcript_dicts[i][
                "start_charnum"
            ] + len(transcript_dicts[i]["text"])

    if do_assert:
        # check for each element in the list if the start_charnum and end_charnum are correct
        for i in range(len(transcript_dicts)):
            assert (
                full_transcript[
                    transcript_dicts[i]["start_charnum"] : transcript_dicts[i][
                        "end_charnum"
                    ]
                ]
                == transcript_dicts[i]["text"],
                "Error in the start_charnum and end_charnum",
            )
    return full_transcript, transcript_dicts
