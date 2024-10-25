from openai import OpenAI
import faiss
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
import pickle
import requests
import concurrent.futures
import os
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key =openai_api_key)

cred = credentials.Certificate("./ai-finder-4a04e-firebase-adminsdk-f1lm9-5aac28c1c0.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

index = faiss.read_index("./ai_tools.index")

# IDマッピングの読み込み
with open('index_to_doc_id.pkl', 'rb') as f:
    index_to_doc_id = pickle.load(f)

# ユーザーからのプロンプトをベクトル化
def embed_user_prompt(prompt):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=prompt
    )
    embedding = np.array(response.data[0].embedding, dtype=np.float32)
    # ベクトルの正規化
    embedding = embedding / np.linalg.norm(embedding)
    return embedding

# FAISSで検索して最も類似する上位k件を取得
def search_similar_tools(prompt_embedding, top_k=5):
    prompt_embedding = np.array([prompt_embedding], dtype='float32')
    # ベクトルの正規化
    prompt_embedding = prompt_embedding / np.linalg.norm(prompt_embedding, axis=1, keepdims=True)

    # インデックスに検索を実行
    try:
        D, I = index.search(prompt_embedding, top_k * 2)  # 候補を増やす
        # インデックスからDocumentIDを取得
        similar_doc_ids = [index_to_doc_id[i] for i in I[0]]
        distances = D[0]
        return list(zip(similar_doc_ids, distances))
    except Exception as e:
        print(f"Error during search: {e}")
        return []


# Firestoreからデータを取得
def get_tools_from_firestore(doc_ids_scores):
    results = []
    for doc_id, score in doc_ids_scores:
        try:
            doc_ref = db.collection('ai_tools').document(str(doc_id))
            doc = doc_ref.get()
            if doc.exists:
                tool_data = doc.to_dict()
                results.append((tool_data, score))
            else:
                print(f"Document {doc_id} does not exist.")
        except Exception as e:
            print(f"Error retrieving document {doc_id}: {e}")
    return results

# メイン処理
def find_best_ai_tools(user_input):
    # ユーザーの入力をそのままEmbeddingに使用
    prompt_embedding = embed_user_prompt(user_input)
    # FAISSで最も類似するベクトルを検索
    doc_ids_scores = search_similar_tools(prompt_embedding)
    # Firestoreからデータを取得し、URLを検証
    ai_tools_with_scores = get_tools_from_firestore(doc_ids_scores)
    # 類似度スコアでソート（高い順）
    ai_tools_with_scores.sort(key=lambda x: x[1], reverse=True)
    # 上位5件を返す
    return ai_tools_with_scores[:5]

# ユーザーのプロンプトに基づいてAIツールを取得
user_input = input("どんなAIツールを探していますか？\nツールの特徴や目的を教えてください: ")

# AIツールを検索
top_ai_tools = find_best_ai_tools(user_input)

# 結果を表示
for idx, (tool, score) in enumerate(top_ai_tools, 1):
    print(f"Top {idx} AI Tool:")
    print(f"Name: {tool['Name']}")
    print(f"Description: {tool['Description']}")
    print(f"URL: {tool['Website']}")
    print(f"Similarity Score: {score}")
    print("-" * 50)