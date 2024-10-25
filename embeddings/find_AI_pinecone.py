import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import concurrent.futures
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

# 環境変数を取得
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')
openai_api_key = os.getenv('OPENAI_API_KEY')


client = OpenAI(api_key =openai_api_key)

# Pineconeの初期化
pc = Pinecone(api_key=pinecone_api_key)

# Firestoreの初期化
cred = credentials.Certificate("./ai-finder-4a04e-firebase-adminsdk-f1lm9-5aac28c1c0.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Pineconeの初期化
pc = Pinecone(api_key=pinecone_api_key)

# インデックスに接続
index_name = 'ai-tools-index'
index = pc.Index(index_name)

# ユーザーからのプロンプトをベクトル化
def embed_user_prompt(prompt):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=prompt
    )
    embedding = np.array(response.data[0].embedding, dtype=np.float32)
    return embedding

# Pineconeで検索して最も類似する上位k件を取得
def search_similar_tools(prompt_embedding, top_k=15):
    response = index.query(
        vector=prompt_embedding.tolist(),
        top_k=top_k * 3,  # 候補を増やす
    )
    matches = response.matches
    similar_doc_ids = [match.id for match in matches]
    scores = [match.score for match in matches]
    return list(zip(similar_doc_ids, scores))

# URLが有効かどうかを確認する関数
def is_url_valid(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# 並列でURLを検証し、有効なツールのみを返す
def validate_urls_parallel(tools_data):
    valid_tools = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_tool = {executor.submit(is_url_valid, tool['Website']): (tool, score) for tool, score in tools_data}
        for future in concurrent.futures.as_completed(future_to_tool):
            tool, score = future_to_tool[future]
            try:
                if future.result():
                    valid_tools.append((tool, score))
                else:
                    print(f"無効なURL: {tool['Website']}")
            except Exception as e:
                print(f"Error validating URL: {tool['Website']}, Error: {e}")
    return valid_tools

# Firestoreからデータを取得し、URLを検証
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
    # 並列でURLを検証し、有効なツールのみを返す
    valid_tools = validate_urls_parallel(results)
    return valid_tools

# メイン処理
def find_best_ai_tools(user_input):
    # ユーザーの入力をEmbeddingに変換
    prompt_embedding = embed_user_prompt(user_input)
    # Pineconeで最も類似するベクトルを検索
    doc_ids_scores = search_similar_tools(prompt_embedding)
    # Firestoreからデータを取得し、URLを検証
    ai_tools_with_scores = get_tools_from_firestore(doc_ids_scores)
    # 類似度スコアでソート（高い順）
    ai_tools_with_scores.sort(key=lambda x: x[1], reverse=True)
    # 上位15件を取得
    top_ai_tools = ai_tools_with_scores[:15]
    # 投票数でソート（降順）
    top_ai_tools.sort(key=lambda x: x[0].get('vote_count', 0), reverse=True)
    return top_ai_tools

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
    print(f"Vote Count: {tool.get('vote_count', 0)}")
    print(f"Similarity Score: {score}")
    print("-" * 50)