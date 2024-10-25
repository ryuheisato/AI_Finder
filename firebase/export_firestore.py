import csv
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Admin SDKの初期化
cred = credentials.Certificate('./ai-finder-4a04e-firebase-adminsdk-f1lm9-5aac28c1c0.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Firestoreのコレクションを取得
collection_name = 'ai_tools'
docs = db.collection(collection_name).stream()

# CSVファイルにデータを書き出す
csv_file_path = 'exported_firestore_data.csv'

with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['DocumentID', 'Name', 'Tagline', 'Description', 'Votes Count', 'Website', 'Topic Names', 'Reviews Rating', 'Slug', 'Thumbnail URL', 'Created At', 'EndCursor']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # ヘッダーの書き込み
    writer.writeheader()

    # FirestoreのデータをCSVに書き込む
    for doc in docs:
        data = doc.to_dict()
        data['DocumentID'] = doc.id
        writer.writerow(data)

print(f"Firestoreのデータを {csv_file_path} にエクスポートしました。")