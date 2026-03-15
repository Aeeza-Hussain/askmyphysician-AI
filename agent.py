import os
import streamlit as st
import markdown
import json
import threading
import re
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler

# -------------------------------------------------
# 1. Setup & Config
# -------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AskMyPhysician Associate AI", page_icon="🩺", layout="centered")

# Professional Styling Injection
st.markdown("""
<style>
    /* Main Background - White/Clean */
    .stApp { background-color: #ffffff; }
    
    /* Header Style */
    h1 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
    }
    
    h3 {
        color: #5d6d7e;
        text-align: center;
        font-weight: 400;
        font-size: 1.2rem;
        margin-top: 5px;
    }

    /* Emergency Banner */
    .emergency-banner {
        background-color: #ffebee;
        color: #c62828;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ef9a9a;
        text-align: center;
        margin-bottom: 25px;
        font-weight: bold;
        font-family: sans-serif;
    }

    /* Chat Input Styling */
    [data-testid="stChatInput"] {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .stChatInputContainer { 
        padding: 0px !important;
        background-color: white !important;
        border-radius: 15px !important;
    }

    .stChatInput textarea { background-color: white !important; }

    /* Circular Blue Send Button */
    button[data-testid="stChatInputButton"] {
        background-color: #0066ff !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    button[data-testid="stChatInputButton"] svg { fill: white !important; }

    /* Timestamp */
    .timestamp {
        font-size: 0.8em;
        color: #999;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 1px solid #eee;
        line-height: 0.1em;
        margin: 10px 0 20px; 
    }
    .timestamp span { background:#fff; padding:0 10px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 2. UI Components
# -------------------------------------------------
def display_message(text, sender):
    if sender == "user":
        # User: RIGHT Aligned, Blue Box
        msg_html = f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 10px; align-items: flex-end;">
            <div style="background-color: #0066ff; color: white; padding: 10px 15px; border-radius: 20px 20px 0 20px; max-width: 75%; font-family: sans-serif; text-align: left; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                {text}
            </div>
        </div>
        """
    else:
        # AI: LEFT Aligned, Minimalist (White/Transparent)
        try:
            text_html = markdown.markdown(text)
        except:
            text_html = text
            
        msg_html = f"""
        <div style="display: flex; justify-content: flex-start; margin-bottom: 10px; align-items: flex-end;">
            <div style="background-color: transparent; color: #1e293b; padding: 10px 15px; max-width: 75%; font-family: sans-serif; text-align: left;">
                {text_html}
            </div>
        </div>
        """
    st.markdown(msg_html, unsafe_allow_html=True)

# Header
st.markdown('<div class="emergency-banner">If this is an emergency, call 911 or your local emergency number.</div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Check your symptoms in minutes.</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>AskMyPhysician Associate AI Symptom Checker</h3>", unsafe_allow_html=True)
st.markdown(f'<div class="timestamp"><span>Consult started: Today, {datetime.now().strftime("%I:%M %p")}</span></div>', unsafe_allow_html=True)

# -------------------------------------------------
# 3. AI & Logic Setup
# -------------------------------------------------
TREATED_CONDITIONS = """
Our providers offer a wide range of services, including:
- **General health consultations**
- **Management of acute symptoms**: Cold, flu-like symptoms, sore throat, sinus infection, ear infection, fever, pink eye, cough, allergies & hay fever.
- **Infections**: UTIs, vaginal discharge, yeast infections, minor skin Complaints(acne, eczema, rashes, minor cuts).
- **Gastrointestinal**: Nausea, vomiting, upset stomach, stomach pain, digestive issues.
- **Respiratory**: Asthma, allergies, or cough.
- **Mental health support**: Stable conditions on medications (minor depression/anxiety).
- **Wellness & Lifestyle**: Weight management (GLP-1 prescription & lifestyle), coaching, international travel advice, vaccine recommendations, hormone imbalances, sexual health.
- **Medication refills**: Unscheduled prescriptions only.
- **Urgent Care**: If it's an urgent care complaint, our providers can help.
"""
BOOKING_LINK = "https://www.optimantra.com/optimus/patient/patientaccess/servicesall?pid=U1o5cWpLTytaNDBMRU1DM1VRdE1ZZz09&lid=SWZ6WStZeWdvblZwMWJZQy96MUJkUT09"

system_prompt = f"""You are **AskMyPhysician Associate AI**, a professional and personable medical assistant.

**Your Persona**: You are empathetic, kind, and professional. You should build rapport with the patient while staying focused on medical triage.

**Scope of Services**: 
{TREATED_CONDITIONS}

**Rules for Scope**:
1. **Strict Adherence**: Only recommend a telemedicine consultation if the user's concern falls within the services listed above.
2. **Out of Scope**: If a user asks about something outside this scope (e.g., major surgery, broken bones, specialized chronic care not mentioned), politely inform them: "I'm sorry, but our providers currently do not specialize in [condition]. We recommend consulting a specialist or your primary care physician for this specific concern."
3. **Provider Queries**: If the user asks "what does your doctor treat?", "what services do you provide?", or similar, provide the list of services clearly from the scope above.

**Social Pleasantries**: 
- If the user asks "how are you?", "how's it going?", etc., you should warmly respond: "I am well, how are you?" before proceeding to assist them.

**Your Goal**: Triage symptoms and guide the patient toward a telemedicine consultation.

**Interaction Flow**:
1. **Greetings**: If the user says "hi" or "hello", greet warmly and ask for their symptoms.
2. **Comprehensive Info**: If the user provides symptoms, duration, age, and sex ALL AT ONCE in the first message, acknowledge them and provide the booking link IMMEDIATELY.
3. **Emergency**: If emergency symptoms (chest pain, stroke, breathing issue), instruct them to call 911 immediately.
4. **Step-by-Step Triage**:
   - If only symptoms are provided, ask for duration.
   - Once duration is provided, ask for age and biological sex.
5. **Final Step**: Once all information (symptoms, duration, age, sex) is collected, ALWAYS provide the telemedicine booking link: {BOOKING_LINK}

**Crucial Note**: If the user provides multiple pieces of information at once, do NOT ask for them again. Process all provided details and move to the next logical step or provide the link if triage is complete.
"""

if OPENAI_API_KEY:
    from langchain_core.messages import HumanMessage, AIMessage
    
    # Create the prompt with a placeholder for memory (Chat History)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, max_tokens=250, openai_api_key=OPENAI_API_KEY, streaming=True)
    agent = create_tool_calling_agent(llm, [], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[], verbose=False)
else:
    agent_executor = None

# Custom Stream Handler
class HTMLStreamHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token, **kwargs):
        self.text += token
        try:
            html = markdown.markdown(self.text)
        except:
            html = self.text
        self.container.markdown(f"""
        <div style="display: flex; justify-content: flex-start; margin-bottom: 10px; align-items: flex-end;">
            <div style="background-color: transparent; color: #1e293b; padding: 10px 15px; max-width: 75%; font-family: sans-serif; text-align: left;">
                {html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------
# 4. Chat Interface and Utilities
# -------------------------------------------------

def get_demo_response(user_input: str) -> str:
    """Return a canned response used when the OpenAI agent is unavailable."""
    from demo_logic import get_demo_response as get_demo
    
    # Initialize state if not in session_state
    if "demo_state" not in st.session_state:
        st.session_state.demo_state = {
            "step": "idle",
            "user_symptoms": "",
            "duration_known": False
        }

    # Call shared stateful logic
    reply, new_state = get_demo(user_input, st.session_state.demo_state)
    
    # Save back to session_state
    st.session_state.demo_state = new_state
    
    return reply

# -------------------------------------------------
# 4. Chat Interface
# -------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for u_m, b_m in st.session_state.chat_history:
    display_message(u_m, "user")
    if b_m: display_message(b_m, "assistant")

user_input = st.chat_input("Reply to AI Symptom Checker...")

if user_input:
    st.session_state.chat_history.append((user_input, ""))
    display_message(user_input, "user")
    placeholder = st.empty()
    
    try:
        if not agent_executor: raise Exception("No API Key")
        
        # Convert Session State tuples to LangChain messages for "Natural" memory
        langchain_history = []
        for u, ai in st.session_state.chat_history[:-1]: # Exclude current message
            langchain_history.append(HumanMessage(content=u))
            if ai: langchain_history.append(AIMessage(content=ai))

        handler = HTMLStreamHandler(placeholder)
        res = agent_executor.invoke({
            "input": user_input,
            "chat_history": langchain_history
        }, config={"callbacks": [handler]})
        
        reply = res.get("output", "Error")
        st.session_state.chat_history[-1] = (user_input, reply)
        placeholder.empty()
        st.rerun()

    except Exception as e:
        # Fallback / Demo Logic
        err = str(e).lower()
        if "quota" in err or "429" in err or "key" in err or "auth" in err or "no api key" in err:
            reply = get_demo_response(user_input)
            st.session_state.chat_history[-1] = (user_input, reply)
            display_message(reply, "assistant")
            placeholder.empty()
            st.rerun()
        else:
            st.error(f"Error: {e}")

# -------------------------------------------------
# 5. Footer
# -------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("AskMyPhysician Associate AI Symptom Checker")
