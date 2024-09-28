import time
from string import Template

import httpx
from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyperclip
from datetime import date

time.sleep(0.1)

controller = Controller()

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "qwen2:0.5b",
    "keep_alive": "5m",
    "stream": False,
}

FIX_PROMPT_TEMPLATE = Template(
    """Fix all typos and casing and punctuation in this text, but preserve all new line characters:

$text

Return only the corrected text, don't include a preamble.
"""
)

INSTR_PROMPT_TEMPLATE = Template(
    """You are AI assistant, a large language model trained by human, based on the AI architecture.
Knowledge cutoff: 2023-04
Current date: $date
The request :

$text
"""
)


def fix_text(text):
    prompt = FIX_PROMPT_TEMPLATE.substitute(text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    return response.json()["response"].strip()

def instr_text(text):
    cur_date = date.today()
    prompt = INSTR_PROMPT_TEMPLATE.substitute(date=cur_date, text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    return response.json()["response"].strip()

def fix_current_line(usecase="fix"):
    # macOS short cut to select current line: Cmd+Shift+Left
    # win short cut to select current line: shift+home
    with controller.pressed(Key.shift):
        controller.tap(Key.home)
    time.sleep(0.1)
    if usecase == "fix":
        fix_selection(usecase="fix")
    elif usecase == "instruct":
        fix_selection(usecase="instruct")


def fix_selection(usecase="fix"):
    # 1. Copy selection to clipboard
    with controller.pressed(Key.ctrl): #cmd
        controller.tap("c")

    # 2. Get the clipboard string
    time.sleep(0.1)
    text = pyperclip.paste()

    # 3. Fix string
    if not text:
        return
    if usecase == "fix":
        fixed_text = fix_text(text)
    elif usecase == "instruct":
        fixed_text = instr_text(text)
    if not fixed_text:
        return

    # 4. Paste the fixed string to the clipboard
    pyperclip.copy(fixed_text)
    time.sleep(0.1)

    # 5. Paste the clipboard and replace the selected text
    with controller.pressed(Key.ctrl): #.cmd
        controller.tap("v")


def on_f9():
    fix_current_line(usecase="fix")


def on_f10():
    fix_current_line(usecase="instruct")

def on_f11():
    fix_selection(usecase="instruct")


# on Win, '<120>'==F9, '<121>'==F10
with keyboard.GlobalHotKeys({'<120>': on_f9, '<121>': on_f10, '<122>': on_f11}) as h:
    h.join()