from googlesearch import search
from groq import Groq
from json import dump, load
from dotenv import dotenv_values
import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred_json = os.environ.get("FIREBASE_CRED_JSON")
    if not cred_json:
        raise RuntimeError("FIREBASE_CRED_JSON environment variable not set")
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Retrieve environment variables
creater = os.environ.get("Username")
PersonalAssistant = os.environ.get("Assistantname")
GroqAPIKey = os.environ.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey environment variable not set.")

# Create a Groq client
client = Groq(api_key=GroqAPIKey)  # Groq API client for AI model interaction

# Define a system message to set the context for the AI model
System = f"""Hello, I am {creater}, You are a very accurate and advanced Personal assistant named {PersonalAssistant} which has real-time up-to-date information from the internet.
*** if user asks who created you, say you were created by {creater}.***
***Give short and concise answers unless the user asks for more details.***
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Helper functions to load/save chat log from Firestore
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

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n\n"
    
    for i in results:
        # i is a SearchResult object with title and description attributes
        Answer += f"Link: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "hi"},
    {"role": "assistant", "content": "Hello, I am your personal assistant. How can I help you today?"}
]

def Information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = f"Use this real-time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds\n"
    return data

def RealtimeSearchEngine(prompt, user_id="default_user"):
    global SystemChatBot

    messages = load_chat_log(user_id)
    messages = messages[-10:]
    messages.append({"role": "user", "content": prompt})

    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "user", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=4048,
        top_p=1.0,
        stream=True,
        stop=None,
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("\\s", "")
    messages.append({"role": "assistant", "content": Answer})

    save_chat_log(messages, user_id)

    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

if __name__ == "__main__":
    user_id = "default_user"  # You can customize or fetch dynamically per user
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt, user_id))
