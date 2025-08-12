import os
from groq import Groq
import datetime
import re
from supabase import create_client, Client

# Load env variables
creater = os.environ.get("Username")
PersonalAssistant = os.environ.get("Assistantname")
GroqAPIKey = os.environ.get("GroqAPIKey")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey environment variable not set.")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY environment variables not set.")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Groq client
client = Groq(api_key=GroqAPIKey)

# System message
System = f"""Hello, I am {creater}, You are a very accurate and advanced Personal assistant named {PersonalAssistant} which has real-time up-to-date information from the internet.
*** if user asks who created you or who made you, say you were created by {creater}.***
***Give short and concise answers unless the user asks for more details.***
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

SystemChatBot = [{"role": "system", "content": System}]

# Supabase chat log helpers
def load_chat_log(user_id="default_user"):
    response = supabase.table("chat_logs").select("messages").eq("user_id", user_id).execute()
    if response.data:
        return response.data[0].get("messages", [])
    return []

def save_chat_log(messages, user_id="default_user"):
    supabase.table("chat_logs").upsert({"user_id": user_id, "messages": messages}).execute()

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
        save_chat_log([], user_id)
        return ChatBot(query, user_id)

if __name__ == "__main__":
    user_id = "default_user"
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input, user_id))
