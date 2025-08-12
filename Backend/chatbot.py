import os
from groq import Groq
from json import dump, load
import datetime
from dotenv import dotenv_values
import re

# Ensure Data folder exists
os.makedirs("Data", exist_ok=True)

# Load .env file locally (won't affect Vercel since .env usually isn't present there)
load_dotenv()

# Get environment variables
creater = os.environ.get("Username")
PersonalAssistant = os.environ.get("Assistantname")
GroqAPIKey = os.environ.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey environment variable not set.")

# Create Groq client
client = Groq(api_key=GroqAPIKey)

# System message
System = f"""Hello, I am {creater}, You are a very accurate and advanced Personal assistant named {PersonalAssistant} which has real-time up-to-date information from the internet.
*** if user asks who created you or who made you, say you were created by {creater}.***
***Give short and concise answers unless the user asks for more details.***
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


SystemChatBot = [{"role": "system", "content": System}]

# Try to load chat log or create it
if not os.path.exists("Data/ChatLog.json"):
    with open("Data/ChatLog.json", "w") as f:
        dump([], f)

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-information if needed,\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')}hours : {now.strftime('%M')}minutes : {now.strftime('%S')}seconds\n"
    )

def AnswerModifier(answer):
    # Remove extra whitespace
    return re.sub(r"\s+", " ", answer).strip()

def ChatBot(query):
    try:
        with open("Data/ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "user", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1.0,
            stream=True,
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = AnswerModifier(answer)

        messages.append({"role": "assistant", "content": answer})

        with open("Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return answer

    except Exception as e:
        print(f"Error: {e}")
        with open("Data/ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(query)

if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input))
