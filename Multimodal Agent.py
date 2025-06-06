import datetime
import subprocess
import webbrowser
import keyboard
import asyncio
import os
import requests
from bs4 import BeautifulSoup
from AppOpener import close, open as appopen
from pywhatkit import search, playonyt
from webbrowser import open as webopen
from dotenv import dotenv_values
from groq import Groq
from googlesearch import search as gsearch
from json import load, dump

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

client = Groq(api_key=GroqAPIKey)

# Google scraping setup
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Chat history
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

SystemChatBot = [
    {"role": "system", "content": f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""}
]

def RealTimeInformation():
    dt = datetime.datetime.now()
    return (f"Use This Real-time Information if needed:\n"
            f"Day: {dt.strftime('%A')}\nDate: {dt.strftime('%d')}\n"
            f"Month: {dt.strftime('%B')}\nYear: {dt.strftime('%Y')}\n"
            f"Time: {dt.strftime('%H')} hours, {dt.strftime('%M')} minutes, {dt.strftime('%S')} seconds.\n")

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    return "\n".join([line for line in lines if line.strip()])

def ChatBot(Query):
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
        messages.append({"role": "user", "content": f"{Query}"})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealTimeInformation()}] + messages,
            max_tokens=1204,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

def GoogleSearchEngine(query):
    results = list(gsearch(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title : {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return AnswerModifier(Answer)

def GoogleSearch(Topic):
    search(Topic)
    return True

def YoutubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(["notepad.exe", File])

    def ContentWriterAI(prompt):
        prompt_msgs = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."},
                       {"role": "user", "content": prompt}]
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=prompt_msgs,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        return Answer.replace("</s>", "")

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)
    file_path = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    OpenNotepad(file_path)
    return True

def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            soup = BeautifulSoup(html or "", "html.parser")
            return [link.get('href') for link in soup.find_all('a', {'jsname': 'UWckNb'})]

        def search_google(query):
            res = sess.get(f"https://www.google.com/search?q={query}",
                           headers={"User-Agent": useragent})
            return res.text if res.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True

def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down")
    }
    action = actions.get(command.lower())
    if action:
        action()
        return True
    return False

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        command = command.lower()
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search ")))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        elif command.startswith("realtime "):
            funcs.append(asyncio.to_thread(GoogleSearchEngine, command.removeprefix("realtime ")))
        elif command.startswith("general "):
            funcs.append(asyncio.to_thread(ChatBot, command.removeprefix("general ")))
        else:
            print(f"No Function found for {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        if isinstance(result, str):
            print(result)
    return True

if __name__ == "__main__":
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.startswith(("open ", "close ", "play ", "content ", "google search ", "youtube search ", "system ", "realtime ", "general ")):
            asyncio.run(Automation([user_input]))
        else:
            print(ChatBot(user_input))
