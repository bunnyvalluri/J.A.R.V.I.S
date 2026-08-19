from urllib.request import urlopen
import urllib.parse
import webbrowser
from sys import platform
import os

if platform == "linux" or platform == "linux2":
    chrome_path = '/usr/bin/google-chrome'

elif platform == "darwin":
    chrome_path = 'open -a /Applications/Google\\ Chrome.app'

elif platform == "win32":
    p1 = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    p2 = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    chrome_path = p1 if os.path.exists(p1) else p2
else:
    print('Unsupported OS')
    exit(1)

try:
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
except Exception:
    pass


def youtube(textToSearch):
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    webbrowser.get('chrome').open_new_tab(url)


if __name__ == '__main__':
    youtube('any text')
