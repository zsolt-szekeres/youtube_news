import logging
import argparse

import youtube_parser as yp
import myshare
import speech2text as s2t
import llms
import content
import config
import os
from tqdm import tqdm


if __name__ == '__main__': 

    parser = argparse.ArgumentParser(description="Build knowledge base.")
    # Add arguments
    parser.add_argument("-c", "--channel_id", type=str, default='UC2D2CMWXMOVWx7giW1n3LIg', help="Youtube channel ID to collect videos from.")
    parser.add_argument("-n", "--num_vid", type=int, default=100, help="Number of videos to collect.")
    
    # Parse arguments
    args = parser.parse_args()

    #Set up logging    
    logging.basicConfig(
    level=logging.DEBUG if config.params['run_mode']=='DEBUG' else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='batch.log',
    filemode='w'
    )
    logger = logging.getLogger()

    ws = s2t.ws() # initialize speech to text model

    channel_ids = [args.channel_id]
    exception_list = ['dZWngkjrFxw'] # videos that fail for some reason 

    for channel_id in channel_ids:    
        try:        
            video_ids = yp.get_videos_from_channel(channel_id,args.num_vid)  
            video_ids = [item for item in video_ids if item not in exception_list]                                 
            for v in tqdm(video_ids):                
                logger.info(channel_id+' _ '+v) 
                try:
                    url = 'https://www.youtube.com/watch?v='+v
                    fn,format, info = yp.get_video(url, format='mp3', download=False)    
                    if not os.path.exists(fn+'_transcript.json'):
                        logger.debug("Recent="+str(yp.is_recent(info['upload_date'], lookback=2530)))
                        if (yp.is_recent(info['upload_date'], lookback=2530)):                          
                            logger.debug ( info['channel']+' | '+info['title']+' | '+info['upload_date'])            
                            fname, format, info = yp.get_video('https://www.youtube.com/watch?v='+v, format='mp3')
                            logger.debug (f"Duration: {info['duration_string']}")
                            transcription = ws.transcribe(fname+'.'+format)
                            ntokens = llms.get_num_tokens(transcription['text'])
                            logger.debug(f'This has  {ntokens} tokens')
                            summary, chunk_size, overlap = llms.get_summary([transcription['text']], ntokens)                    
                            #myshare.send_email(summary, info)
                            logger.info('email sent')
                            content.save_all(summary, transcription, info, fname)                        
                        else:
                            break   
                except Exception as e:            
                    logger.info("An exception occurred while sending the email: {}".format(str(e)))
                    continue
        except Exception as e2:        
            logger.info("An exception occurred with the channel: {}".format(str(channel_id)))
            logger.info("Details: {}".format(str(e2)))
            continue
