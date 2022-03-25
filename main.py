import pyaudio
import speech_recognition as sr
import os
import warnings
import webbrowser
import re
import urllib.request
from gtts import gTTS
from bs4 import BeautifulSoup, element
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# -----------------------------------------------------------------------------------------
warnings.filterwarnings('ignore')

# takes audio and understands it. 
def RecordAudioIntake():
    intake = sr.Recognizer()
    # creates an recognizable object. 
    
    # standard os micorpgone device
    with sr.Microphone(device_index = 1) as source:
        print("I am listening...")
        audio = intake.listen(source)
    data = ""

    try:
        data = intake.recognize_google(audio)
        # recognizes and understands the audio
        print("You said: " + data.lower())
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio, unknown error")
    except sr.RequestError as e:
        print("Request results from Google Speech Recognition service error: " + e)
    return data.lower()
    # returns what the audio as a string in lowercase


def AssistentResponse(text):
    print(text)
    text2Speach = gTTS(text = text, lang = 'en', slow = False)
    text2Speach.save("assistant_response.mp3")
    os.system("start assistant_response.mp3")


def ActivationWord(speech_input):
    activatingWords = ["hey computer", "hey alexa", "hey google", "hey bitch", "hey siri", "google", "siri"]

    for phrase in activatingWords:
        if phrase in speech_input:
            return True
    return False


def WebScrape(URL_searchTerm):
    driver = webdriver.Chrome("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\chromedriver.exe")
    driver.get(URL_searchTerm)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # removes Google Cookies pop up and other possible pop up bs
    driver.find_element_by_id("L2AGLb").click()

    delay = 10

    re_comp_search = "to \$"
    # "\" to escape special char ($ in this case)

    try:
        # waits for an HTML element to become visible
        WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.XPATH, '//h3')))
        print("Page is ready!")
 
        # google answers
        if soup.find_all(class_="Z0LcW XcVN5d"): 
            for text in soup.find_all(class_="Z0LcW XcVN5d"):
                AssistentResponse("This is what I found: ", text.get_text())

        # If there's no answer from Google, then it searches for it in the descriptions of the sites | re.compile is a RegEx shit
        elif soup.body.findAll(text=re.compile(re_comp_search)):  
            for text in soup.body.findAll(text=re.compile(re_comp_search)):
                AssistentResponse("This is what I found: ", text)

        else:
            print("No results")
            AssistentResponse("I could not find a sufficent answer to your request.")

    except TimeoutException:
        print("Loading took too much time!")
        AssistentResponse("I could not find an answer due to this unit being doo doo.")


def GoogleSearch(speech_input):
    activatingWords = ["hey computer", "hey alexa", "hey google", "hey bitch", "hey siri", "google", "siri"]
    text = speech_input.lower()

    for phrase in activatingWords:
        if phrase in text:
            indexValue = text.index(phrase)
            searchTerm = text[(indexValue + len(phrase))::]
            # only takes what is said after the activation word.
            URL_searchTerm = str("https://www.google.com/search?q=" + searchTerm)
            URL_searchTerm =  URL_searchTerm.replace(" ", "+")

    if 'play ' in searchTerm:
        song = searchTerm.replace('play ', '')
        AssistentResponse("playing" + song)

        # webscraping youtube search_query to get the link of the first video
        query = urllib.parse.quote(song)
        youtube_url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(youtube_url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        for vid in soup.findAll(attrs={'class':'yt-uix-title-link'}):
            link_to_open = "https://www.youtube.com" + vid["href"]
            break
        webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open(link_to_open)

    else:
        WebScrape(URL_searchTerm)


def main():
    text = RecordAudioIntake()

    if (ActivationWord(text) == True):
        AssistentResponse("Yes dear leader, whos every word is my command.")
        GoogleSearch(text)

    elif (ActivationWord(text) == False):
        AssistentResponse("I could not identify an activation command in the audio")

    else:
        AssistentResponse("I do not know what went wrong")


main()
