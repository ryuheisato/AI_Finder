import json
import faiss
import numpy as np
import pickle

jsonl_file_path = 'AItool_embeddings.jsonl'
embedding_dim = 1536

embeddings = []
doc_ids = []

# JSONLファイルから埋め込みベクトルを読み込む
with open(jsonl_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        embeddings.append(data['embedding'])  # 埋め込みベクトルをリストに追加
        doc_ids.append(data['custom_id'])  # DocumentIDを保存

# ベクトルをnumpy配列に変換
embeddings_np = np.array(embeddings, dtype=np.float32)

# ベクトルの正規化（コサイン類似度を使用する場合）
embeddings_np = embeddings_np / np.linalg.norm(embeddings_np, axis=1, keepdims=True)

# FAISSインデックスの作成（内積を使ったインデックス）
index = faiss.IndexFlatIP(embedding_dim)

# ベクトルをFAISSインデックスに追加
index.add(embeddings_np)

# インデックスが正しく作成されたか確認
print(f"インデックスに追加されたベクトルの数: {index.ntotal}")

# インデックスとDocumentIDのマッピングを保存
with open('index_to_doc_id.pkl', 'wb') as f:
    pickle.dump(doc_ids, f)

# FAISSインデックスの保存
faiss.write_index(index, 'ai_tools.index')

print("インデックスとIDマッピングが保存されました。")
