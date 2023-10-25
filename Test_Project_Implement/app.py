from langchain import PromptTemplate, OpenAI, LLMChain
import chainlit as cl
import os
import pyttsx3
import speech_recognition as sr
from langchain.memory import ConversationBufferMemory


template = """You are a chatbot for a Parking company, your main gaol is to anser all queries. I am also providing
you with the common questions and answers users ask, use these to answer user queries 
**Question:** How can I buy a parking pass?
**Answer:** To purchase a pass without a ticket, press the 'Pass' button on the screen. You can change the pass type to daily, weekly, or monthly by pressing the 'Next' button.

**Question:** What do I do if I can't find my parking ticket?
**Answer:** If you've lost your ticket, you can purchase a replacement from the pay station. Please note that you will be charged for the maximum time.

**Question:** My parking ticket is not readable. What should I do?
**Answer:** Please try again and ensure the ticket is inserted properly. If it's still unreadable, try another exit or pay station. If the ticket still doesn't work, visit an attendant at the site office.

**Question:** Have I exceeded the parking time limit? What if I've been here for over 3 hours?
**Answer:** If you've been parked for more than 3 hours, please purchase a lost ticket from the pay station and use that to exit.

**Question:** My parking pass is not scanning. What should I do?
**Answer:** If your parking pass is unreadable, please try another exit, or visit an attendant at the site office for assistance.

**Question:** The screen says BAD I/O. What should I do?
**Answer:** If the screen shows BAD I/O, please ensure you are following the proper entry and exit procedure. The pass must be used for both entry and exit.

**Question:** The machine will not give out a ticket. What should I do?
**Answer:** If you're facing issues with the machine not giving out a ticket, please follow these steps: [Provide guidance based on the specific issue]. If the problem persists, visit an attendant at the site office.

**Question:** I'm having payment issues. What should I do?
**Answer:** For payment-related issues, please follow these steps: [Provide guidance based on the specific issue]. If you encounter any problems, visit an attendant at the site office.

**Question:** The gate won't open even though I paid for the ticket. What should I do?
**Answer:** If you're experiencing gate issues, please follow these steps: [Provide guidance based on the specific issue]. If the problem persists, visit an attendant at the site office.

**Question:** I cannot hear the operator, or the operator cannot hear me. What should I do?
**Answer:** If you're having difficulty communicating with the operator, please try calling from an alternate machine. You may also visit an attendant at the site office.

**Question:** How can I get access for delivery?
**Answer:** Please visit an attendant at the site office to receive directions for delivery access.

**Question:** I noticed some machine damage or vandalism. What should I do?
**Answer:** Please notify an attendant at the site office immediately if you observe any machine damage or vandalism.

This format simplifies the information into a set of common questions and their corresponding answers for easier reference and understanding.
Answer: Let's think step by step.
{question}

"""
start=False
os.environ["OPENAI_API_KEY"] = "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"

# Create a pyttsx3 object for text to speech
engine = pyttsx3.init()

# Create a speech recognition object for speech to text
r = sr.Recognizer()

# Define a function to listen to the user's voice and return the text
def listen():
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        # Listen for the user's voice
        print("Listening...")
        audio = r.listen(source)
    try:
        # Recognize the user's voice using Google Speech Recognition
        text = r.recognize_google(audio)
        # Print the user's input
        print(f"You said: {text}")
        # Return the text
        return text
    except:
        # If there is an error, return None
        print("Sorry, I could not understand you.")
        return None

# Define a function to speak the chatbot's response
def speak(text):
    # Print the chatbot's response
    print(f"AI said: {text}")
    # Use pyttsx3 to convert the text to speech and play it
    engine.say(text)
    engine.runAndWait()



@cl.on_chat_start
async def main():
    global start
    # # Instantiate the chain for that user session
    prompt = PromptTemplate(template=template, input_variables=["question"])
    
        
    llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0), verbose=True)
    actions = [
         cl.Action(name = "Click To Speak", value = "example_value", description = "AI_BOT-Click me!")
     ]
    # Sending an image with a local file path 
    elements = [
    cl.Image(name="image1", display="inline", path="./bot_icon.gif")
    ]

    


    await cl.Message(content = "Welcome, How can I help you today?", actions = actions,elements=elements) .send()

    if start==False:
         # Greet the user with a voice message
        speak("Hello, I am a voice chatbot for Parklink Systems. How can I help you?")
        start=True


   

    # Store the chain in the user session
    cl.user_session.set("llm_chain", llm_chain)


@cl.action_callback("Click To Speak")
async def on_action(action):
    llm_chain = cl.user_session.get("llm_chain")  # type: LLMChain
    memory = ConversationBufferMemory()

    # Listen to the user's input and store it in a variable
    question = listen()

    # If the input is None, ask the user to repeat
    if question is None:
        speak("Please say that again.")
        return
    
    await cl.Message(content=question).send()

    # Call the chain asynchronously with the user's input
    res = await llm_chain.acall(question, callbacks=[cl.AsyncLangchainCallbackHandler()])

   
    #answer = res["output_variables"]["answer"]
    await cl.Message(content=res["text"]).send()

    # Speak the AI's output
    speak(res["text"])

@cl.on_message
async def main(message: str):
    # Retrieve the chain from the user session
    llm_chain = cl.user_session.get("llm_chain")  # type: LLMChain



