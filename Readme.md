# フォルダとファイルの説明

## `csv_process` フォルダ

- **`remove_unworking_url.py`**: CSV ファイルから機能しない URL を削除します。URL のチェックには`requests`ライブラリを使用しています。
- **`remove_duplicated_data.py`**: CSV ファイルから重複したデータを削除します。
- **`drop_csv.py`**: 指定された列を CSV ファイルから削除します。
- **`combine_csv.py`**: 複数の CSV ファイルを 1 つに結合します。

## `firebase` フォルダ

- **`upload_csv_to_firebase.py`**: CSV ファイルのデータを Firebase Firestore にアップロードします。  
  **使用 API**: Firebase Firestore
- **`export_firestore.py`**: Firestore のデータを CSV ファイルにエクスポートします。  
  **使用 API**: Firebase Firestore

## `search_AI_tools` フォルダ

- **`filter_and_translate.py`**: ツール名でフィルタリングし、Google Apps Script を使って翻訳します。  
  **使用 API**: Google Apps Script
- **`summarize.py`**: AI ツールの詳細情報を OpenAI の API を使って要約します。  
  **使用 API**: OpenAI
- **`scraping/main.py`**: Selenium を使ってウェブサイトから AI ツールの情報をスクレイピングします。
- **`search_tools.py`**: ユーザーが入力したツール名に基づいて、ProductHunt ツール一覧から最も近い一致を検索し、結果を新しい CSV ファイルに保存します。

## `embeddings` フォルダ

- **`count_token_jsonl.py`**: JSONL ファイル内のテキストのトークン数をカウントします。
- **`find_AI_pinecone.py`**: Pinecone を使って AI ツールを検索します。  
  **使用 API**: Pinecone, OpenAI
- **`embedding_csv.py`**: CSV データを OpenAI の API を使ってベクトル化し、JSONL ファイルに保存します。  
  **使用 API**: OpenAI
- **`upload_to_pinecone.py`**: JSONL ファイルから Pinecone にベクトルをアップロードします。  
  **使用 API**: Pinecone

## `product_hunt` フォルダ

- **`main.py`**: Product Hunt API を使って AI ツールの情報を取得し、CSV ファイルに保存します。  
  **使用 API**: Product Hunt

## `faiss` フォルダ

- **`find_AI.py`**: FAISS を使って AI ツールを検索します。  
  **使用 API**: OpenAI
- **`add_data_to_faiss.py`**: JSONL ファイルから FAISS にデータを追加します。
