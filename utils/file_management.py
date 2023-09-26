import re


def save_content_to_text_file(content_object):
    filename = (re.sub('[?\"%*:|<>]', '', ("assets/" + content_object['timestamp'] + "_senan.txt")))
    with open(filename, 'w') as file:
        for key, value in content_object.items():
            file.write(f"{key}:\n{value};\n\n")
