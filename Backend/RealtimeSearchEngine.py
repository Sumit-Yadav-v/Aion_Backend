from googlesearch import search
from groq import Groq
from json import dump, load
from dotenv import dotenv_values
import datetime

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Retrieve information from environment variables
creater = env_vars.get("Username")
PersonalAssistant = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Create a Groq client
client = Groq(api_key=GroqAPIKey)  # Groq API client for AI model interaction

#define a system message to set the context for the AI model
System = f"""Hello, I am {creater}, You are a very accurate and advanced Personal assistant named {PersonalAssistant} which has real-time up-to-date information from the internet.
*** if user asks who created you, say you were created by {creater}.***
***Give short and concise answers unless the user asks for more details.***
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""



#try to load chat history from a JSON file
try:
    with open(r".\Data\ChatLog.json", "r") as f:
        messages = load(f)

except:
    with open(r".\Data\ChatLog.json", "w") as f:
        dump([], f)

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n\n"
    
    for i in results:
        Answer += f"Link: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    #print(Answer)  
    return Answer

    

# function to clean uo the answer by removing unnecessary text
def AnswerModifier(Answer):
    # remove the system message from the answer
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


    #predfine chatbot conversation system message and initial message for the AI model
SystemChatBot = [
        {"role": "system", "content": System},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "Hello, I am your personal assistant. How can I help you today?"}
    ]


 #Function to get real-time like the current date and time
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
        #format the information into a string
    data += f"Use this real-time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds\n"
    return data
    

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    #load the chat log from the JSON file
    with open(r".\Data\ChatLog.json", "r") as f:
        messages = load(f)
        messages = messages[-10:]  
    messages.append({"role": "user", "content": f"{prompt}"})

    #Add Google search results to the chat log
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    #Generate a response using the Groq client 
    completion = client.chat.completions.create(
        model="llama3-70b-8192",  # specify the model to use
        messages=SystemChatBot + [{"role": "user", "content": Information()}] + messages,  # include system instructions and real-time information
        temperature=0.7, 
        max_tokens=4048, # set creativity level of the model
        top_p=1.0,  # set the top-p value for nucleus sampling
        stream=True,  # enable streaming for real-time response
        stop=None,  # no specific stop sequence
    )

    Answer = ""

    #concatenate response chunks from the streaming output
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    #clean up the response 
    Answer = Answer.strip().replace("\\s", "")  
    messages.append({"role": "assistant", "content": Answer})  

    #save the updated chat log to the JSON file
    with open(r".\Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    #remove the most recent system message (Google search results) 
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)  # return the cleaned-up answer

#main entry point for the module
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))  