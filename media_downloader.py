import yt_dlp
import feedparser
import os
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
import logging

import config

logger = logging.getLogger(__name__)


class MediaDownloader:
    def __init__(
        self,
        config,
        days_limit=2,
        lookback_days=config.params["lookback_days"],
        output_format="mp3",
    ):
        self.yt_api_key = config.params["auth_codes"]["Youtube_API_key"]
        self.days_limit = days_limit
        self.lookback_days = lookback_days
        self.save_path = config.params["videos_folder"]
        self.output_format = output_format

    def _is_recent(self, date, lookback=None) -> bool:
        if not lookback:
            lookback = self.lookback_days
        time_difference = datetime.now() - date
        time_limit = timedelta(days=lookback)
        return time_difference < time_limit

    def _youtube_api_request(self, url_params):
        base_url = "https://www.googleapis.com/youtube/v3/search?"
        try:
            response = requests.get(base_url + urlencode(url_params))
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error making request: {e}")
            return None

    def download_from_youtube(self, channel_id: str, max_results: int = 10) -> list:
        video_ids = self._get_videos_from_channel(channel_id, max_results)
        videos = []
        for vid in video_ids:
            url = f"https://www.youtube.com/watch?v={vid}"
            videos.append(self._get_audio_from_youtube(url))
        return videos

    def download_from_rss_podcast(self, rss_url: str, num_episodes: int = 1) -> list:
        feed = feedparser.parse(rss_url)
        downloaded_episodes = []
        for entry in feed.entries[:num_episodes]:
            episode_date = datetime(*entry.published_parsed[:6])
            if self._is_recent(episode_date, self.days_limit):
                mp3_url = entry.enclosures[0].href
                file_name = os.path.join(
                    self.save_path, entry.title.replace(" ", "_") + ".mp3"
                )
                try:
                    response = requests.get(mp3_url, stream=True)
                    response.raise_for_status()
                    with open(file_name, "wb") as mp3_file:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                mp3_file.write(chunk)
                    downloaded_episodes.append(file_name)
                except requests.RequestException as e:
                    logger.error(f"Error downloading podcast episode: {e}")
        return downloaded_episodes

    def _get_audio_from_youtube(self, url: str) -> tuple:
        ytdl_opts = {
            "format": "bestaudio",
            "outtmpl": os.path.join(
                self.save_path, "%(title)s/%(title)s.%(ext)s"
            ),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.output_format,
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            info_dict = ytdl.extract_info(url, download=True)
            audio_filename = ytdl.prepare_filename(info_dict)

        return audio_filename[:-5], self.output_format, info_dict

    def _get_videos_from_channel(self, channel_id: str, max_results: int = 10) -> list:
        url_params = {
            "part": "snippet",
            "channelId": channel_id,
            "key": self.yt_api_key,
            "order": "date",
            "maxResults": max_results,
            "type": "video",
        }

        response = self._youtube_api_request(url_params)
        if not response:
            return []

        video_ids = [item["id"]["videoId"] for item in response["items"]]

        while ("nextPageToken" in response) and (len(video_ids) < max_results):
            url_params["pageToken"] = response["nextPageToken"]
            response = self._youtube_api_request(url_params)
            if not response:
                break
            video_ids += [item["id"]["videoId"] for item in response["items"]]

        return video_ids
