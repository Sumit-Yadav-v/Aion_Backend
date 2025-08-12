from googlesearch import search
from groq import Groq
import datetime
import os
import json
from supabase import create_client, Client  # Supabase client

# --- Supabase Initialization ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase credentials are not set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Retrieve environment variables ---
creater = os.environ.get("Username")
PersonalAssistant = os.environ.get("Assistantname")
GroqAPIKey = os.environ.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey environment variable not set.")

# --- Create Groq client ---
client = Groq(api_key=GroqAPIKey)

# --- System message ---
System = f"""Hello, I am {creater}, You are a very accurate and advanced Personal assistant named {PersonalAssistant} which has real-time up-to-date information from the internet.
*** if user asks who created you, say you were created by {creater}.***
***Give short and concise answers unless the user asks for more details.***
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# --- Supabase DB functions ---
def load_chat_log(user_id="default_user"):
    res = supabase.table("chat_logs").select("messages").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]["messages"]
    return []

def save_chat_log(messages, user_id="default_user"):
    supabase.table("chat_logs").upsert({
        "user_id": user_id,
        "messages": messages
    }).execute()

# --- Google Search helper ---
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n\n"
    
    for i in results:
        Answer += f"Link: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

# --- Format answer ---
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# --- System ChatBot memory ---
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "hi"},
    {"role": "assistant", "content": "Hello, I am your personal assistant. How can I help you today?"}
]

# --- Real-time info ---
def Information():
    now = datetime.datetime.now()
    return (
        f"Use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours : {now.strftime('%M')} minutes : {now.strftime('%S')} seconds\n"
    )

# --- Main chatbot function ---
def RealtimeSearchEngine(prompt, user_id="default_user"):
    global SystemChatBot

    messages = load_chat_log(user_id)[-10:]  # last 10 messages
    messages.append({"role": "user", "content": prompt})

    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "user", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=4048,
        top_p=1.0,
        stream=True,
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip()
    messages.append({"role": "assistant", "content": Answer})

    save_chat_log(messages, user_id)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

# --- Run locally ---
if __name__ == "__main__":
    user_id = "default_user"
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt, user_id))
