import os
from dotenv import load_dotenv
from langchain_community.embeddings import FakeEmbeddings
from langchain_chroma import Chroma

load_dotenv()

embeddings = FakeEmbeddings(size=384)

vectorstore = Chroma(
    collection_name="blog_memory",
    embedding_function=embeddings,
    persist_directory="./blog_memory_db"
)


def store_memory(text: str):
    vectorstore.add_texts([text])


def retrieve_memory(query: str) -> str:
    try:
        docs = vectorstore.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in docs]) if docs else ""
    except Exception:
        return ""
