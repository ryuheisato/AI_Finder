import pandas as pd
import difflib

input_csv_file = 'ProductHuntToolsList.csv'  # 元のCSVファイル名
output_csv_file = 'Add_tools.csv'  # 抽出後のCSVファイル名

# ツール名の一覧を入力として受け取る（カンマ区切り）
tool_names_input = input("Enter tool names (comma-separated): ")
tool_names = [name.strip() for name in tool_names_input.split(',')]  # リストに変換して空白をトリム

# CSVファイルを読み込み
df = pd.read_csv(input_csv_file)

# 部分一致で最も近いツールを検索し、結果をフィルタリング
filtered_rows = []
for tool_name in tool_names:
    # difflibを使って最も一致するツール名を見つける
    possible_matches = difflib.get_close_matches(tool_name, df['Name'].astype(str), n=1, cutoff=0.1)
    
    if possible_matches:
        # 最も近い一致を取得し、その行をフィルタリング
        closest_match = possible_matches[0]
        matched_row = df[df['Name'] == closest_match]
        filtered_rows.append(matched_row)

# 抽出結果を新しいDataFrameに結合
if filtered_rows:
    filtered_df = pd.concat(filtered_rows)

    # 新しいCSVファイルに書き出し
    filtered_df.to_csv(output_csv_file, index=False)

    print(f"Filtered data has been saved to {output_csv_file}.")
else:
    print("No matching tools found.")
