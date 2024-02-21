import json
import os
import config


def get_subfolders(relative_path):

    absolute_path = os.path.abspath(relative_path)
    all_entries = os.listdir(absolute_path)
    subfolders = [
        entry
        for entry in all_entries
        if os.path.isdir(os.path.join(absolute_path, entry))
    ]

    return subfolders


def save_all(summary, transcription, info, fname, local_config=None, cloud=None):
    """
    Save summary, transcription, info and filename to a dedicated folder
    """
    folder = str.split(fname, os.sep)[0] + os.sep + str.split(fname, os.sep)[1]
    name = str.split(fname, os.sep)[2]
    subfolders = get_subfolders(folder)
    subfolders_int = list(map(int, subfolders))
    max_int = max(subfolders_int) if subfolders_int else 0
    version = str(max_int + 1)
    os.mkdir(folder + os.sep + version)
    with open(
        folder + os.sep + str(max_int + 1) + os.sep + name + "_" + version + ".html",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(summary)
    if local_config:
        with open(
            folder
            + os.sep
            + str(max_int + 1)
            + os.sep
            + name
            + "_"
            + version
            + ".json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(local_config, f, ensure_ascii=False, indent=4)
    else:
        with open(
            folder
            + os.sep
            + str(max_int + 1)
            + os.sep
            + name
            + "_"
            + version
            + ".json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                {k: config.params[k] for k in ["gpt", "chunking"]},
                f,
                ensure_ascii=False,
                indent=4,
            )
    with open(fname + "_transcript.json", "w", encoding="utf-8") as f:
        json.dump(transcription, f, ensure_ascii=False, indent=4)
    with open(fname + "_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=4)


def get_transcript(folder):
    fname = folder + str.split(folder, os.sep)[4]
    with open(fname + "_transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)
    with open(fname + "_info.json", "r", encoding="utf-8") as f:
        info = json.load(f)
    return transcript, info
