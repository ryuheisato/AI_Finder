import json
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
load_dotenv()

pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')

pc = Pinecone(api_key=pinecone_api_key)

index_name = 'ai-tools-index'

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric='cosine',  # コサイン類似度を使用
        spec=ServerlessSpec(
            cloud='aws',
            region=pinecone_environment 
        )
    )
index = pc.Index(index_name)

# JSONLファイルからEmbeddingsを読み込む
jsonl_file_path = 'AItool_embeddings.jsonl'
vectors = []

with open(jsonl_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        custom_id = data['custom_id']
        embedding = data['embedding']
        vectors.append((str(custom_id), embedding)) 

# Embeddingsをバッチでアップロード
batch_size = 100
for i in range(0, len(vectors), batch_size):
    batch = vectors[i:i+batch_size]
    index.upsert(vectors=batch)

print("EmbeddingsがPineconeにアップロードされました。")
