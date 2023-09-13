# Summary

This tool does the following:
* gets the audio of select youtube videos
* generates a transcript via OpenAI whisper
* summarizes them via a combination of OpenAI's GPT API and LangChain's map reduce approach introduced at https://www.youtube.com/watch?v=qaPMdcCqtWk
* and finally sends the summary by email to you

 There are two entry points:
 * main.py offers an interactive UI via streamlit where you can pick a single youtube video and finetune prompts and other parameters
 * batch.py offers the opportunity to collect and process recent videos from your favorite channels and schedule this process say daily

# Setup 
* I started with Anaconda on Win 11 and have GPU support via pytorch+cuda for the transcription. Installed the few packages included at the top of the .py files. I included a full requirements.txt file for reference.
* I set up Gmail's two factor authentication to help send automated emails (google it)
* All config sits in config.json. The auth_code_env_vars section points to a list of environmental variables which store API keys and the Gmail two-factor pwd.
 
# Run the Interactive Version

Execute streamlit run main.py as usual go to the url shown. From here:
* Either
  * provide a direct url to a youtube video OR
  * provide the path to the pickle file generated in a previous step (This supports caching the output of previous runs.)
* You may wanna play with the prompts and the map reduce parameters chunk_size and overlap. This becomes handy when you work with the cached transcript and perform your sensitivity analysis.
* The checkbox lets you decide if you wanna have the email or just wanna play on the UI
* Pressing the button will run this thing and the UI will give you some details on the video before giving the summary.
* Output will be stored in a dedicated subfolder called videos.

# Run the Batch Version

Execute python batch.py. You can simply schedule a bat say in Win task scheduler to get your daily emails based on your favorite config.
You can review what happened in batch.log.

# Output

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


