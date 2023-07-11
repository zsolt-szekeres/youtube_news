import logging
import scrapetube
import youtube_parser as yp
from datetime import datetime, timedelta
import myshare
import speech2text as s2t
import llms
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='batch.log',
    filemode='w'
)

logger = logging.getLogger()

def is_recent(date_string):
    # Convert the string to a datetime object
    date_format = '%Y%m%d'
    date = datetime.strptime(date_string, date_format)
    
    # Calculate the time difference between the current date and the given date
    time_difference = datetime.now() - date
    time_limit = timedelta(days=2)

    return (time_difference < time_limit)
    
channel_urls = pd.read_csv('channels.csv')['channels'].tolist()

ws = s2t.ws() 
for channel_url in channel_urls:
    videos = list(scrapetube.get_channel(channel_url=channel_url,sort_by='newest'))
    for v in videos[:2]:        
        # Get only the two most recent videos from each channel        
        logger.info(channel_url+' _ '+v['videoId']) 
        try:
            # Handle exceptions to make sure a single hickup doesn't prevents other videos to be summarized
            url = 'https://www.youtube.com/watch?v='+v['videoId']
            fn,format, info_dict = yp.get_video(url, format='mp3', download=False)    
            print (is_recent(info_dict['upload_date']))
            if (is_recent(info_dict['upload_date'])):      
                logger.info(info_dict['channel']+' | '+ v['title']['runs'][0]['text']+' | '+info_dict['upload_date'])       
                print ( info_dict['channel'],' | ', v['title']['runs'][0]['text'], ' | ',info_dict['upload_date'])            
                #msg.append(info_dict['channel']+' | '+v['title']['runs'][0]['text']+' | '+info_dict['upload_date'])
                fname, format, info = yp.get_video('https://www.youtube.com/watch?v='+v['videoId'], format='mp3')
                print (f"Duration: {info['duration_string']}")
                response = ws.transcribe(fname+'.'+format)
                ntokens = llms.get_num_tokens(response['text'])
                print(f'This has  {ntokens} tokens')
                output, chunk_size, overlap = llms.get_bullets([response['text']], ntokens)
                myshare.send_email(output, info['title'], url)
                logger.info('email sent')
            else:
                break   
        except:
            continue
