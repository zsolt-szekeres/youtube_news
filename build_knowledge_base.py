import time
import os
import json
import pandas as pd
from pathlib import Path

from tqdm import tqdm
import argparse

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

import config

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Build knowledge base.")
    # Add arguments
    parser.add_argument(
        "-p", "--prev_inv", type=str, default=" ", help="Previous inventory file."
    )
    parser.add_argument(
        "-n",
        "--new_inv",
        type=str,
        default=r"inventory.xlsx",
        help="New inventory file.",
    )
    parser.add_argument(
        "-s", "--chunk_size", type=int, default=10000, help="Chunk size in tokens."
    )
    parser.add_argument(
        "-o",
        "--chunk_overlap",
        type=int,
        default=1000,
        help="Overlap of chunks in tokens.",
    )

    # Parse arguments
    args = parser.parse_args()

    folders = os.listdir(os.path.join(os.getcwd(), "videos"))
    inventory = {}

    text_splitter_search = RecursiveCharacterTextSplitter(
        chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap
    )
    base_directory = config.params["vector_store"]
    if args.prev_inv != " ":
        previous_inventory = pd.read_excel(args.prev_inv)
        loaded = previous_inventory["id"].tolist()
    else:
        loaded = []

    for f in tqdm(folders):
        transcript_file = os.path.join(
            "videos", os.path.join(f, f + "_transcript.json")
        )
        info_file = os.path.join("videos", os.path.join(f, f + "_info.json"))
        print(info_file, transcript_file)
        if os.path.exists(transcript_file) & os.path.exists(info_file):
            with open(info_file, "r", encoding="utf-8") as file:
                info = json.load(file)
            try:
                if info["id"] not in loaded:
                    title = info["title"]
                    inventory[title] = {}
                    inventory[title]["title"] = title
                    inventory[title]["id"] = info["id"]
                    inventory[title]["channel"] = info["channel"]
                    try:
                        inventory[title]["like_count"] = info["like_count"]
                    except:
                        inventory[title]["like_count"] = -1
                    inventory[title]["upload_date"] = info["upload_date"]
                    inventory[title]["original_url"] = info["original_url"]
                    inventory[title]["duration"] = info["duration"]
                    inventory[title]["duration_string"] = info["duration_string"]
                    if (info["channel"] == "Andrew Huberman") or (
                        info["channel"] == "Lex Fridman"
                    ):
                        guest = title.split(":")[0]
                        if guest.count(" ") < 3:
                            inventory[title]["guest"] = guest
                        else:
                            guest = "Unknown"
                            inventory[title]["guest"] = guest
                        try:
                            text = json.loads(Path(transcript_file).read_text())["text"]
                            docs_search = text_splitter_search.create_documents([text])
                            for d in docs_search:
                                d.metadata = {
                                    "host": info["channel"],
                                    "guest": guest,
                                    "upload_date": info["upload_date"],
                                    "id": info["id"],
                                }
                            persist_directory = (
                                base_directory
                                + "/"
                                + info["channel"]
                                + "_"
                                + str(args.chunk_size)
                                + "_"
                                + str(args.chunk_overlap)
                            )
                            db = Chroma.from_documents(
                                docs_search,
                                OpenAIEmbeddings(),
                                persist_directory=persist_directory,
                            )
                            inventory[title]["in_db"] = 1
                        except:
                            print("Exception: " + guest)
            except:
                print("Exception: ", title)

    new_inventory = pd.DataFrame(inventory).T

    if args.prev_inv != " ":
        result = pd.concat([previous_inventory, new_inventory], ignore_index=True)
    else:
        result = new_inventory

    result.to_excel(args.new_inv, index=False)
    # pd.DataFrame(inventory).T.to_excel('inventory_20231009.xlsx', index=False)

    print(db._collection.count())
