import os
import re
import emoji
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By


def find_min_and_max_float_index(series):
    # Filter out non-float values
    series = series.dropna().astype(float)
    # Find index of minimum value
    idxmin = series.index[series.argmin()]
    # Find index of maximum value
    idxmax = series.index[series.argmax()]

    return idxmin, idxmax


def html_to_png(media_url, file_path):
    # Check if directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Configure Selenium to use the appropriate web driver
    driver_path = 'C:\\chromedriver_win32\\chromedriver_win32.exe'  # todo move to config
    driver = webdriver.Chrome(driver_path)

    # Load the HTML into the web driver
    driver.get(media_url)

    # Wait for page to render
    driver.implicitly_wait(20)

    # Get the coordinates and dimensions of the element
    element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')
    left = element.location['x']
    top = element.location['y']
    right = left + element.size['width']
    bottom = top + element.size['height']
    # Get the dimensions of the web page
    height = driver.execute_script('return document.documentElement.scrollHeight')

    # Take a screenshot of the element and save it as a PNG image
    screenshot = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(screenshot))
    im = im.crop((left, top + 80, right + 200, bottom))
    im.save(file_path)

    # Check if file was saved successfully
    if os.path.isfile(file_path):
        print("File saved successfully.")
    else:
        print("Error: file not saved.")


def remove_urls_and_emojis_and_leave_only_english_text(text):
    # Remove URLs
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    text = url_pattern.sub('', text)

    # Remove emojis
    emoji_pattern = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
    text = emoji_pattern.sub('', text)

    # Remove specific unicode emoji characters
    text = emoji.replace_emoji(text, '')

    # Define the range of Unicode characters for the English alphabet
    basic_latin = (32)
    english_alpha_1 = (65, 90)
    english_alpha_2 = (97, 122)

    # Define the range of Unicode characters for combining diacritical marks
    diacritical = (768, 879)

    # Filter out non-English characters from the input text
    cleaned_text = ''
    for char in text:
        char_unicode = ord(char)
        if char_unicode in range(*english_alpha_1) \
                or char_unicode in range(*english_alpha_2) \
                or char_unicode in range(*diacritical)\
                or char_unicode == basic_latin:
            cleaned_text += char

    return cleaned_text


def remove_files_in_dir(dir_path):
    # Check if directory exists
    if not os.path.isdir(dir_path):
        print(f"{dir_path} is not a directory")
        return

    # Get list of files in directory
    files_in_dir = os.listdir(dir_path)

    # Loop through the list of files and delete them one at a time
    for file in files_in_dir:
        try:
            os.remove(os.path.join(dir_path, file))
            print(f"{file} deleted successfully")
        except OSError as e:
            print(f"Error: {file} cannot be deleted. {e}")

    # Check if all files were deleted successfully
    num_files_left = len(os.listdir(dir_path))
    if num_files_left == 0:
        print(f"All files in {dir_path} deleted successfully.")
    else:
        print(f"Error: {num_files_left} files were not deleted.")
