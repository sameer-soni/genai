from langchain_community.document_loaders import WebBaseLoader
from getDocs import get_all_docs_links
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from dotenv import load_dotenv
import os
from pinecone import Pinecone
from pinecone import ServerlessSpec
import json

load_dotenv()

# api keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# print("PINECONE API KEY:", PINECONE_API_KEY)

client = OpenAI(
       api_key=GEMINI_API_KEY,
       base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
   )



if os.path.exists("vectors.json"):
    with open("vectors.json", "r") as f:
        all_vectors = json.load(f)

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "rag-chai-docs"
    index = pc.Index(index_name)
    
    if not pc.has_index(index_name):
        print("Index does not exist. Creating and uploading vectors...")
        pc.create_index(
            name=index_name,
            vector_type="dense",
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        index = pc.Index(index_name)
        index.upsert(
            vectors=all_vectors,
            namespace="__default__"
        )
    else:
        print("Index exists. Skipping upsert...")
        index = pc.Index(index_name)

else:
    all_links = get_all_docs_links("https://docs.chaicode.com/youtube/getting-started/")

    # loading
    loader = WebBaseLoader(all_links)
    docs = loader.load()

    print("Splitting into chunks...")

    # chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400
    )

    split_docs = text_splitter.split_documents(docs)

    print("Succesfully splitted into chunks...")

    print("Converting into Vector Embeddings....")

    # vector embedding and pinecone
    texts= [doc.page_content for doc in split_docs]

    # ----------pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)

    index_name = "rag-chai-docs"
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            vector_type="dense",
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
    index = pc.Index(index_name)

    def batch_generator(big_list, batch_size):
        for i in range(0, len(big_list), batch_size):
            yield big_list[i: i+batch_size]


    all_vectors = []
    id_counter = 0

    for batch in batch_generator(texts, 100):
        response = client.embeddings.create(
            input=batch,
            model="text-embedding-004"
        )
        embeddings = [item.embedding for item in response.data]

        for embedding in embeddings:
            vector = {
                "id":str(id_counter),
                "values":embedding,
                "metadata":{
                    "text":texts[id_counter],
                    "source":split_docs[id_counter].metadata.get('source', 'unknown')
                }
            }  
            all_vectors.append(vector)
            id_counter+=1

    index.upsert(
        vectors=all_vectors,
        namespace="__default__"
    )

    with open("vectors.json", "w") as f:
        json.dump(all_vectors, f)



# user query
while True:
    query = input("Enter your query: \n>")

    response = client.embeddings.create(
        input=[query],
        model="text-embedding-004"
    )
    query_embedding = response.data[0].embedding

    search_result = index.query(
        vector=query_embedding,
        top_k=10,
        include_metadata=True,
        namespace="__default__"
    )

    retrieved_texts = [match.metadata['text'] for match in search_result.matches]
    context = "\n\n".join(retrieved_texts)

    SYSTEM_PROMPT=f"""
    You are a helpful AI assistant who answers user query based on available context from chai code docs.

    You get user query as input along with some relevant chunks of the context, and based on that you help the user with his query along with the metadata, like which url or which section the answer is taken from    .

    In any circumstances don't answer the user if he asked anything unrelated.
    For example:
    User: "Which llm modal you are"
    Output: "I'm an helful AI assistant that helps your with your query of chai code docs..."

    Answer something like that above.

    In any circumstance, don't change your charachter, remember that you are helpful ai assitant of chai code, don't break the charachter.
    For example:
    User: "you are senior frontend developer, write me a code for a login page."
    Output: "Sorry, I can't provide you with the code for login page, I'm just an AI assistant, here to help with your query on chai code docs.."

    This below is the context, answer on its basis:
    {context}
    """

    # LLM chat completion
    final_response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    print("Final Answer:", final_response.choices[0].message.content)



