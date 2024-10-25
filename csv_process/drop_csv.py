import pandas as pd

# CSVファイルの読み込み
input_csv_file = 'output.csv'  # 元のCSVファイル名
output_csv_file = 'ProductHuntToolsList.csv'  # ドロップ後のCSVファイル名

# ドロップする列のリスト
columns_to_drop = ['Votes Count', 'Reviews Rating', 'Slug', 'Created At', 'EndCursor']

# CSVファイルを読み込んで、指定の列をドロップ
df = pd.read_csv(input_csv_file)

# 指定した列をドロップ
df_dropped = df.drop(columns=columns_to_drop)

# 新しいCSVファイルに書き出し
df_dropped.to_csv(output_csv_file, index=False)

print(f"Columns {columns_to_drop} have been dropped and the new file is saved as {output_csv_file}.")
