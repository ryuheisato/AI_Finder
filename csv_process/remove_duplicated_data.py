import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('AI_tools.csv')

# 'Name' 列を基準に重複を削除
df_deduplicated = df.drop_duplicates(subset=['Name'], keep='first')

# 新しいCSVとして保存
df_deduplicated.to_csv('deduplicated.csv', index=False)

print("重複した名前が削除され、新しいファイルに保存されました。")
