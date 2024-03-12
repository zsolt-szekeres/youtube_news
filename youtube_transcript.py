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


def get_transcript(yt_link):

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

    manually_created_languages = list(
        transcript_list._manually_created_transcripts.keys()
    )
    print(f"manually created transcript languages: {manually_created_languages}")
    generated_languages = list(transcript_list._generated_transcripts.keys())
    print(f"generated transcript languages: {generated_languages}")

    english_codes = [
        "en",
        "en-US",
        "en-GB",
        "en-CA",
        "en-AU",
        "en-NZ",
        "en-IN",
        "en-IE",
        "en-ZA",
        "en-JM",
        "en-BZ",
        "en-TT",
    ]
    try:
        # Try to fetch manually created English transcript"
        transcript = transcript_list.find_manually_created_transcript(english_codes)
    except NoTranscriptFound:
        # Try to fetch automatically generated English transcript
        try:
            transcript = transcript_list.find_generated_transcript(english_codes)
        except NoTranscriptFound:
            # Try to fetch manually created transcript in other languages
            # First in the list is probably the original language of the speaker
            try:
                transcript = transcript_list.find_manually_created_transcript(
                    manually_created_languages
                )
            except NoTranscriptFound:
                # Try to fetch automatically generated transcript in other languages
                try:
                    transcript = transcript_list.find_generated_transcript(
                        generated_languages
                    )
                except NoTranscriptFound:
                    print("No transcripts were found.")
                    return None, None
    print(f"Transcript language: {transcript.language_code}")
    # fetch the actual transcript data that is a list of dictionaries
    transcript_dicts = transcript.fetch()
    # concatenate the text from the individual dictionaries into a single string and remove line breaks
    full_transcript = " ".join(
        [dict["text"].replace("\n", " ") for dict in transcript_dicts]
    )
    return full_transcript, transcript.language_code


# print(get_transcript("https://www.youtube.com/watch?v=H6MVJm9ElMA"))
