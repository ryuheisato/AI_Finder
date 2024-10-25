import csv
import json
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key =openai_api_key)

input_jsonl = 'batch_input.jsonl'
csv_file_path = 'exported_firestore_data.csv'

#CSVからJSONLファイルを作成
with open(csv_file_path, 'r', encoding='utf-8') as csvfile, open(input_jsonl, 'w', encoding='utf-8') as jsonlfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader):
        # ベクトル化するテキストを結合
        text_to_embed = f"Name: {row['Name']}. Tagline: {row['Tagline']}. Description: {row['Description']}"
        # DocumentIDをcustom_idとして使用
        custom_id = row['DocumentID']
        # JSONL形式で書き込み
        json_line = json.dumps({
            "custom_id": str(custom_id),
            "method": "POST",
            "url": "/v1/embeddings",
            "body": {
                "model": "text-embedding-ada-002",
                "input": text_to_embed
            }
        }, ensure_ascii=False)
        jsonlfile.write(json_line + '\n')

#JSONLファイルをアップロード
batch_input_file = client.files.create(
    file=open(input_jsonl, "rb"),
    purpose="batch"
)

batch = client.batches.create(
    input_file_id=batch_input_file.id,
    endpoint="/v1/embeddings",
    completion_window="24h",
    metadata={"description": "Embedding processing for AI tool data"}
)

batch_id = batch.id
print(f"バッチジョブが開始されました。ID: {batch_id}")

# ジョブの完了を待つ
while True:
    job_status = client.batches.retrieve(batch_id)
    print(f"ジョブの状態: {job_status.status}")
    
    if job_status.status in ['completed', 'failed']:
        break
    
    time.sleep(60) 

if job_status.status == 'completed':
    output_file = client.files.retrieve(job_status.output_file_id)
    result = client.files.content(output_file.id)
    
    # 結果をファイルに保存
    with open('embeddings.jsonl', 'wb') as f: 
        f.write(result.content) 
    print("結果が保存されました。")

    # custom_id と embedding を抽出して保存
    with open('embeddings.jsonl', 'r', encoding='utf-8') as infile, open('AItool_embeddings.jsonl', 'w', encoding='utf-8') as outfile:
        # 各行の JSON データを処理
        for line in infile:
            data = json.loads(line)
            
            # custom_id と embedding を抽出
            custom_id = data.get("custom_id")
            embedding = data.get("response", {}).get("body", {}).get("data", [])[0].get("embedding")
            
            # 新しい JSONL フォーマットに整形
            if custom_id and embedding:
                filtered_data = {
                    "custom_id": custom_id,
                    "embedding": embedding
                }
                
                # 新しいファイルに書き込む
                outfile.write(json.dumps(filtered_data) + '\n')
    
    print("custom_id と embedding のみが AItool_embeddings.jsonl に保存されました。")
else:
    print("ジョブが失敗しました。")
