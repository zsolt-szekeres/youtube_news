# Summary

This tool does the following:
* gets the audio of select youtube videos
* generates a transcript via OpenAI whisper
* summarizes them via a combination of OpenAI's GPT API and the map reduce approach introduced at https://www.youtube.com/watch?v=qaPMdcCqtWk
* and finally sends the summary by email to you

 There are two entry points:
 * main.py offers an interactive UI via streamlit where you can pick a single youtube video and finetune prompts and other parameters
 * batch.py offers the opportunity to collect and process recent videos from your favorite channels and schedule this process say daily

# Setup 
* I started with Anaconda on Win 11 and have GPU support via pytorch+cuda for the transcription. Installed the few packages included at the top of the .py files. I included a full requirements.txt file for reference.
* I set up Gmail's two factor authentication to help send automated emails (google it)
* There are some configs in dedicated env variables:
  *   OPENAI_API_KEY
  *   GMAIL_EMAIL - your email address
  *   GMAIL_TWOFACTOR - your two factor pass
* There are some file configs:
  * edit channels.csv to include the channels you want to follow
  * edit simple_prompt where prompt length fits into your model (this version is now set to 3.5-turbo) so you don't need map reduce (this will be the default for both the UI and the batch versions)
  * edit map_prompt and combine_prompt to reflect your choice of the map reduce steps outlined in Greg's video (this will be the default for both the UI and the batch versions)
 
# Run the Interactive Version

Execute streamlit run main.py as usual go to the url shown. From here:
* Either
  * provide a direct url to a youtube video OR
  * provide the path to the pickle file generated in a previous step (This supports caching the output of previous runs.)
* You may wanna play with the prompts and the map reduce parameters chunk_size and overlap. This becomes handy when you work with the cached transcript and perform your sensitivity analysis.
* The checkbox lets you decide if you wanna have the email or just wanna play on the UI
* Pressing the button will run this thing and the UI will give you some details on the video before giving the summary.

# Run the Batch Version

Execute python batch.py. You can simply schedule a bat say in Win task scheduler to get your daily emails based on your favorite config.


