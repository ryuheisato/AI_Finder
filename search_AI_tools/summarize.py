#AIツールギャラリーからスクレイピングした詳細情報をChatGPTで要約。

import pandas as pd
from openai import OpenAI
import json
import time
import os
from dotenv import load_dotenv
import re
from tqdm import tqdm
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key =openai_api_key)

input_csv = 'ai_tools_details.csv'
output_csv = 'Summarized.csv'

df = pd.read_csv(input_csv, encoding='utf-8-sig')

# 更新するカラムを確認
required_columns = ['ツール名', '概要説明', '詳細説明', 'カテゴリー', '無料プラン', '有料プラン', 'ツールのURL', 'imageURL']
for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"必要なカラム '{column}' がCSVファイルに存在しません。")
    
# 出力CSVにヘッダーを書き込む（初回のみ）
if not os.path.exists(output_csv):
    df.head(0).to_csv(output_csv, index=False, encoding='utf-8-sig')

# APIリクエストの関数を定義
def get_summary_category(detailed_description):
    prompt = """
    このAIツール説明文について、概要説明、詳細説明、カテゴリーの3つに分けてください。
    概要説明はツールを1つの文章で紹介するもの。
    詳細説明はツール情報の要約。
    カテゴリーは説明文の中からキーワードを抽出してカンマ区切りで繋げてください。例：「画面録画, 要約, 文字起こし, 議事録, Chrome拡張機能」
    そして出力はJSON形式のように、
    {
        "概要説明":"テキスト",
        "詳細説明":"テキスト",
        "カテゴリー":"テキスト"
    }
    のようにしてください。コードブロックは使用しないでください。
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは優秀な要約者です。"},
                {"role": "user", "content": prompt + "\n\n詳細説明:\n" + detailed_description}
            ],
            max_tokens=500,
            temperature=0.5,
        )
        # レスポンスから内容を取得
        content = response.choices[0].message.content.strip()
        print(f"APIレスポンス: {content}")
        
        # コードブロックマークダウンを除去
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        # JSONとして解析
        result = json.loads(content)
        return result
    except Exception as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
        return None

# 出力CSVに既に書き込まれたインデックスを取得（再実行時に重複を避けるため）
processed_indices = set()
if os.path.exists(output_csv):
    processed_df = pd.read_csv(output_csv, encoding='utf-8-sig')
    processed_indices = set(processed_df.index)

# 各行を処理
with open(output_csv, 'a', encoding='utf-8-sig', newline='') as f_out:
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing rows"):
        if index in processed_indices:
            print(f"Row {index + 1} は既に処理済みのためスキップします。")
            continue

        detailed_description = row['詳細説明']
        print(f"Processing row {index + 1}/{len(df)}: {row['ツール名']}")
        
        result = get_summary_category(detailed_description)
        
        if result:
            # JSONから各項目を取得して更新
            row['概要説明'] = result.get('概要説明', row['概要説明'])
            row['詳細説明'] = result.get('詳細説明', row['詳細説明'])
            row['カテゴリー'] = result.get('カテゴリー', row['カテゴリー'])
            print(f"Row {index + 1} を正常に更新しました。")
        else:
            print(f"Row {index + 1} の更新に失敗しました。元のデータを保持します。")
        
        # 更新した行を出力CSVに書き込む
        row.to_frame().T.to_csv(f_out, header=False, index=False, encoding='utf-8-sig')
        
        # APIのレート制限を避けるために少し待機
        time.sleep(1)

print(f"全ての行の処理が完了しました。更新されたCSVファイルを '{output_csv}' として保存しました。")