import pandas as pd
import os
import shutil
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI
import time
load_dotenv()

CSV_FILE_PATH = 'Summarized.csv'
API_KEY = os.getenv("PERPLEXITY_API_KEY") 
MODEL_NAME = "llama-3.1-sonar-huge-128k-online" 

client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")

def get_detailed_description(tool_name):
    """
    Perplexity APIを使用してツール名から詳細説明を取得します。
    
    Args:
        tool_name (str): ツールの名前。
        
    Returns:
        str: 取得した詳細説明。取得できない場合は空文字列。
    """
    messages = [
        {
            "role": "system",
            "content": "以下の指示に従ってください。"
        },
        {
            "role": "user",
            "content": f"{tool_name}について4つの文章で教えてください"
        }
    ]
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )
        print(response)
        # レスポンスからメッセージ内容を抽出
        description = response.choices[0].message.content
        return description
    except Exception as e:
        print(f"ツール名 '{tool_name}' の詳細説明の取得中にエラーが発生しました: {e}")
        return ''

def backup_csv(file_path):
    """
    元のCSVファイルをバックアップします。
    
    Args:
        file_path (str): バックアップ対象のCSVファイルのパス。
    """
    backup_path = f"{file_path}.backup"
    try:
        shutil.copy(file_path, backup_path)
        print(f"バックアップを '{backup_path}' に作成しました。")
    except Exception as e:
        print(f"バックアップの作成中にエラーが発生しました: {e}")

def main():
    # CSVファイルを読み込む
    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
    except FileNotFoundError:
        print(f"ファイル '{CSV_FILE_PATH}' が見つかりません。パスを確認してください。")
        return
    except Exception as e:
        print(f"CSVの読み込み中にエラーが発生しました: {e}")
        return
    
    # '詳細説明' が null の最初の行を抽出
    null_descriptions = df['詳細説明'].isnull()
    tools_to_update = df[null_descriptions]['ツール名'].tolist()
    
    if not tools_to_update:
        print("更新が必要なツールはありません。")
        return
    
    # バックアップを作成
    backup_csv(CSV_FILE_PATH)
    
    # '詳細説明'を更新
    for index, row in df[null_descriptions].iterrows():
        tool_name = row['ツール名']
        print(f"ツール名 '{tool_name}' の詳細説明を取得中...")
        description = get_detailed_description(tool_name)
        
        if description:
            df.at[index, '詳細説明'] = description
            print(f"詳細説明を更新しました。")
        else:
            print(f"詳細説明の取得に失敗しました。")
        
        # APIのレート制限を避けるために少し待つ（必要に応じて調整）
        time.sleep(1)
    
    # 更新されたDataFrameを元のCSVファイルに上書き保存
    try:
        df.to_csv(CSV_FILE_PATH, index=False, encoding='utf-8-sig')
        print(f"更新されたCSVファイルを '{CSV_FILE_PATH}' に保存しました。")
    except Exception as e:
        print(f"CSVの保存中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
