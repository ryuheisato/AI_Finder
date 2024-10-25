# 必要なライブラリのインポート
import csv
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Admin SDKの初期化
cred = credentials.Certificate('./ai-finder-4a04e-firebase-adminsdk-f1lm9-5aac28c1c0.json')  # サービスアカウントキーのパスを指定
firebase_admin.initialize_app(cred)
db = firestore.client()

# CSVファイルのパス
csv_file_path = './Final.csv'  # CSVファイルのパスを指定

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

with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader):
        batch_data.append((idx, {
            'Name': row['Name'],
            'Tagline': row['Tagline'],
            'Description': row['Description'],
            'Votes Count': int(row['Votes Count']),
            'Website': row['Website'],
            'Topic Names': row['Topic Names'].split(', '),
            'Reviews Rating': float(row['Reviews Rating']),
            'Slug': row['Slug'],
            'Thumbnail URL': row['Thumbnail URL'],
            'Created At': row['Created At'],
            'EndCursor': row['EndCursor']
        }))
        
        if len(batch_data) == batch_size:
            batch_num += 1
            write_batch(batch_data, batch_num)
            batch_data = []

    # 残りのデータをバッチ書き込み
    if batch_data:
        batch_num += 1
        write_batch(batch_data, batch_num)
