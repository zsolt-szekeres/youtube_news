import config

from langchain.chat_models import ChatOpenAI as LChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate
from langchain.schema import (
    HumanMessage,
    SystemMessage
)

# Initialization
llm35 = LChatOpenAI(model_name='gpt-3.5-turbo',temperature=0, openai_api_key=config.params['auth_codes']['OpenAI_API_key'])

def get_num_tokens(text):    
    return llm35.get_num_tokens(text)

def get_bullets(text, ntokens, map_prompt=config.params['gpt_prompts']['map_prompt'], \
                combine_prompt = config.params['gpt_prompts']['combine_prompt'], \
                simple_prompt=config.params['gpt_prompts']['simple_prompt'], \
                chunk_size=config.params['chunking']['size'], 
                overlap=config.params['chunking']['overlap']):

    if ntokens < 3900:              
        res=llm35([SystemMessage(content=simple_prompt),\
                   HumanMessage(content=text[0])])

        return (res.content, 0, 0)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    docs = text_splitter.create_documents(text)

    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])
    combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])

    summary_chain = load_summarize_chain(llm=llm35,
                                    chain_type='map_reduce',
                                    map_prompt=map_prompt_template,
                                    combine_prompt=combine_prompt_template,
#                                      verbose=True
                                    )
    
    summary = summary_chain.run(docs)
    return (summary, chunk_size, overlap)



