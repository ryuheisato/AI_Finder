import pandas as pd
import glob

# 1. 現在のディレクトリにあるすべてのCSVファイルを取得
csv_files = glob.glob('./*.csv')

# 2. 共通の列名を定義（列名はすでにCSVファイルに含まれているので特に設定しない）
dfs = []
for csv_file in csv_files:
    # CSVファイルを読み込む（最初の行がヘッダー行）
    df = pd.read_csv(csv_file, skip_blank_lines=True)

    # 空行を削除
    df.dropna(how='all', inplace=True)

    # DataFrameをリストに追加
    dfs.append(df)

# 3. データフレームを連結
combined_df = pd.concat(dfs, ignore_index=True)

# 4. 連結したデータを1つのCSVファイルに保存
combined_df.to_csv('combined_data.csv', index=False)

print(f"Total rows combined: {len(combined_df)}")
