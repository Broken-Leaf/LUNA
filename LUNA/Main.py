from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    SetMicrophoneStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus )
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import TextToSpeech
from Backend.Chatbot import ChatBot
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import random

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
Greet = env_vars.get("Greet")
DefaultMessage = f'''{Username} : Hey {Assistantname}, How are You?
{Assistantname} : Welcome sir !!. I am doing well. How may I assist you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def GreetUser():
    try:
        print("GreetUser() function started")
        with open(r'Data\greeting.json', 'r', encoding='utf-8') as file:
            greetings_data = json.load(file)
        greetings = greetings_data.get("greetings", [])
        if not greetings:
            raise ValueError("Greeting list is empty!")
        greeting_message = random.choice(greetings).replace("{Greet}", Greet)
        print(f"Greeting selected: {greeting_message}")
        run(TextToSpeech(greeting_message))
    except Exception as e:
        print(f"Error in GreetUser: {e}")

def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = "User" if entry["role"] == "user" else "Assistant"
        formatted_chatlog += f"{role} : {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", f"{Username} ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", f"{Assistantname} ")
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as File:
        Data = File.read()
    if len(Data) > 0:
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as File:
            File.write(Data)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()
    GreetUser()

InitialExecution()

def MainExecution():
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    print(f"\nDecision: {Decision}\n")

    ImageExecution = False
    ImageGenerationQuery = ""

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = queries
            ImageExecution = True
            break

    TaskExecution = any(queries.startswith(func) for queries in Decision for func in Functions)

    if TaskExecution:
        try:
            run(Automation(list(Decision)))
        except Exception as e:
            print(f"Error in Automation: {e}")

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error in ImageGeneration.py: {e}")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        run(TextToSpeech(Answer))
        return

    for queries in Decision:
        if "general" in queries:
            SetAssistantStatus("Thinking...")
            Answer = ChatBot(QueryModifier(queries.replace("general", "")))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            run(TextToSpeech(Answer))
            return
        elif "realtime" in queries:
            SetAssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(queries.replace("realtime", "")))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            run(TextToSpeech(Answer))
            return
        elif "exit" in queries:
            SetAssistantStatus("Answering...")
            run(TextToSpeech("Okay, Bye!"))
            os._exit(1)

def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        elif "Available..." not in GetAssistantStatus():
            SetAssistantStatus("Available...")
        sleep(0.1)

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    threading.Thread(target=FirstThread, daemon=True).start()
    SecondThread()