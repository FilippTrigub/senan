import json
import os
import re
from typing import Dict, List

from utils.GlobalLogger import log_info


def save_content_to_text_file(content_object):
    filename = (re.sub('[?\"%*:|<>]', '', ("assets/" + content_object['timestamp'] + "_senan.txt")))
    with open(filename, 'w') as file:
        for key, value in content_object.items():
            file.write(f"{key}:\n{value};\n\n")


def save_str_to_file(filename: str, to_be_saved_str: str):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        log_info('Saving to file.')
        with open(filename, 'w') as f:
            f.write(to_be_saved_str)
        return True
    except Exception as e:
        print(f"An error occurred while saving the str file: {str(e)}")
        return False


def save_list_to_file(filename: str, to_be_saved_list: List[str]):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        log_info('Saving to file.')
        with open(filename, 'w') as f:
            for text in to_be_saved_list:
                f.write(text)
                f.write('\n')
        return True
    except Exception as e:
        print(f"An error occurred while saving the list file: {str(e)}")
        return False


def save_dict_to_file(filename: str, dictionary: Dict[str, str]):
    log_info(f'Save dict to file: {filename}')
    try:
        log_info('Making directory.')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as file:
            log_info('Saving to file.')
            json.dump(dictionary, file)
    except Exception as e:
        log_info(f"Failed to save dictionary: {e}")
