import config

from langchain_openai import ChatOpenAI as LChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain

# from langchain import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

# Note this: https://github.com/kyamagu/faiss-wheels/issues/39
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

# Initialization
llm35 = LChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=config.params["auth_codes"]["OpenAI_API_key"],
)
llm4 = LChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    openai_api_key=config.params["auth_codes"]["OpenAI_API_key"],
)


def get_num_tokens(text):
    return llm35.get_num_tokens(text)


def get_config(local_config=None):

    if local_config:
        simple_prompt = local_config["simple_prompt"]
        map_prompt = local_config["map_prompt"]
        combine_prompt = local_config["combine_prompt"]
        simple_model = local_config["simple_model"]
        mapreduce_model = local_config["mapreduce_model"]
        chunk_size = int(local_config["chunk_size"])
        overlap = int(local_config["overlap"])
    else:
        map_prompt = config.params["gpt"]["map_prompt"]
        combine_prompt = config.params["gpt"]["combine_prompt"]
        simple_prompt = config.params["gpt"]["simple_prompt"]
        simple_model = config.params["gpt"]["simple_model"]
        mapreduce_model = config.params["gpt"]["mapreduce_model"]
        chunk_size = config.params["chunking"]["size"]
        overlap = config.params["chunking"]["overlap"]

    return (
        map_prompt,
        combine_prompt,
        simple_prompt,
        simple_model,
        mapreduce_model,
        chunk_size,
        overlap,
    )


def get_context_for_bot(
    query, text, local_config=None, context_num=3, context_len=1000, context_overlap=50
):

    (
        map_prompt,
        combine_prompt,
        simple_prompt,
        simple_model,
        mapreduce_model,
        chunk_size,
        overlap,
    ) = get_config(local_config)

    text_splitter_search = RecursiveCharacterTextSplitter(
        chunk_size=context_len, chunk_overlap=context_overlap
    )
    docs_search = text_splitter_search.create_documents(text)

    vector_store = Chroma.from_documents(docs_search, OpenAIEmbeddings())
    context = vector_store.max_marginal_relevance_search(
        query, k=context_num, fetch_k=context_num
    )

    # vector_store = FAISS.from_documents(docs_search, OpenAIEmbeddings())

    # docsNscores=vector_store.similarity_search_with_score(query, context_num)
    # docs = [t[0] for t in docsNscores]
    # distances = [t[1] for t in docsNscores]
    # context = [d.page_content for d in docs]

    return docs_search, context


def get_summary(text, ntokens, local_config=None):

    (
        map_prompt,
        combine_prompt,
        simple_prompt,
        simple_model,
        mapreduce_model,
        chunk_size,
        overlap,
    ) = get_config(local_config)
    # based on lvl 3 summary by Greg's video: http://www.youtube.com/watch?v=qaPMdcCqtWk
    if ntokens < 3900:
        if simple_model == "gpt-3.5-turbo":
            res = llm35(
                [SystemMessage(content=simple_prompt), HumanMessage(content=text[0])]
            )
        else:
            res = llm4(
                [SystemMessage(content=simple_prompt), HumanMessage(content=text[0])]
            )

        return (res.content, 0, 0)

    # This splitting is deterministic, however,
    # 1) not splitting within sentences may distort the  meaning of the first partial
    # sentence of the chunk, hence the corresponding summary (LIMITATION to be dealt with later)
    # 2) given that punctuation marks are often missing in the transcribed text, it's
    # hard to split by sentences using them
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap
    )
    docs = text_splitter.create_documents(text)

    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])
    combine_prompt_template = PromptTemplate(
        template=combine_prompt, input_variables=["text"]
    )

    # For some reason these do not yield deterministic partial (and complete) summaries
    # even at zero temperature
    if mapreduce_model == "gpt-3.5-turbo":
        summary_chain = load_summarize_chain(
            llm=llm35,
            chain_type="map_reduce",
            map_prompt=map_prompt_template,
            combine_prompt=combine_prompt_template,
            # verbose=True
        )
    else:
        summary_chain = load_summarize_chain(
            llm=llm4,
            chain_type="map_reduce",
            map_prompt=map_prompt_template,
            combine_prompt=combine_prompt_template,
            # verbose=True
        )

    summary = summary_chain.run(docs)

    return (summary, chunk_size, overlap)
