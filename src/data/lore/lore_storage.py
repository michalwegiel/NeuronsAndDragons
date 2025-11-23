import glob
import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


load_dotenv()


PROJ_DIR = r"C:\Repositories\NeuronsAndDragons"
PERSIST_DIR = rf"{PROJ_DIR}\chroma_langchain_db"  # temp solution
COLLECTION = "lore"


def get_vector_store():
    db_exists = os.path.exists(PERSIST_DIR) and len(os.listdir(PERSIST_DIR)) > 0

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    if db_exists:
        return Chroma(collection_name=COLLECTION, embedding_function=embeddings, persist_directory=PERSIST_DIR)

    all_docs = []
    for path in glob.glob(f"{PROJ_DIR}/src/data/lore/lore_documents/*.*", recursive=True):
        if path.endswith((".txt", ".md")):
            with open(path, encoding="utf-8") as f:
                text = f.read()

            all_docs.append(
                {
                    "text": text,
                    "metadata": {
                        "path": path,
                        "module": os.path.dirname(path).replace("lore/", ""),
                        "file": os.path.basename(path),
                    },
                }
            )

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    doc_chunks = []
    for d in all_docs:
        for chunk in splitter.split_text(d["text"]):
            doc_chunks.append(Document(page_content=chunk, metadata=d["metadata"]))

    vectorstore = Chroma.from_documents(
        documents=doc_chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=PERSIST_DIR,
    )
    return vectorstore
