from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import time
import csv
import json

# Path to the ChromeDriver
chrome_driver_path = "./chromedriver-mac-x64/chromedriver"

# Initialize the Selenium WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Open the website
url = "https://ai-gallery.jp/tools/"
driver.get(url)
time.sleep(3)  # Wait for the page to load completely

# Prepare the CSV file for storing the tool details
fields = ['ツール名', '概要説明', '詳細説明', 'カテゴリー', '無料プラン', '有料プラン', 'ツールのURL', 'imageURL']

# Open the CSV file for writing
with open('ai_tools_details.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

    while True:
        # Get all the tool cards on the current page
        cards = driver.find_elements(By.CSS_SELECTOR, "div.jet-listing-grid__item")

        # Loop through each card and extract details
        for card in cards:
            try:
                # Extract the link data from 'data-ha-element-link' attribute
                link_element = card.find_element(By.CSS_SELECTOR, "div[data-ha-element-link]")
                link_data = link_element.get_attribute('data-ha-element-link')
                link_json = json.loads(link_data)
                card_url = link_json.get('url', 'null')

                # Open the detail page by using the extracted URL
                driver.get(card_url)
                time.sleep(3)  # Wait for the detail page to load

                # Parse the detail page
                detail_html = driver.page_source
                soup = BeautifulSoup(detail_html, 'html.parser')

                # Extract tool details using BeautifulSoup
                tool_data = {}
                tool_data['ツール名'] = soup.find('h1', class_='elementor-heading-title').get_text(strip=True) \
                    if soup.find('h1', class_='elementor-heading-title') else 'null'

                # Extract the summary (概要説明)
                tool_data['概要説明'] = soup.find('div', class_='jet-listing-dynamic-field__content').get_text(strip=True) \
                    if soup.find('div', class_='jet-listing-dynamic-field__content') else 'null'

                # Extract the detailed information (詳細説明)
                detail_container = soup.find('div', {'data-widget_type': 'theme-post-content.default'})
                if detail_container:
                    tool_data['詳細説明'] = detail_container.get_text(separator='\n', strip=True)
                else:
                    tool_data['詳細説明'] = 'null'

                # Extract the category (カテゴリー) - Exclude price information
                category_list = soup.find('div', class_='category-original')
                if category_list:
                    categories = [a.get_text(strip=True) for a in category_list.select('.elementor-post-info__terms-list-item')]
                    tool_data['カテゴリー'] = ', '.join(categories)
                else:
                    tool_data['カテゴリー'] = 'null'

                # Initialize price plan fields
                tool_data['無料プラン'] = 'null'
                tool_data['有料プラン'] = 'null'

                # Extract pricing information
                price_info_items = soup.select('li.elementor-icon-list-item')
                for item in price_info_items:
                    text_content = item.get_text(strip=True)
                    if '完全無料' in text_content:
                        tool_data['無料プラン'] = '完全無料'
                    elif '基本無料' in text_content:
                        tool_data['無料プラン'] = '基本無料'
                    elif '有料プラン' in text_content:
                        tool_data['有料プラン'] = text_content.replace('有料プラン:', '').strip()

                # Extract the image URL (imageURL)
                image_element = soup.find('img', class_='jet-listing-dynamic-image__img')
                tool_data['imageURL'] = image_element['src'] if image_element else 'null'

                # Extract the tool URL (ツールのURL) from 'data-ha-element-link'
                ha_element = soup.find('div', {'data-ha-element-link': True})
                if ha_element:
                    ha_link_data = ha_element.get('data-ha-element-link')
                    ha_link_json = json.loads(ha_link_data)
                    tool_data['ツールのURL'] = ha_link_json.get('url', 'null')
                else:
                    # Fallback to anchor element URL if the 'data-ha-element-link' is missing
                    anchor_element = soup.find('a', href=True)
                    tool_data['ツールのURL'] = anchor_element['href'] if anchor_element else 'null'

                # Write the tool data to CSV
                writer.writerow(tool_data)

                # Go back to the tool list
                driver.back()
                time.sleep(3)  # Wait for the tool list page to load

            except Exception as e:
                print(f"Error processing card: {e}")
                continue

        # Check if there is a "next" button and click it
        try:
            # Wait until the "next" button is present and clickable
            wait = WebDriverWait(driver, 10)
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.jet-filters-pagination__item.next')))

            # Scroll slightly to avoid the search bar overlapping the "next" button
            driver.execute_script("window.scrollBy(0, 100);")

            # Use ActionChains to move to the element and click
            actions = ActionChains(driver)
            actions.move_to_element(next_button).click().perform()
            time.sleep(3)  # Wait for the next page to load

        except (NoSuchElementException, TimeoutException):
            # If "next" button is not found, we have reached the last page
            print("Reached the last page.")
            break
        except ElementClickInterceptedException:
            # In case the click is still intercepted, click using JavaScript
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)  # Wait for the next page to load

# Close the browser
driver.quit()

print("Scraping completed and data saved to ai_tools_details.csv")
