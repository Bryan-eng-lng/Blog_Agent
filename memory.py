import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

vectorstore = Chroma(
    collection_name="blog_memory",
    embedding_function=embeddings,
    persist_directory="./blog_memory_db"
)


def store_memory(text: str):
    vectorstore.add_texts([text])


def retrieve_memory(query: str) -> str:
    docs = vectorstore.similarity_search_with_relevance_scores(query, k=3)
    relevant = [doc.page_content for doc, score in docs if score > 0.7]
    return "\n".join(relevant) if relevant else ""
