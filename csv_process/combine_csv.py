import pandas as pd

# 1. 2つのCSVファイルのパスを指定
csv_file_1 = '../search_AI_tools/Summarized.csv'
csv_file_2 = '../search_AI_tools/Add_tools.csv'

# 2. DataFrameのリストを作成
dfs = []

# 3. 各CSVファイルを読み込み、空行を削除してリストに追加
for csv_file in [csv_file_1, csv_file_2]:
    df = pd.read_csv(csv_file, skip_blank_lines=True)
    df.dropna(how='all', inplace=True)
    dfs.append(df)

# 4. データフレームを連結
combined_df = pd.concat(dfs, ignore_index=True)

# 5. 連結したデータを1つのCSVファイルに保存
combined_df.to_csv('combined_data.csv', index=False)

print(f"Total rows combined: {len(combined_df)}")
