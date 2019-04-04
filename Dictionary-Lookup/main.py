import json
import requests
import re

app_id = ""
app_key = ""


def get_values(key, json_string):
    # print(json_string)
    gen = (m.start() for m in re.finditer(key, json_string))
    edges = []
    if type(json_string) != str:
        exit("JSON received not a String?")
    for values in gen:
        edges.append(values)
    count = 0
    definitions = []

    # populated list with index values of definitions, now parse strings for values
    for index in edges:
        # print("start: ", index+16, "end: ", json_string.find('"', index+16))
        # print("End: ", json_string.find('"', index+16))
        temp_holder = json_string[index+len(key)+3:json_string.find(',', index+len(key)+3)].strip('[]{}"').capitalize()
        if temp_holder not in definitions:
            # send into different list not formatted as to check for copies
            definitions.append(temp_holder)
            count += 1
        if count == 4:
            return definitions


def definition(word, language):
    base_url = "https://od-api.oxforddictionaries.com:443/api/v1/entries/"
    sep = "/"
    lookup_url = base_url + language + sep + word
    req = requests.get(lookup_url, headers={"app_id": app_id, "app_key": app_key})
    try:
        # object to string
        req = json.dumps(req.json())
    except ValueError:
        if req.status_code == 404:
            print("Word Unavailable")
            return 0
        if req.status_code == 500:
            exit("Internal Server Error")
    return get_values('definitions', req)


def get_keys():
    with open('keys.txt') as config:
        global app_id
        global app_key

        app_id = config.readline().split(':')[1].strip()
        app_key = config.readline().split(':')[1].strip()


def guess(malformed_word):
    guess_url = "https://od-api.oxforddictionaries.com:443/api/v1/search/en?q=" + malformed_word + "&prefix=false"
    guess_req = requests.get(guess_url, headers={"app_id": app_id, "app_key": app_key})
    try:
        guess_req = json.dumps(guess_req.json())
        # print(guess_req)
    except ValueError:
        if guess_req.status_code == 404:
            return 0
        if guess_req.status_code == 500:
            exit("Internal Server Error")

    guesses = get_values("word", guess_req)
    for value in guesses:
        if input("Did you mean: " + value.capitalize() + "\nY/N: ") == 'y':
            return value
    return -1


def main():
    if app_id == "" or app_key == "":
        get_keys()

    languages = {"english": "en", "spanish": "es", "german": "de"}
    lan = input("Choose a language: English || Spanish || German\n").lower()

    while lan not in languages.keys():
        lan = input("Choose a language: English || Spanish|| German\n").lower()

    print("Language Chosen: %s\n" % lan.capitalize())

    url_lang = languages.get(lan)
    word = input("What word would you like to look up?\n").lower()

    definitions = definition(word, url_lang)

    if definitions == 0:
        get_guess = guess(word)
        if get_guess == -1:
            print("Not able to guess word")
            main()
        definitions = definition(get_guess, url_lang)
    # Get Values out of JSON)
    # print(req)
    print("\033[1m\033[4m", "Results for ➤", word.capitalize(), "\033[0m\n")
    for num, define in enumerate(definitions, start=1):
        print("\t\033[1m" + str(num) + ")\033[0m " + define + ".")
    exit("DONE")


main()
