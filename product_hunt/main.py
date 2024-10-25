import requests
import csv
import time
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY1 = os.getenv('PRODUCT_HUNT_API_KEY1')
API_KEY2 = os.getenv('PRODUCT_HUNT_API_KEY2')
API_KEY3 = os.getenv('PRODUCT_HUNT_API_KEY3')
API_KEY4 = os.getenv('PRODUCT_HUNT_API_KEY4')


API_URL = 'https://api.producthunt.com/v2/api/graphql'
API_KEYS = [
    API_KEY1,
    API_KEY2,
    API_KEY3,
    API_KEY4
    # Add more keys if needed
]
HEADERS_TEMPLATE = {
    'Content-Type': 'application/json'
}

QUERY = '''
query getPosts($after: String) {
  posts(topic: "artificial-intelligence", after: $after) {
    edges {
      node {
        name
        tagline
        description
        votesCount
        website
        topics {
          edges {
            node {
              name
            }
          }
        }
        reviewsRating
        slug
        thumbnail {
          url
        }
        createdAt
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
'''

def fetch_all_ai_products():
    all_products = []
    variables = {"after": None}
    api_key_index = 0
    retries = 0
    start_time = None  # To track when the 15-minute window starts

    while True:
        # Set the current API key
        headers = HEADERS_TEMPLATE.copy()
        headers['Authorization'] = f'Bearer {API_KEYS[api_key_index]}'
        
        try:
            # Start the 15-minute window if this is the first request
            if start_time is None:
                start_time = time.time()

            response = requests.post(API_URL, json={"query": QUERY, "variables": variables}, headers=headers)
            
            if response.status_code == 429:  # Rate limit reached
                print(f"Rate limit reached for API key {API_KEYS[api_key_index]}. Switching to the next API key.")
                api_key_index += 1  # Switch to the next API key

                if api_key_index >= len(API_KEYS):  # If all keys are exhausted
                    wait_time = 900
                    print(f"All API keys have reached their limit. Waiting {wait_time} seconds until retrying with the first key...")
                    time.sleep(wait_time)
                    start_time = None  # Reset the timer for the next cycle
                    api_key_index = 0  # Reset to the first API key
                else:
                    print(f"Switching to next API key: {API_KEYS[api_key_index]}")
                continue  # Retry with the next API key

            data = response.json()
            if 'errors' in data:
                print(f"Error in response: {data['errors']}")
                break

            # Collect products data
            products = data['data']['posts']['edges']
            all_products.extend(products)

            # Save each batch of products to the CSV
            save_to_csv(products, variables['after'])

            # Check pagination info
            page_info = data['data']['posts']['pageInfo']
            if not page_info['hasNextPage']:
                break  # No more pages to fetch

            # Update cursor for the next page
            variables['after'] = page_info['endCursor']

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break

        # If no data returned, wait a while before retrying
        if response.status_code == 429:
            wait_time = 120  # Wait for 2 minutes
            print(f"Rate limit reached. Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)

    return all_products

def initialize_csv():
    """Initialize the CSV file and write the header if it doesn't exist."""
    if not os.path.exists('ai_products.csv'):
        with open('ai_products.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Name', 'Tagline', 'Description', 'Votes Count', 'Website', 'Topic Names', 'Reviews Rating', 'Slug', 
                'Thumbnail URL', 'Created At', 'EndCursor'
            ])

def save_to_csv(products, end_cursor):
    """Save products data to a single CSV file, appending the rows."""
    with open('ai_products.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for product in products:
            product_info = product['node']
            topic_names = ", ".join([topic['node']['name'] for topic in product_info['topics']['edges']])

            writer.writerow([
                product_info.get('name'),
                product_info.get('tagline'),
                product_info.get('description'),
                product_info.get('votesCount'),
                product_info.get('website'),
                topic_names,
                product_info.get('reviewsRating'),
                product_info.get('slug'),
                product_info.get('thumbnail', {}).get('url'),
                product_info.get('createdAt'),
                end_cursor
            ])

# Initialize the CSV file and write the header
initialize_csv()

# Fetch all products
print("Fetching AI products...")
products = fetch_all_ai_products()

print(f"Total products fetched: {len(products)}")
