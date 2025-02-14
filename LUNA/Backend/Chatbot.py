from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return f"Day: {current_date_time.strftime('%A')}, Date: {current_date_time.strftime('%d')} {current_date_time.strftime('%B')} {current_date_time.strftime('%Y')}, Time: {current_date_time.strftime('%H:%M:%S')}."

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
{RealtimeInformation()}
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# Ensure ChatLog is properly loaded
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
        if not isinstance(messages, list):  # Ensure it's a list
            messages = []
except (FileNotFoundError, ValueError):  
    messages = []

def AnswerModifier(Answer):
    return "\n".join(line for line in Answer.split("\n") if line.strip())

def ChatBot(Query):
    try:
        messages.append({"role": "user", "content": Query})  # Correct role name

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = "".join(chunk.choices[0].delta.content or "" for chunk in completion)

        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))