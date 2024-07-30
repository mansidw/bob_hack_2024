from langchain_community.document_loaders import WebBaseLoader
from data import links
import os
from dotenv import load_dotenv, find_dotenv
import re

load_dotenv(find_dotenv())

for i in links["other-services"]:
    loader = WebBaseLoader(i)
    data = loader.load()
    match = re.search(r"^(?:[^/]*\/){5}(.*)", i)

    # Extract the matched group
    if match:
        result = match.group(1)
    else:
        result = ""

    directory = "service-data/other-services"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write to the file
    file_path = os.path.join(directory, result + ".txt")

    for doc in data:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(doc.page_content.replace("\n", ""))
