import pandas as pd
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CSVファイルを読み込む
df = pd.read_csv('output.csv')

# チェックするURLの列名（例：'Website'）
url_column = 'Website'

# URLが機能しているかを確認する関数
def check_url(url):
    logging.info(f'Checking URL: {url}')
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            logging.info(f'URL is working: {url}')
            return True
        else:
            logging.warning(f'URL returned status code {response.status_code}: {url}')
            return False
    except requests.RequestException as e:
        logging.error(f'Error checking URL {url}: {e}')
        return False

# 並列処理でURLをチェックする関数
def check_urls_concurrently(urls, max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_url, url): url for url in urls}
        results = []
        for future in tqdm(as_completed(futures), total=len(futures)):
            url = futures[future]
            try:
                results.append(future.result())
            except Exception as e:
                logging.error(f'Error processing URL {url}: {e}')
                results.append(False)
        return results

# 並列処理でURLをチェックし、結果をDataFrameに追加
df['URL_Working'] = check_urls_concurrently(df[url_column], max_workers=20)

# 無効なURLを持つ行を削除
df = df[df['URL_Working'] == True]

# 'URL_Working'列を削除
df = df.drop('URL_Working', axis=1)

# 修正後のデータを新しいCSVファイルに保存する
df.to_csv('Final.csv', index=False)

logging.info('Processing complete. Output saved to Final.csv')
