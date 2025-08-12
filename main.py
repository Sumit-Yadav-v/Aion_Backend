from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.chatbot import ChatBot

#Query modifier to clean up the input query
def QueryModifier(Query):
      new_query = Query.lower().strip()  
      query_words = new_query.split()
      question_words = ["what", "who", "where", "when", "why", "how","whose", "which", "can you", "could you", "would you", "what's", "who's", "where's", "when's", "why's", "how's","whats"]
 # Check if the query starts with a question word
      if any(word + " " in new_query for word in question_words):
          if query_words[0][0] in ['.', '?', '!']:
                  new_query = new_query[:-1] + "?"  # Add a question mark if it doesn't end with one
          else:
                new_query+= "?"
      else:
        #add a period at the end if it doesn't already have one
          if query_words[0][0] in ['.', '?', '!']:
                  new_query = new_query[:-1] + "."  # Add a period if it doesn't end with one
          else:
                new_query += "."

      return new_query.capitalize() 


app = FastAPI()

class Query(BaseModel):
    text: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
def chat(query: Query):
    print(f"\n--- Incoming Query ---\n{query.text}\n")

    Decision = FirstLayerDMM(query.text)
    print(f"Decision List: {Decision}")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Mearged_query = " and ".join(
        " ".join(i.split()[1:]) 
        for i in Decision if i.startswith("general") or i.startswith("realtime")
    )

    # Both general + realtime
    if G and R:
        engine = "RealtimeSearchEngine"
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        print(f"Engine: {engine}\nModel Reply: {Answer}\n")
        return {"answer": Answer, "engine": engine}

    # One or the other
    for Queries in Decision:
        if "general" in Queries:
            engine = "ChatBot"
            QueryFinal = Queries.replace("general ", "")
            Answer = ChatBot(QueryModifier(QueryFinal))
            print(f"Engine: {engine}\nModel Reply: {Answer}\n")
            return {"answer": Answer, "engine": engine}

        elif "realtime" in Queries:
            engine = "RealtimeSearchEngine"
            QueryFinal = Queries.replace("realtime ", "")
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            print(f"Engine: {engine}\nModel Reply: {Answer}\n")
            return {"answer": Answer, "engine": engine}

        elif "exit" in Queries:
            engine = "Exit"
            Answer = "OK, Bye, have a nice day!"
            print(f"Engine: {engine}\nModel Reply: {Answer}\n")
            return {"answer": Answer, "engine": engine}

    engine = "Unknown"
    Answer = "I'm not sure how to respond."
    print(f"Engine: {engine}\nModel Reply: {Answer}\n")
    return {"answer": Answer, "engine": engine}
