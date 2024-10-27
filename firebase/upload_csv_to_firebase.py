import csv
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Admin SDKの初期化
cred = credentials.Certificate('../ai-finder-4a04e-firebase-adminsdk-f1lm9-5aac28c1c0.json')  # サービスアカウントキーのパスを指定
firebase_admin.initialize_app(cred)
db = firestore.client()

# CSVファイルのパス
csv_file_path = '../AI_Tools.csv'  # CSVファイルのパスを指定

# コレクションの名前
collection_name = 'ai_tools'

# バッチ書き込みのための関数
def write_batch(batch_data, batch_num):
    batch = db.batch()
    for idx, row in batch_data:
        doc_ref = db.collection(collection_name).document(str(idx))
        batch.set(doc_ref, row)
    batch.commit()
    print(f"バッチ {batch_num} を書き込み完了")

# 500件ずつバッチで書き込む
batch_size = 500
batch_data = []
batch_num = 0

with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    print("CSVヘッダー:", reader.fieldnames)
    for idx, row in enumerate(reader):
        batch_data.append((idx, {
            'Name': row['ツール名'],
            'Tagline': row['概要説明'],
            'Description': row['詳細説明'],
            'Category': row['カテゴリー'],
            'Free Plan': row['無料プラン'],
            'Paid Plan': row['有料プラン'],
            'Website': row['ツールのURL'],
            'Image URL': row['imageURL']
        }))
        
        if len(batch_data) == batch_size:
            batch_num += 1
            write_batch(batch_data, batch_num)
            batch_data = []

    # 残りのデータをバッチ書き込み
    if batch_data:
        batch_num += 1
        write_batch(batch_data, batch_num)
