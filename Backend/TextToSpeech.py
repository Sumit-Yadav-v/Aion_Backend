import pygame # Importing the pygame library for audio playback
import random # Importing the random library for generating random numbers
import asyncio # Importing asyncio for asynchronous programming
import edge_tts
import os # Importing os for file path operations
from dotenv import dotenv_values # Importing dotenv to load environment variables

# Load environment variables from .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice") # Get the assistant voice from environment variables

#Asynchronous function to convert text to speech
async def TextToAudioFile(text)-> None:
    file_path = r"Data\speech.mp3" # Path to the audio file
    if os.path.exists(file_path): # Check if the file already exists
        os.remove(file_path) # Remove the existing file

    #creare the communicate object to generate speech
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%') # Create a communicate object with the text and voice parameters
    await communicate.save(r'Data\speech.mp3') # Save the generated speech to the specified file path

    #Function to manage Text-to-speech (TTS) functionality
def TTS(Text,func=lambda r=None: (True)):
     while True:
        try:
            #convert text to an audio file asynchronously
            asyncio.run(TextToAudioFile(Text))  

                #Initialize pygame mixer for audio playback
            pygame.mixer.init()

                #Load the generated speech file into pygame mixer
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play() # Play the audio file

                #Loop until the audio playback is finished
            while pygame.mixer.music.get_busy():
                if func() == False:
                        break
                pygame.time.Clock().tick(10) # Wait for a short time to avoid busy-waiting

            return True #return if the audio played successfully 
        except Exception as e:
            print(f"Error in TTS: {e}") 
                 
        finally:
            try:
                    #call the provided function with false to siganl the end of TTS
                func(False)
                pygame.mixer.music.stop() #stop the audio playback
                pygame.mixer.quit() #Quit the pygame mixer

            except Exception as e: #handle any exceptions during cleanup
                print(f"Error in the finally block: {e}")

#function to manage Text-to-speech with additional responses for long text
def TextToSpeech(Text,func=lambda r=None: True):
    Data = str(Text).split(".") #split the text by periods into a list of the sentances

    #list of predefined responses for the cases where the text is too long
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

    #if the text is very long (more than 4 sentences and 250 characters), add a response message
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses),func)

        #otherwise just play the whole text
    else:
        TTS(Text, func)

#main execution loop
if __name__ == "__main__":
    while True:
        #prompt user for input and it to TextToSpeech function
        TextToSpeech(input("Enter the text: "))

