import logging
import youtube_parser as yp
import myshare
import speech2text as s2t
import llms
import pickle

import config


if __name__ == '__main__': 

    #Set up logging    
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='batch.log',
    filemode='w'
    )
    logger = logging.getLogger()

    ws = s2t.ws() # initialize speech to text model

    channel_ids = [item['id'] for item in config.params['youtube_channels']]
     

    for channel_id in channel_ids:    
        try:        
            video_ids = yp.get_videos_from_channel(channel_id,2)                                   
            for v in video_ids[:2]:                
                logger.info(channel_id+' _ '+v) 
                try:
                    url = 'https://www.youtube.com/watch?v='+v
                    fn,format, info = yp.get_video(url, format='mp3', download=False)    
                    logger.debug(yp.is_recent(info['upload_date']))
                    if (yp.is_recent(info['upload_date'])):                          
                        logger.debug ( info['channel'],' | ', info['title'], ' | ',info['upload_date'])            
                        fname, format, info = yp.get_video('https://www.youtube.com/watch?v='+v, format='mp3')
                        logger.debug (f"Duration: {info['duration_string']}")
                        response = ws.transcribe(fname+'.'+format)
                        ntokens = llms.get_num_tokens(response['text'])
                        logger.debug(f'This has  {ntokens} tokens')
                        output, chunk_size, overlap = llms.get_bullets([response['text']], ntokens)                    
                        myshare.send_email(output, info)
                        logger.info('email sent')
                        data = (output, response, info, fname)
                        with open(fname+'_sum.p', "wb") as file:
                            pickle.dump(data, file)
                    else:
                        break   
                except Exception as e:            
                    logger.info("An exception occurred while sending the email: {}".format(str(e)))
                    continue
        except Exception as e2:        
            logger.info("An exception occurred with the channel: {}".format(str(channel_id)))
            logger.info("Details: {}".format(str(e2)))
            continue
