import pandas as pd
import difflib
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

translate_url = os.getenv("GOOGLE_TRANSLATE_API_URL")
# CSVファイルの読み込み
input_csv_file = 'ProductHuntToolsList.csv'  # 元のCSVファイル名
output_csv_file = 'Add_tools.csv'  # 抽出後のCSVファイル名

# ツール名の一覧を入力として受け取る（カンマ区切り）
tool_names_input = input("ツール名を入力してください（カンマ区切り）: ")
tool_names = [name.strip() for name in tool_names_input.split(',')]  # リストに変換して空白をトリム

# CSVファイルを読み込み
df = pd.read_csv(input_csv_file)

# 既存のadd_tools.csvファイルを読み込む（存在しない場合は空のDataFrameを作成）
try:
    existing_df = pd.read_csv(output_csv_file)
    # 列名を変更
    existing_df.columns = ['ツール名', '概要説明', '詳細説明', 'カテゴリー', '無料プラン', '有料プラン', 'ツールのURL', 'imageURL']
except FileNotFoundError:
    existing_df = pd.DataFrame(columns=['ツール名', '概要説明', '詳細説明', 'カテゴリー', '無料プラン', '有料プラン', 'ツールのURL', 'imageURL'])

# Google Apps Scriptでデプロイした翻訳APIのURLを設定
url = translate_url

# 部分一致で最も近いツールを検索し、結果をフィルタリング
filtered_rows = []
for tool_name in tool_names:
    # difflibを使って最も一致するツール名を見つける
    possible_matches = difflib.get_close_matches(tool_name, df['Name'].astype(str), n=1, cutoff=0.1)
    
    if possible_matches:
        # 最も近い一致を取得し、その行をフィルタリング
        closest_match = possible_matches[0]
        matched_row = df[df['Name'] == closest_match]
        
        if not matched_row.empty:
            # Tagline, Description, Topic Namesを取得
            tagline = matched_row['Tagline'].iloc[0] if 'Tagline' in matched_row.columns else ''
            description = matched_row['Description'].iloc[0] if 'Description' in matched_row.columns else ''
            topic_names = matched_row['Topic Names'].iloc[0] if 'Topic Names' in matched_row.columns else ''
            
            # 翻訳APIに送信するデータを準備
            data = {
                "topicNames": topic_names,
                "tagline": tagline,
                "description": description,
                "source": "en",
                "target": "ja"
            }
            
            # POSTリクエストを送信
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
            
            # レスポンスの確認
            if response.status_code == 200:
                translated_data = response.json()
                # 翻訳されたデータでmatched_rowを更新
                translated_topics = translated_data.get('translated topicNames', topic_names)

                # カテゴリーの形式を変更: 全角の「、」を半角の「, 」に置き換え
                formatted_topics = (
                            translated_topics
                            .strip("[]")                     # 角括弧を削除
                            .replace("「", "")                # 左引用符を削除
                            .replace("」", "")                # 右引用符を削除
                            .replace("、", ", ")              # 全角カンマを半角カンマに置換
                        )

                matched_row.loc[:, 'Topic Names'] = formatted_topics
                matched_row.loc[:, 'Tagline'] = translated_data.get('translated tagline', tagline)
                matched_row.loc[:, 'Description'] = translated_data.get('translated description', description)

            else:
                print("翻訳APIでエラーが発生しました:", response.status_code)
                print("メッセージ:", response.text)
            
            # フィルタリングされた行をリストに追加
            filtered_rows.append(matched_row)

# 抽出結果を新しいDataFrameに結合
if filtered_rows:
    filtered_df = pd.concat(filtered_rows)
    
    # 列名を変更し、新しい列を追加
    filtered_df = filtered_df.rename(columns={
        'Name': 'ツール名',
        'Tagline': '概要説明',
        'Description': '詳細説明',
        'Topic Names': 'カテゴリー',
        'Website': 'ツールのURL',
        'Thumbnail URL': 'imageURL'
    })
    
    # 無料プランと有料プランの列を追加し、nullで埋める
    filtered_df['無料プラン'] = pd.NA
    filtered_df['有料プラン'] = pd.NA
    
    # 列の順序を調整
    filtered_df = filtered_df[['ツール名', '概要説明', '詳細説明', 'カテゴリー', '無料プラン', '有料プラン', 'ツールのURL', 'imageURL']]
    
    # 既存のDataFrameと新しいDataFrameを結合
    updated_df = pd.concat([existing_df, filtered_df], ignore_index=True)
    
    # 重複を削除（'ツール名'列をキーとして）
    updated_df = updated_df.drop_duplicates(subset='ツール名', keep='last')
    
    # 更新されたDataFrameをCSVファイルに書き出し
    updated_df.to_csv(output_csv_file, index=False)

    print(f"翻訳されたデータが {output_csv_file} に追加されました。")
else:
    print("一致するツールが見つかりませんでした。")
