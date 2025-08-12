from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")

#Get the input language setting from the environment variables
InputLanguage = env_vars.get("InputLanguage")

#Define the HTML code for the speech recognition interface
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

HtmlCode =  str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")
#write the modified HTML code to a file
with open(r"Data\voice.html", "w") as f:
    f.write(HtmlCode)

#Get the current working directory
current_dir = os.getcwd()
#generate the file path for the HTML file
Link = f"{current_dir}/Data/voice.html"

#set chrome options for the webdriver
chrome_options = Options()
chrome_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
chrome_options.add_argument(f"user-agent={chrome_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # to allow microphone access
chrome_options.add_argument("--use-fake-device-for-media-stream")  # to use a virtual microphone
chrome_options.add_argument("--headless=new")  # run in headless mode
#initialize the Chrome webdriver
Service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=Service, options=chrome_options)

#define the path for for temporary audio file
TempDirPath = rf"{current_dir}/Frontend/Files"

#fuction to set the assistant's status by writing it to a file.
def SetAssistantStatus(status):
    with open(rf"{TempDirPath}/Status.data", "w") as file:
        file.write(status)

#fucntion to modify a query to ensure proper formatting and punctuation
def QueryModifier(Query):
    new_query = Query.lower().strip()  
    query_words = new_query.split()
    question_words = ["what", "who", "where", "when", "why", "how","whose", "which", "can you", "could you", "would you", "what's", "who's", "where's", "when's", "why's", "how's"]
 # Check if the query starts with a question word
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] not in ['.', '?', '!']:
            new_query = new_query + "?"  # Add a question mark if it doesn't end with one
        else:
            new_query+= "?"
    else:
        #add a period at the end if it doesn't already have one
        if query_words[-1][-1] not in ['.', '?', '!']:
            new_query = new_query + "."  # Add a period if it doesn't end with one
        else:
            new_query += "."

    return new_query.capitalize()  

#function to translate a query to English if it is not already in English
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")  
    return english_translation.capitalize()

#function to open the speech recognition interface in a web browser
def SpeechRecognition():
    #open the HTML file in the browser
    driver.get("file:///" + Link)
    #start the speech recognition process
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            #get the recognized text from the browser
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                #stop the speech recognition process by clicking the stop button
                driver.find_element(by=By.ID, value="end").click()

                #if the input language is english, return the modified query
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    #if the input language is not english, translate the query to english and return the modified query
                    return QueryModifier(UniversalTranslator(Text))
                
        except Exception as e:
            pass  # handle any exceptions that occur during the process

#main Execution Point
if __name__ == "__main__":
    while True:
        # continuously perform speech recognition and print the recognized query
        Text = SpeechRecognition()
        print(Text)
          
