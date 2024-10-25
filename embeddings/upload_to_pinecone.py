import json
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

# 環境変数を取得
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')

# Pineconeの初期化
pc = Pinecone(api_key=pinecone_api_key)

# インデックス名の設定
index_name = 'ai-tools-index'

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric='cosine',  # コサイン類似度を使用
        spec=ServerlessSpec(
            cloud='aws',  # ご利用のクラウドプロバイダに合わせて変更
            region=pinecone_environment  # あなたのPinecone環境に合わせて設定
        )
    )
# インデックスへの接続
index = pc.Index(index_name)

# JSONLファイルからEmbeddingsを読み込む
jsonl_file_path = 'AItool_embeddings.jsonl'
vectors = []

with open(jsonl_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        custom_id = data['custom_id']
        embedding = data['embedding']
        vectors.append((str(custom_id), embedding))  # IDは文字列である必要があります

# Embeddingsをバッチでアップロード
batch_size = 100
for i in range(0, len(vectors), batch_size):
    batch = vectors[i:i+batch_size]
    index.upsert(vectors=batch)

print("EmbeddingsがPineconeにアップロードされました。")
