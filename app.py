import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def get_categories(driver, url):
    print(f"Fetching categories from {url}")
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Look for category links specifically in the navigation menu
    categories = []
    
    # Find links that contain "in-isl" in their href attribute
    links = soup.find_all('a', href=lambda href: href and 'in-isl' in href)
    
    for link in links:
        category_name = link.text.strip()
        href = link['href']
        
        # Skip alphabets categories as mentioned in your original code
        if category_name and category_name not in ['Alphabets', 'ASL Alphabets']:
            # Make URL absolute
            if not href.startswith('http'):
                if not href.startswith('/'):
                    href = '/' + href
                href = "https://talkinghands.co.in" + href
            print(f"Adding category: {category_name} - {href}")
            categories.append((category_name, href))
    
    return categories

def get_words_from_category(driver, category_url):
    print(f"Getting words from: {category_url}")
    driver.get(category_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Based on the HTML structure you provided, words are in list items with views-field-title
    word_items = soup.select('div.views-field-title a')
    print(f"Found {len(word_items)} word links")

    words = []
    for link in word_items:
        word = link.text.strip()
        href = link.get('href', '')

        # Skip empty words
        if not word:
            continue

        # Build full URL
        if not href.startswith('http'):
            href = "https://talkinghands.co.in" + href

        print(f"Adding word: {word} - {href}")
        words.append((word, href))
    
    return words

def get_video_details(driver, word_url):
    print(f"Getting video details from: {word_url}")
    driver.get(word_url)
    time.sleep(3)

    try:
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Look for the source tag inside the video element
        source_tag = soup.select_one('video source')
        
        if source_tag and source_tag.has_attr('src'):
            video_src = source_tag['src']
            
            # Make URL absolute if it's relative
            if video_src.startswith('/'):
                video_src = "https://talkinghands.co.in" + video_src
                
            print(f"Found video source: {video_src}")
            
            # Try to get video duration
            try:
                video_element = driver.find_element(By.TAG_NAME, "video")
                duration = driver.execute_script("return arguments[0].duration", video_element)
                
                if duration and not pd.isna(duration):
                    duration = float(duration)
                    minutes = int(duration // 60)
                    seconds = int(duration % 60)
                    print(f"Video duration: {minutes}m {seconds}s")
                    return video_src, minutes, 0, minutes, seconds
                else:
                    print("Could not get video duration, using default (0m 3s)")
                    return video_src, 0, 0, 0, 3
            except Exception as e:
                print(f"Error getting duration: {e}")
                return video_src, 0, 0, 0, 3
        else:
            print("No video source found")
            return None, 0, 0, 0, 0

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
    base_url = "https://talkinghands.co.in"
    print("Starting main function")

    os.makedirs("output", exist_ok=True)

    print("Initializing WebDriver in headless mode...")
    # Set up Chrome options for headless operation
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Using the newer headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Add user agent to prevent detection as a bot
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)

    df = pd.DataFrame(columns=['Name', 'yt_name', 'Link', 'start_min', 'start_sec', 'end_min', 'end_sec'])

    try:
        categories = get_categories(driver, base_url)
        print(f"Found {len(categories)} categories")

        # If no categories found, try using some predefined ones
        if not categories:
            print("No categories found automatically. Using predefined categories...")
            categories = [
                ("Animals and Birds", "https://talkinghands.co.in/animals-and-birds-in-isl"),
                # Add more predefined categories if needed
            ]

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

                time.sleep(1)  # Gentle delay between requests

            # Save category-specific dataset
            if not category_df.empty:
                safe_name = safe_filename(category_name)
                category_df.to_excel(f"output/isl_dataset_{safe_name}.xlsx", index=False)
                print(f"Saved progress for category: {category_name}")

            # Save overall progress after each category
            if not df.empty:
                df.to_excel("output/isl_dataset_progress.xlsx", index=False)
                print("Saved overall progress")

    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()
        print("WebDriver closed")

    # Save final complete dataset
    if not df.empty:
        df.to_excel("output/isl_dataset_complete.xlsx", index=False)
        print("Dataset creation completed!")
    else:
        print("No data was collected. Dataset creation failed.")

if __name__ == "__main__":
    try:
        print("Script starting...")
        main()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
