import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def get_categories(driver, url):
    print(f"Fetching categories from {url}")
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_links = soup.find_all('a')
    
    categories = []
    for link in all_links:
        category_name = link.text.strip()
        try:
            href = link['href']
            if 'in-isl' in href and category_name and category_name not in ['Alphabets', 'ASL Alphabets']:
                # Make URL absolute
                if not href.startswith('http'):
                    if not href.startswith('/'):
                        href = '/' + href
                    href = url + href
                print(f"Adding category: {category_name} - {href}")
                categories.append((category_name, href))
        except KeyError:
            pass
    return categories

def get_words_from_category(driver, category_url):
    print(f"Getting words from: {category_url}")
    driver.get(category_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    main_content = soup.find('div', id='content') or soup.find('div', class_='content') or soup

    links = main_content.find_all('a')
    print(f"Found {len(links)} links in content area")

    words = []
    for link in links:
        word = link.text.strip()
        href = link.get('href', '')

        # Skip UI elements or invalid words
        if (not word or
            word.lower() in ['previous', 'next', 'home', 'back', 'log in', 'logout'] or
            '#' in href or
            'user' in href or
            'menu' in href or
            'block-bartik' in href or
            'in-isl' in href):
            print(f"Skipping non-word link: {word} -> {href}")
            continue

        # Build full URL
        if not href.startswith('http'):
            base_url = category_url.split('/in-isl')[0]
            href = base_url + ('' if href.startswith('/') else '/') + href

        print(f"Adding word: {word} - {href}")
        words.append((word, href))
    
    return words

def get_video_details(driver, word_url):
    print(f"Getting video details from: {word_url}")
    driver.get(word_url)
    time.sleep(3)

    try:
        video_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )

        video_src = video_element.get_attribute('src')
        print(f"Found video source: {video_src}")

        duration = driver.execute_script("return arguments[0].duration", video_element)
        if duration:
            duration = float(duration)
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return video_src, minutes, 0, minutes, seconds
        else:
            print("Could not get video duration, using default (3s)")
            return video_src, 0, 0, 0, 3

    except Exception as e:
        print(f"Error getting video details: {e}")
        try:
            screenshot_name = f"error_{int(time.time())}.png"
            driver.save_screenshot(screenshot_name)
            print(f"Saved error screenshot to {screenshot_name}")
        except:
            pass
        return None, 0, 0, 0, 0

def safe_filename(name):
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def main():
    base_url = "https://talkingHands.co.in"
    print("Starting main function")

    os.makedirs("output", exist_ok=True)

    print("Initializing WebDriver...")
    driver = webdriver.Chrome()

    df = pd.DataFrame(columns=['Name', 'yt_name', 'Link', 'start_min', 'start_sec', 'end_min', 'end_sec'])

    try:
        categories = get_categories(driver, base_url)
        print(f"Found {len(categories)} categories")

        for category_name, category_url in categories:
            print(f"\nProcessing category: {category_name}")
            words = get_words_from_category(driver, category_url)
            print(f"Found {len(words)} words in category {category_name}")

            category_df = pd.DataFrame(columns=df.columns)

            for word, word_url in words:
                print(f"\nProcessing word: {word}")
                video_link, start_min, start_sec, end_min, end_sec = get_video_details(driver, word_url)

                if video_link:
                    new_row = {
                        'Name': word,
                        'yt_name': word,
                        'Link': video_link,
                        'start_min': start_min,
                        'start_sec': start_sec,
                        'end_min': end_min,
                        'end_sec': end_sec
                    }
                    category_df = pd.concat([category_df, pd.DataFrame([new_row])], ignore_index=True)
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    print(f"Added to dataset: {word}")
                else:
                    print(f"Skipping {word} (no video link found)")

                time.sleep(1)

            safe_name = safe_filename(category_name)
            category_df.to_excel(f"output/isl_dataset_{safe_name}.xlsx", index=False)
            print(f"Saved progress for category: {category_name}")

    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()
        print("WebDriver closed")

    df.to_excel("output/isl_dataset_complete.xlsx", index=False)
    print("Dataset creation completed!")

if __name__ == "__main__":
    try:
        print("Script starting...")
        main()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
