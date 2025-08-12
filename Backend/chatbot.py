import os
from groq import Groq
import datetime
import re
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import dotenv_values

# Initialize Firebase Admin SDK once
if not firebase_admin._apps:
    cred_json = os.environ.get("FIREBASE_CRED_JSON")
    if not cred_json:
        raise RuntimeError("FIREBASE_CRED_JSON environment variable not set")
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

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

# Firestore chat log helpers
def load_chat_log(user_id="default_user"):
    doc_ref = db.collection("chat_logs").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("messages", [])
    else:
        return []

def save_chat_log(messages, user_id="default_user"):
    doc_ref = db.collection("chat_logs").document(user_id)
    doc_ref.set({"messages": messages})

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

def ChatBot(query, user_id="default_user"):
    try:
        messages = load_chat_log(user_id)

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

        save_chat_log(messages, user_id)

        return answer

    except Exception as e:
        print(f"Error: {e}")
        # Reset chat log on error
        save_chat_log([], user_id)
        return ChatBot(query, user_id)

if __name__ == "__main__":
    user_id = "default_user"  # Change if you want multiple user sessions
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input, user_id))
