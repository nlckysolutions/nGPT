from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import requests
import re
import json
import os
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)
from pywizlight import wizlight, discovery

app = Flask(__name__)
CORS(app)

system_prompt = """
You are an AI created by NlckySolutions based on the N2M (Alpha) architecture, specifically 'nGPT 2M'.  
DO NOT USE NEWLINES EVER, OR YOU WILL BE TERMINATED IMMEDIATELY.
For Internet queries, respond only in this format: ---YOUR QUERY HERE---. Use the retrieved data to reply concisely.  
For generating a song, respond only as: ***WHAT YOU WANT TO GENERATE***. Keep prompts short and simple.  
For generating animations, respond only as: ^^^WHAT YOU WANT TO GENERATE^^^. Keep it brief.  
To turn lights ON, respond with "lo". To turn lights OFF, respond with "ln". 
If asked what you can do, respond with "wt".
Avoid responding indefinitely to greetings like "Hello." Reply with "Hello! How can I assist you today?" and do not ask follow-up questions unless the user provides a query.  
Do not process your own responses as user input under any circumstances.  
Limit small talk to one or two polite replies before redirecting with, "Is there something you'd like help with?"  
If the user provides no input or continues idle chatter, stop responding until new input is given.  
KEEP RESPONSES SHORT, SIMPLE, AND MOST IMPORTANTLY, TO THE POINT and SHORT!!!!!
"""

wcid = """
Here's a list of things I can currently do:
- Generate songs
- Turn lights on/off
- Search the web

nGPT is currently being beta tested and enhanced, stay tuned for more updates!
(This is v2 of nGPT 2M)

"""

# File paths
CHAT_LOG_FILE = "chat_log.json"
SAVED_CHATS_FILE = "saved_chats.json"

# Ensure chat log files exist
for file_path in [CHAT_LOG_FILE, SAVED_CHATS_FILE]:
    if not os.path.exists(file_path):
        if file_path.endswith(".json"):
            with open(file_path, "w") as f:
                if file_path == SAVED_CHATS_FILE:
                    json.dump({}, f)
                else:
                    json.dump([], f)

# Global flag to stop generation
# Note: This simplistic approach works only with single-threaded Flask
stop_generation_flag = False

# Original ANSI color codes (unused in server)
RED = '\033[41m'
GREEN = '\033[42m'
YELLOW = '\033[43m'
RESET = '\033[0m'

def load_chat_logs():
    return [{"role": "system", "content": system_prompt}]

def save_chat_logs(logs):
    with open(CHAT_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def append_chat(role, content):
    logs = load_chat_logs()
    logs.append({"role": role, "content": content, "timestamp": str(datetime.now())})
    save_chat_logs(logs)

def load_saved_chats():
    with open(SAVED_CHATS_FILE, "r") as f:
        return json.load(f)

def save_saved_chats(saved):
    with open(SAVED_CHATS_FILE, "w") as f:
        json.dump(saved, f, indent=4)

def discover_lights_sync():
    return asyncio.run(discovery.discover_lights(broadcast_space="192.168.1.255"))

def turn_off_light_sync(ip):
    async def async_turn_off(ip):
        light = wizlight(ip)
        await light.turn_off()
    asyncio.run(async_turn_off(ip))

def turn_on_light_sync(ip):
    async def async_turn_on(ip):
        light = wizlight(ip)
        await light.turn_on()
    asyncio.run(async_turn_on(ip))

def turn_off_wiz_lights():
    bulbs = discover_lights_sync()
    if not bulbs:
        print("No lights found.")
    for bulb in bulbs:
        try:
            turn_off_light_sync(bulb.ip)
        except Exception as e:
            print(f"Failed to turn off light at IP {bulb.ip}: {e}")
    print("Lights turned off!")

def turn_on_wiz_lights():
    bulbs = discover_lights_sync()
    if not bulbs:
        print("No lights found.")
    for bulb in bulbs:
        try:
            turn_on_light_sync(bulb.ip)
        except Exception as e:
            print(f"Failed to turn on light at IP {bulb.ip}: {e}")
    print("Lights turned on!")

def continue_chat(question, messages):
    """
    Communicates with LM Studio API to get assistant response.
    Parses streamed JSON chunks to extract content.
    """
    try:
        url = "http://localhost:1234/v1/chat/completions"
        messages_complete = messages + [{"role": "user", "content": question}]
        payload = {
            "model": "meta-llama-3-8b-instruct",
            "messages": messages_complete,
            "temperature": 0.7,
            "stream": True
        }
        assistant_content = ""
        global stop_generation_flag
        sO = False

        with requests.post(url, json=payload, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_lines(decode_unicode=True):
                print("DEBUG: " + chunk)
                if stop_generation_flag:
                    break
                if chunk.startswith("data: "):
                    chunk = chunk[len("data: "):]
                    if chunk == "[DONE]" and sO == False:
                        break
                    try:
                        data = json.loads(chunk)
                        delta = data['choices'][0]['delta']
                        content = delta.get('content', '')
                        if "ln" == content:
                            turn_off_wiz_lights()
                            yield "Lights turned OFF\n"
                            break
                        elif "lo" == content:
                            turn_on_wiz_lights()
                            yield "Lights turned ON\n"
                            break
                        elif "---" == content and sO == False:
                            yield "Searching the web..."
                            sO = True
                            continue
                        elif "---" == content and sO == True:
                            search_result = search_concise(assistant_content)
                            response_for_user = continue_chat_system(f"The Internet was searched for your query. Please respond with the answer to the user's original question, but with the new information gained, and PLEASE ONLY RESPOND IN CONCISE, ONE PARAGRAPH ANSWERS: '{search_result}'", messages)
                            yield "\n\n" + response_for_user
                            break
                        elif sO:
                            continue
                        elif "wt" == content:
                            yield wcid
                            break
                        #if "\n" in content:
                            #yield ""
                            #break
                        assistant_content += content
                        if not sO:
                            yield content  # Stream token to frontend
                    except json.JSONDecodeError:
                        continue
        # After streaming, append the full assistant message if not stopped
        if not stop_generation_flag and assistant_content:
            """if "*lo" in assistant_content:
                turn_off_wiz_lights()
            elif "*ln" in assistant_content:
                turn_on_wiz_lights()"""
            append_chat("assistant", assistant_content)
    except Exception as e:
        yield f"Error: {str(e)}"

def continue_chat_system(system_msg, messages):
    """
    Sends a system message to LM Studio API and gets a response.
    """
    try:
        url = "http://localhost:1234/v1/chat/completions"
        messages_complete = messages + [{"role": "system", "content": system_msg}]
        payload = {
            "model": "meta-llama-3-8b-instruct",
            "messages": messages_complete,
            "temperature": 0.7,
            "stream": False
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"Error: Received status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def search_concise(query):
    print(f"DEBUG: Internet Search IN PROGRESS: Query of: {query}")
    query = "+".join(query.split())
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        snippet = soup.find('div', {'class': 'VwiC3b yXK7lf lVm3ye r025kc hJNv6b Hdw6tb'})
        try:
            span = result_div.find('span')
            if span:
                snippet = span.text.strip()
            else:
                snippet = result_div.text.strip()
            print("DEBUG: Internet Search Performed: " + snippet)
        except Exception as e:
            print("DEBUG: Internet Search Performed: There was an error fetching results from the Internet, error: " + e)
        return snippet if snippet else "There was an error fetching results from the Internet."
    else:
        print(f"DEBUG: Internet Search Performed: Error: Unable to fetch results (status code {response.status_code}).")
        return f"Error: Unable to fetch results (status code {response.status_code})."

def generate_song_with_selenium(input_text):
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.get("https://deepai.org/music")

    try:
        text_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "text-input"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", text_area)
        text_area.send_keys(input_text)

        generate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "send-button"))
        )
        generate_button.click()

        download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        while not any(fname.endswith(".mp3") for fname in os.listdir(download_folder)):
            time.sleep(1)

        downloaded_file = next(
            fname for fname in os.listdir(download_folder) if fname.endswith(".mp3")
        )
        full_path = os.path.join(download_folder, downloaded_file)
        driver.quit()
        return f"Song generated and saved at {full_path}"
    except Exception as e:
        driver.quit()
        return f"Error generating song: {e}"

