# Dockerfile

## Changes
```kubernetes/gke/Dockerfile``` is different from ```kubernetes/minikube/Dockerfile``` in the way of passing ```config.json``` to the container.
```bash
$ diff -y kubernetes/minikube/Dockerfile kubernetes/gke/Dockerfile 
...
# Set the entrypoint:                                           # Set the entrypoint: 
# - copy /etc/config/config.json to /youtube_news/config.json | # - copy $CONFIG_JSON env var to /youtube_news/config.json
# - create output folders                                       # - create output folders
# - activate the virtual environment                            # - activate the virtual environment
RUN echo '#!/bin/bash\n\                                        RUN echo '#!/bin/bash\n\
cp /etc/config/config.json /youtube_news/config.json\n\       | echo $CONFIG_JSON > /youtube_news/config.json\n\
mkdir -p /data/log /data/videos /data/backup /data/vector_sto   mkdir -p /data/log /data/videos /data/backup /data/vector_sto
source /youtube_news/env/bin/activate\n\                        source /youtube_news/env/bin/activate\n\
"$@"' > /entrypoint.sh \                                        "$@"' > /entrypoint.sh \
&& chmod +x /entrypoint.sh                                      && chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]                                 ENTRYPOINT [ "/entrypoint.sh" ]
...
```
Only GKE kubernetes, minikube or, in general, kubernetes environments support ConfigMap with json variables.
E.g., see, ConfigMap ```yt-news-config-json``` in ```kubernetes/minikube/yt_news_deployment.yaml```)

Other environments that run docker containers do not support configmaps with json variables. E.g. Google Batch Jobs are like that.
Hence we keep the more generic solution, reading config.json dumps as normal runtime environment variable.

Notes: different ways to provide config.json file to the application
* We could COPY config.json at the build stage of docker image, but then we should deploy a new docker image at each change of config.json.
* We could also give a command line argument ```--config-json-file=/path/to/config.json``` to the application, but in this case, at the entrypoint we should first copy from a Storage the json file in the container.
* We can pass the contents of the config.json file as a runtime environment variable, and overwrite ```/youtube_news/config.json``` at the entrypoint.  This is where the application is reading the config.json file.
* GKE kubernetes environment supports ConfigMaps using json file variables, that will be automatically mounted to ```/etc/config```.


## Create small docker image, without pytorch and cuda support.

Install python environment without pytorch:
```bash
cd youtube_news-workspace/youtube_news/
. .venv-small/bin/activate
pip install --upgrade --no-cache-dir pip==24.0
pip install --upgrade --no-cache-dir setuptools==69.1.0
pip install streamlit
pip install langchain langchain-openai
pip install yt_dlp
pip install feedparser
pip install youtube_transcript_api
pip freeze > requirements_py3.11_nocuda.txt
```

## Build docker image
```bash
docker build -t youtube_news:main . -f dockerize/Dockerfile
```
The image size is huge, 6.64GB. ~5.4GB is consumed by python virtual environment.


## Builder docker without cuda and pytorch
```bash
docker build -t youtube_news:main . -f dockerize/Dockerfile.nocuda
```
The image size is 1.13GB: 500MB is consumed by ffmpeg libraries, 500MB is consumed by python virtual environment.

You can use this docker image in case of ```"yt_transcript_api_enabled": true``` in config.json. In this case the applicaiton does not try to load OpenAI whisper model.


## Test docker image

Create host local folder where container /data folder will be mounted:
```bash
sudo mkdir -p /volumes/youtube-news/data
```

