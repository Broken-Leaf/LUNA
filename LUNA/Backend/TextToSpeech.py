import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values


env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice") or "en-US-JennyNeural"

async def TextToAudioFile(Text):
    file_path = r"Data\speech.mp3"
    

    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(Text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def play_audio(file_path, func):
    """Plays audio using pygame and ensures proper cleanup."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        if func() == False:
            break
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

async def TTS(Text, func=lambda r=None: True):
    try:
        await TextToAudioFile(Text)
        play_audio(r"Data\speech.mp3", func)
    except Exception as e:
        print(f"Error in TTS: {e}")
    finally:
        try:
            func(False)
        except Exception as e:
            print(f"Error in finally block: {e}")

async def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
    
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    short_text = " ".join(Data[:2]) if len(Data) > 1 else Text

    if len(Data) > 4 and len(Text) >= 250:
        await TTS(short_text + ". " + random.choice(responses), func)
    else:
        await TTS(Text, func)

if __name__ == "__main__":
    asyncio.run(TextToSpeech())