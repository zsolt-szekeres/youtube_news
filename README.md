# Summary

This tool does the following:
* gets the audio of select youtube videos
* generates a transcript via OpenAI whisper
* summarizes them via a combination of OpenAI's GPT API and LangChain's map reduce approach introduced at https://www.youtube.com/watch?v=qaPMdcCqtWk
* sends the summary by email to you
* allows to chat with the transcript of a single video
* allows to build a knowledge base of multiple videos and chat with those

 There are three entry points:
 * main.py offers an interactive UI via streamlit where you can pick a single youtube video and configure prompts and other parameters
 * batch.py offers the opportunity to collect and process recent videos from your favorite channels and schedule this process say daily
 * batch_channel.py provides collecting a longer series of videos from a single channel
 * build_knowledge_base.py helps building a knowledge base in avector store using the transcripts of videos 
 * chat.py implements a RAG (Retrieval Augmented Generator) based on transcript of a single video with tunable chunk parameters
 * chat_multiple.py implements a RAG given a pre-built vector store with tunable context parameters

# Setup 
* I started with Anaconda 202309 on Win 11 (python 3.11) and have GPU support via pytorch+cuda for the transcription. Installed the few packages included at the top of the .py files. I included a full requirements.txt file for reference.
* I set up ffmpeg. I used the local install version of Whisper with the medium model.
* I set up Gmail's two factor authentication to help send automated emails. Also set up the Youtube API and the OpenAI API.
* All config sits in config.json. The auth_code_env_vars section points to a list of environmental variables which store API keys and the Gmail two-factor pwd.
 
# Run the Interactive Version

Execute streamlit run main.py as usual go to the url shown. From here:
* Either
  * provide a direct url to a youtube video OR
  * provide the path to the folder created in a previous step (This supports caching the transcript from previous runs.)
* You may wanna play with the prompts and the map reduce parameters chunk_size and overlap. This becomes handy when you work with the cached transcript and perform your sensitivity analysis.
* The checkbox lets you decide if you wanna have the email or just wanna play on the UI
* Pressing the button will run this thing and the UI will give you some details on the video before giving the summary.
* Output will be stored in a dedicated subfolder called videos.

# Run the Batch Version

Execute python batch.py. You can simply schedule a bat say in Win task scheduler to get your daily emails based on your favorite config.
You can review what happened in batch.log.

# Run the Single Video Chat

Execute streamlit run chat.py. Pick your chunking parameters and ask away. This one builds a small vector store on the fly.

# Run the Batch Channel script

It is a command line tool. You need to provide the youtube channel ID and the number of videos to collect (going backwards from the most recent one), e.g.: 
python batch_cannel.py -c C2D2CMWXMOVWx7giW1n3LIg -n 100

# Run the Knowledge Base

It is a command line tool. You can provide some chunking parameters and spreadsheet files to store the catalogue of the knowledge base with some metadata, e.g.
python build_knowledge_base.py -s 10000 -o 1000

# Run the Multi-Video Chat

Execute streamlit run chat_multiple.py. Pick your vector store, the MMR (maximal marginal relevance) parameters, potentially the prompt and ask away. This one relies on the vector store built with previously specified chunking parameters in the above step. Ask away and get multiple perspectives on your question.

# Sample output - main.py

Here's some sample output using Greg's video:

Speech to text...

Transcribed in 3.11 mins

This has 5413 tokens

Summarizing...

chunk size=3600 , overlap=100

1. The importance of text summarization and the different levels of summarization
2. Using language models to summarize text and adjusting instructions for different types of summaries
3. Using prompt templates for summarizing longer passages of text
4. Using a template and language model to generate one-sentence summaries of essays
5. Using a map reduce method to summarize longer documents
6. Summarizing a single prompt using bullet points
7. Using "best representation vectors" to summarize an entire book
8. Selecting representative documents from a cluster of texts
9. Visualizing clusters and assigning colors to each cluster
10. Using dimensionality reduction to identify the most representative document in each cluster
11. Using a map-reduce method with GPT 3.5 Turbo to summarize sections of a book
12. Generating summaries for selected pieces of text
13. Using GPT-4 for generating a verbose summary of a book
14. The use of agents to summarize text and their reliability
15. An example of using an agent to search Wikipedia for information on Napoleon Bonaparte and Serena Williams
16. Inviting readers to share their own summarization experiences on Twitter

Summarized in 0.37 mins

# Sample output - chat_multiple.py

Question: How to sleep well?

Vector store: transcripts of about 300 Huberman videos, enriched with the name of the guest implied from the title of the episode
MMR: fetching 15 videos, using the best 5

Answer:

SOURCE: Dr. Matthew Walker

Have a wind down routine before bed, such as light stretching, meditation, reading, or listening to a relaxing podcast.
Instead of counting sheep, try taking a mental walk and visualize a pleasant environment, such as nature or a beach.
Write down any concerns or worries in a journal, at least an hour or two before bed, to help clear your mind.
Remove all clock faces from your bedroom, including your phone, to avoid checking the time during the night and causing unnecessary stress.

SOURCE: Unknown

Avoid drinking a lot of fluids right before bed to prevent waking up to use the bathroom.
Drinking water before bed can lead to fragmented REM sleep, resulting in more dream recall.
Be cautious with serotonin supplements (e.g. tryptophan, 5-HTP), as they can disrupt the timing of REM sleep and slow wave sleep.

SOURCE: AMA #2

The amount of sleep needed varies among individuals, but most adults need at least 6-8 hours of sleep per night.
Daytime sleepiness is a sign of insufficient sleep.
Increasing slow wave sleep can be achieved through resistance exercise, which triggers the release of growth hormone.
Lucid dreaming can be enhanced by setting cues, keeping a dream journal, and optimizing sleep duration.
Alcohol, marijuana, and serotonin supplements can disrupt sleep architecture.
Inositol supplementation (900mg) may help individuals fall back asleep if they wake up in the middle of the night.

SOURCE: Dr. Gina Poe

Establish a calm state before sleep through practices like deep breathing, meditation, warm bath, or a comforting book.
Estrogen may have a protective effect against PTSD and reduce activity in the locus coeruleus during REM sleep.
Sex differences exist in sleep patterns, with females experiencing more efficient sleep and denser sleep spindles during high hormonal phases.
Be cautious with sleep trackers, as excessive focus on sleep scores can lead to sleep issues and obsession.
Use sleep trackers wisely and avoid checking sleep scores immediately after waking to prevent anxiety.

SOURCE: Dr. Andy Galpin

Use non-sleep deep rest practices like yoga nidra, meditation, or deep breathing exercises to promote relaxation before sleep.
Consider using apps like Reveri for sleep hypnosis or black and white phone screens with limited notifications to minimize disruptions before sleep.
Be cautious with anti-inflammatory supplements during the recovery phase of exercise. A balanced approach is needed, as some inflammation is necessary for adaptation.
Prioritize reducing fatigue through tapering and deloading to enhance performance rather than relying solely on anti-inflammatory supplements.