```bash
docker run \
    --rm  \
    -v /volumes/youtube-news/data:/data \
    -e YOUTUBE_API_KEY="<your_youtube_api_key>" \
    -e OPENAI_API_KEY="<your_openai_api_key>" \
    -e GMAIL_TWOFACTOR="<yout_gmail_twofactor_app_password>" \
    -e CONFIG_JSON="{\"youtube_channels\":[{\"id\":\"UCNJ1Ymd5yFuUPtn21xtRbbw\",\"descriptor\":\"AI-Explained\"},{\"id\":\"UCSHZKyawb77ixDdsGog4iWA\",\"descriptor\":\"Lex Fridman\"},{\"id\":\"UCwD5YYkbYmN2iFHON9FyDXg\",\"descriptor\":\"David Sinclair\"},{\"id\":\"UC2D2CMWXMOVWx7giW1n3LIg\",\"descriptor\":\"Huberman\"},{\"id\":\"UCAuUUnT6oDeKwE6v1NGQxug\",\"descriptor\":\"TED\"},{\"id\":\"UCyR2Ct3pDOeZSRyZH5hPO-Q\",\"descriptor\":\"Data Independent\"},{\"id\":\"UCvKRFNawVcuz4b9ihUTApCg\",\"descriptor\":\"4IR with David Shapiro\"},{\"id\":\"UCK7tJXHCdxWpA4Q5349wfkw\",\"descriptor\":\"Invisible Machines\"}],\"gpt\":{\"simple_model\":\"gpt-3.5-turbo\",\"mapreduce_model\":\"gpt-3.5-turbo\",\"simple_prompt\":\"Summarize the context provided by the user. Return your response in html as ordered list, which covers the key points of the text.\",\"map_prompt\":\" Write a concise summary of the following: '{text}' CONCISE SUMMARY:\",\"combine_prompt\":\"Analyze the following text and extract the  most crucial points. Return your summary in HTML as an ordered list. '{text}' \"},\"chunking\":{\"size\":6000,\"overlap\":300},\"lookback_days\":1,\"run_mode\":\"DEBUG\",\"auth_codes_env_vars\":{\"Youtube_API_key\":\"YOUTUBE_API_KEY\",\"OpenAI_API_key\":\"OPENAI_API_KEY\",\"GMAIL_two_factor_password\":\"GMAIL_TWOFACTOR\"},\"email\":{\"sender_email\":\"your@email\",\"receiver_emails\":[\"user1@email\", \"user2@email\"]},\"log_folder\":\"/data/log\",\"videos_folder\":\"/data/videos\",\"backup_folder\":\"/data/backup\",\"vector_store\":\"/data/vector_store\",\"yt_transcript_api_enabled\":\"true\"}" \
    youtube_news:main python batch.py
```

```bash
docker run \
    --rm  \
    -v /volumes/youtube-news/data:/data \
    -e YOUTUBE_API_KEY="<your_youtube_api_key>" \
    -e OPENAI_API_KEY="<your_openai_api_key>" \
    -e GMAIL_TWOFACTOR="<yout_gmail_twofactor_app_password>" \
    -e CONFIG_JSON="{\"youtube_channels\":[{\"id\":\"UCNJ1Ymd5yFuUPtn21xtRbbw\",\"descriptor\":\"AI-Explained\"},{\"id\":\"UCSHZKyawb77ixDdsGog4iWA\",\"descriptor\":\"Lex Fridman\"},{\"id\":\"UCwD5YYkbYmN2iFHON9FyDXg\",\"descriptor\":\"David Sinclair\"},{\"id\":\"UC2D2CMWXMOVWx7giW1n3LIg\",\"descriptor\":\"Huberman\"},{\"id\":\"UCAuUUnT6oDeKwE6v1NGQxug\",\"descriptor\":\"TED\"},{\"id\":\"UCyR2Ct3pDOeZSRyZH5hPO-Q\",\"descriptor\":\"Data Independent\"},{\"id\":\"UCvKRFNawVcuz4b9ihUTApCg\",\"descriptor\":\"4IR with David Shapiro\"},{\"id\":\"UCK7tJXHCdxWpA4Q5349wfkw\",\"descriptor\":\"Invisible Machines\"}],\"gpt\":{\"simple_model\":\"gpt-3.5-turbo\",\"mapreduce_model\":\"gpt-3.5-turbo\",\"simple_prompt\":\"Summarize the context provided by the user. Return your response in html as ordered list, which covers the key points of the text.\",\"map_prompt\":\" Write a concise summary of the following: '{text}' CONCISE SUMMARY:\",\"combine_prompt\":\"Analyze the following text and extract the  most crucial points. Return your summary in HTML as an ordered list. '{text}' \"},\"chunking\":{\"size\":6000,\"overlap\":300},\"lookback_days\":1,\"run_mode\":\"DEBUG\",\"auth_codes_env_vars\":{\"Youtube_API_key\":\"YOUTUBE_API_KEY\",\"OpenAI_API_key\":\"OPENAI_API_KEY\",\"GMAIL_two_factor_password\":\"GMAIL_TWOFACTOR\"},\"email\":{\"sender_email\":\"your@email\",\"receiver_emails\":[\"user1@email\", \"user2@email\"]},\"log_folder\":\"/data/log\",\"videos_folder\":\"/data/videos\",\"backup_folder\":\"/data/backup\",\"vector_store\":\"/data/vector_store\",\"yt_transcript_api_enabled\":\"true\"}" \
    youtube_news:main python batch_channel.py -n 3
```

