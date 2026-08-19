import pyttsx3
import pyautogui
import psutil
import pyjokes
import speech_recognition as sr
import json
import requests
import geocoder
from difflib import get_close_matches


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
g = geocoder.ip('me')
data = json.load(open('data.json'))

def speak(audio) -> None:
        engine.say(audio)
        engine.runAndWait()

def screenshot() -> None:
    img = pyautogui.screenshot()
    img.save('path of folder you want to save/screenshot.png')

def cpu() -> None:
    usage = str(psutil.cpu_percent())
    speak("CPU is at"+usage)

    battery = psutil.sensors_battery()
    speak("battery is at")
    speak(battery.percent)

def joke() -> None:
    for i in range(5):
        speak(pyjokes.get_jokes()[i])

def takeCommand() -> str:
    r = sr.Recognizer()
    query = ""
    try:
        with sr.Microphone() as source:
            print('\n[Mic] Listening... (Speak now or wait/press Enter to type)')
            r.pause_threshold = 1
            r.energy_threshold = 494
            r.adjust_for_ambient_noise(source, duration=0.8)
            audio = r.listen(source, timeout=4, phrase_time_limit=8)
        print('[Mic] Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        print(f'User said (Voice): {query}\n')
        return query
    except Exception:
        pass

    try:
        user_input = input('[Type Command]: ').strip()
        if user_input:
            print(f'User said (Text): {user_input}\n')
            return user_input
    except Exception:
        pass

    return 'None'

def weather():
    try:
        if g and hasattr(g, 'latlng') and g.latlng:
            api_url = "https://fcc-weather-api.glitch.me/api/current?lat=" + \
                str(g.latlng[0]) + "&lon=" + str(g.latlng[1])
            data = requests.get(api_url, timeout=3)
            data_json = data.json()
            if isinstance(data_json, dict) and data_json.get('cod') == 200:
                main = data_json.get('main', {})
                wind = data_json.get('wind', {})
                weather_desc = data_json.get('weather', [{}])[0]
                speak(str(data_json.get('coord', {}).get('lat', '')) + ' latitude ' + str(data_json.get('coord', {}).get('lon', '')) + ' longitude')
                speak('Current location is ' + str(data_json.get('name', '')) + ' ' + str(data_json.get('sys', {}).get('country', '')))
                speak('weather type ' + str(weather_desc.get('main', '')))
                speak('Wind speed is ' + str(wind.get('speed', '')) + ' metre per second')
                speak('Temperature: ' + str(main.get('temp', '')) + ' degree celcius')
                speak('Humidity is ' + str(main.get('humidity', '')))
    except Exception as e:
        print(f"[Weather info skipped: {e}]")

def translate(word):
    word = word.lower()
    if word in data:
        speak(data[word])
    elif len(get_close_matches(word, data.keys())) > 0:
        x = get_close_matches(word, data.keys())[0]
        speak('Did you mean ' + x +
              ' instead,  respond with Yes or No.')
        ans = takeCommand().lower()
        if 'yes' in ans:
            speak(data[x])
        elif 'no' in ans:
            speak("Word doesn't exist. Please make sure you spelled it correctly.")
        else:
            speak("We didn't understand your entry.")

    else:
        speak("Word doesn't exist. Please double check it.")
