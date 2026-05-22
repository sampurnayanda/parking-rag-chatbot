import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "parking-chatbot-index"


def create_rag_pipeline():

    # 1. Load and split
    loader = TextLoader("data/parking_info.txt")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    docs = splitter.split_documents(documents)

    # 2. Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # 3. Pinecone index — delete and recreate to force fresh index
    existing_indexes = [i.name for i in pc.list_indexes()]
    if INDEX_NAME in existing_indexes:
        pc.delete_index(INDEX_NAME)

    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

    # 4. Vector store — always re-index from current parking_info.txt
    vectorstore = PineconeVectorStore.from_documents(
        docs, embeddings, index_name=INDEX_NAME
    )

    # 5. Retriever — k=5 to get more relevant chunks
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # 6. LLM — keep gemma-4-31b-it
    llm = ChatGoogleGenerativeAI(
        model="gemma-4-31b-it",
        temperature=0.1
    )

    # 7. Callable with a minimal prompt Gemma won't echo back
    def qa_chain(query):
        question = query["query"]
        relevant_docs = retriever.get_relevant_documents(question)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # Keep prompt short and natural — no numbered lists or "Constraint:" labels
        # Gemma echoes back anything that looks like structured instructions
        prompt = (
            "Parking info:\n{context}\n\n"
            "Q: {question}\n"
            "A:"
        ).format(context=context, question=question)

        response = llm.invoke([HumanMessage(content=prompt)])

        raw = response.content
        if isinstance(raw, list):
            raw = " ".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in raw
            )

        # If Gemma put "A:" in output, take only what comes after
        raw = str(raw)
        if "A:" in raw:
            raw = raw.split("A:")[-1].strip()

        return {"result": raw}

    return qa_chain