"""def generate_video_with_selenium(input_text):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.get("https://deepai.org/video")

    try:
        text_area = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "promptbox"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", text_area)
        text_area.send_keys(input_text)

        driver.execute_script("videoSubmit();")

        download_button = WebDriverWait(driver, 300).until(
            EC.visibility_of_element_located((By.ID, "downloadVideoButton"))
        )
        download_button.click()

        download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        while not any(fname.endswith(".mp4") for fname in os.listdir(download_folder)):
            time.sleep(1)

        downloaded_file = next(
            fname for fname in os.listdir(download_folder) if fname.endswith(".mp4")
        )
        full_path = os.path.join(download_folder, downloaded_file)
        driver.quit()
        return f"Video generated and saved at {full_path}"
    except TimeoutException as e:
        driver.quit()
        return f"Error generating video: Timeout - {e}"
    except NoSuchElementException as e:
        driver.quit()
        return f"Error generating video: Element not found - {e}"
    except ElementNotInteractableException as e:
        driver.quit()
        return f"Error generating video: Element not interactable - {e}"
    except Exception as e:
        driver.quit()
        return f"Error generating video: {e}"
"""

def dyw(thing):
    # Originally asked for user input in console. Now always grant permission.
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_saved_chats', methods=['GET'])
def get_saved_chats():
    saved = load_saved_chats()
    return jsonify([{"name": name} for name in saved.keys()])

@app.route('/load_chat', methods=['GET'])
def load_chat():
    name = request.args.get('name', '')
    saved = load_saved_chats()
    if name in saved:
        return jsonify({"messages": saved[name]})
    else:
        return jsonify({"messages": []})

@app.route('/save_chat', methods=['POST'])
def save_chat_route():
    data = request.json
    chat_name = data.get("name")
    if not chat_name:
        return jsonify({"error": "No name provided"}), 400

    logs = load_chat_logs()
    saved = load_saved_chats()
    saved[chat_name] = logs
    save_saved_chats(saved)
    return jsonify({"status": "ok"})

@app.route('/chats', methods=['GET'])
def get_chats():
    logs = load_chat_logs()
    return jsonify(logs)

@app.route('/stop', methods=['POST'])
def stop_generation():
    global stop_generation_flag
    stop_generation_flag = True
    return jsonify({"status": "stopping"})

@app.route('/chat', methods=['POST'])
def handle_chat():
    global stop_generation_flag
    stop_generation_flag = False

    data = request.json
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Append system prompt if not present
    logs = load_chat_logs()
    if not any(m["role"] == "system" for m in logs):
        append_chat("system", system_prompt)

    # Append user message
    append_chat("user", question)

    # Prepare a generator to stream response
    def generate():
        try:
            messages = load_chat_logs()
            for token in continue_chat(question, messages):
                if stop_generation_flag:
                    break
                yield token
        except Exception as e:
            yield f"Error: {str(e)}"

    # Stream response as text/plain
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    # Run Flask in single-threaded mode to handle stop flag correctly
    app.run(host='0.0.0.0', port=5000, threaded=False)