```bash
docker run \
    --rm  \
    -p 5001:5000 \
    -v /volumes/youtube-news/data:/data \
    -e YOUTUBE_API_KEY="<your_youtube_api_key>" \
    -e OPENAI_API_KEY="<your_openai_api_key>" \
    -e GMAIL_TWOFACTOR="<yout_gmail_twofactor_app_password>" \
    -e CONFIG_JSON="{\"youtube_channels\":[{\"id\":\"UCNJ1Ymd5yFuUPtn21xtRbbw\",\"descriptor\":\"AI-Explained\"},{\"id\":\"UCSHZKyawb77ixDdsGog4iWA\",\"descriptor\":\"Lex Fridman\"},{\"id\":\"UCwD5YYkbYmN2iFHON9FyDXg\",\"descriptor\":\"David Sinclair\"},{\"id\":\"UC2D2CMWXMOVWx7giW1n3LIg\",\"descriptor\":\"Huberman\"},{\"id\":\"UCAuUUnT6oDeKwE6v1NGQxug\",\"descriptor\":\"TED\"},{\"id\":\"UCyR2Ct3pDOeZSRyZH5hPO-Q\",\"descriptor\":\"Data Independent\"},{\"id\":\"UCvKRFNawVcuz4b9ihUTApCg\",\"descriptor\":\"4IR with David Shapiro\"},{\"id\":\"UCK7tJXHCdxWpA4Q5349wfkw\",\"descriptor\":\"Invisible Machines\"}],\"gpt\":{\"simple_model\":\"gpt-3.5-turbo\",\"mapreduce_model\":\"gpt-3.5-turbo\",\"simple_prompt\":\"Summarize the context provided by the user. Return your response in html as ordered list, which covers the key points of the text.\",\"map_prompt\":\" Write a concise summary of the following: '{text}' CONCISE SUMMARY:\",\"combine_prompt\":\"Analyze the following text and extract the  most crucial points. Return your summary in HTML as an ordered list. '{text}' \"},\"chunking\":{\"size\":6000,\"overlap\":300},\"lookback_days\":1,\"run_mode\":\"DEBUG\",\"auth_codes_env_vars\":{\"Youtube_API_key\":\"YOUTUBE_API_KEY\",\"OpenAI_API_key\":\"OPENAI_API_KEY\",\"GMAIL_two_factor_password\":\"GMAIL_TWOFACTOR\"},\"email\":{\"sender_email\":\"your@email\",\"receiver_emails\":[\"user1@email\", \"user2@email\"]},\"log_folder\":\"/data/log\",\"videos_folder\":\"/data/videos\",\"backup_folder\":\"/data/backup\",\"vector_store\":\"/data/vector_store\",\"yt_transcript_api_enabled\":\"true\"}" \
    youtube_news:main streamlit run main.py --server.port 5000
```