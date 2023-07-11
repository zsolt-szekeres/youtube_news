import yt_dlp

def get_video(url, format='mp3', download=True):

    ytdl_opts = {
    'format': 'bestaudio',
    'outtmpl': 'videos/%(title)s/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': format,
        'preferredquality': '192',
    }],
    'forceduration':True,
    'forcethumbnail': True,
    'writethumbnail': True
    }
    
    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
        info_dict = ytdl.extract_info(url, download=download)
        audio_filename = ytdl.prepare_filename(info_dict)

    return (audio_filename[:-5],format, info_dict)
