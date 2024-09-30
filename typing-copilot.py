import asyncio
import logging
import platform
import sys
import time
from datetime import date
from string import Template

import ollama
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Controller

# Set up logging
logging.basicConfig(filename='typing_copilot.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class OllamaChatBot():
    def __init__(self):
        super().__init__()
        self.controller = Controller()
        # Ollama API configuration
        self.OLLAMA_BASE = "http://localhost:11434"
        self.OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
        self.OLLAMA_CONFIG = {
            "model": "qwen2.5:1.5b", #llama3.2:1b qwen2.5:0.5b
            "keep_alive": "5m",
            "stream": True,
        }
        try:
            # Initialize Ollama client
            self.client = ollama.Client(host=self.OLLAMA_BASE)
            logging.info("Ollama client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Ollama client: {str(e)}")
            raise

        # Detect operating system
        self.is_mac = platform.system() == "Darwin"
        logging.info(f"Operating system detected: {'macOS' if self.is_mac else 'Windows'}")

        # Define prompt templates for text fixing and instruction processing
        self.FIX_PROMPT_TEMPLATE = Template(
            """Fix all typos and casing and punctuation in this text, but preserve all new line characters:
        
        $text
        
        Return only the corrected text, don't include a preamble.
        """
        )

        self.INSTR_PROMPT_TEMPLATE = Template(
            """You are AI assistant, a large language model trained by human, based on the AI architecture.
        Knowledge cutoff: 2023-04
        Current date: $date
        The request :
        
        $text
        """
        )

    def fix_text(self, text):
        initialWait = True
        # Generate a prompt to fix the text
        prompt = self.FIX_PROMPT_TEMPLATE.substitute(text=text)
        try:
            for part in self.client.generate(prompt=prompt, **self.OLLAMA_CONFIG):
                fixed_text = part['response']
                if initialWait:
                    time.sleep(0.5)
                    initialWait = False
                pyperclip.copy(fixed_text)
                time.sleep(0.1)
                self.paste_text()
                time.sleep(0.01)
            logging.info("Text fixed successfully")
        except Exception as e:
            logging.error(f"Error in fix_text: {str(e)}")
            return None

    def instr_text(self, text):
        # Generate a prompt for instruction processing
        cur_date = date.today()
        prompt = self.INSTR_PROMPT_TEMPLATE.substitute(date=cur_date, text=text)
        try:
            response = self.client.generate(prompt=prompt, **self.OLLAMA_CONFIG)
            logging.info("Instruction processed successfully")
            return response['response']
        except Exception as e:
            logging.error(f"Error in instr_text: {str(e)}")
            return None

    async def afix_text(self, text):
        try:
            initialWait = True
            # Use asynchronous client for text fixing
            self.aclient = ollama.AsyncClient(host=self.OLLAMA_BASE)
            prompt = self.FIX_PROMPT_TEMPLATE.substitute(text=text)
            async for part in await self.aclient.generate(prompt=prompt, **self.OLLAMA_CONFIG):
                fixed_text = part['response']
                pyperclip.copy(fixed_text)
                time.sleep(0.1)
                self.paste_text()
                time.sleep(0.05)
            logging.info("Async text fixing completed")
        except Exception as e:
            logging.error(f"Error in afix_text: {str(e)}")

    async def ainstr_text(self, text):
        try:
            # Use asynchronous client for instruction processing
            self.aclient = ollama.AsyncClient(host=self.OLLAMA_BASE)
            cur_date = date.today()
            prompt = self.INSTR_PROMPT_TEMPLATE.substitute(date=cur_date, text=text)
            async for part in await self.aclient.generate(prompt=prompt, **self.OLLAMA_CONFIG):
                fixed_text = part['response']
                pyperclip.copy(fixed_text)
                time.sleep(0.1)
                self.paste_text()
            logging.info("Async instruction processing completed")
        except Exception as e:
            logging.error(f"Error in ainstr_text: {str(e)}")

    def select_current_line(self):
        try:
            # Select the current line based on the operating system
            if self.is_mac:
                with self.controller.pressed(Key.shift, Key.cmd):
                    self.controller.tap(Key.left)
            else:
                with self.controller.pressed(Key.shift):
                    self.controller.tap(Key.home)
            time.sleep(0.1)
            logging.info("Current line selected")
        except Exception as e:
            logging.error(f"Error in select_current_line: {str(e)}")

    def copy_text(self):
        try:
            # Copy selected text to clipboard
            with self.controller.pressed(Key.cmd if self.is_mac else Key.ctrl):
                self.controller.tap("c")
            time.sleep(0.1)
            logging.info("Text copied: " + pyperclip.paste())
        except Exception as e:
            logging.error(f"Error in copy_text: {str(e)}")

    def paste_text(self):
        try:
            # Paste text from clipboard
            with self.controller.pressed(Key.cmd if self.is_mac else Key.ctrl):
                self.controller.tap("v")
            logging.info("Text pasted: " + pyperclip.paste())
        except Exception as e:
            logging.error(f"Error in paste_text: {str(e)}")

    def fix_current_line(self, usecase="fix"):
        # Fix or process the current line based on the usecase
        self.select_current_line()
        if usecase == "fix":
            self.fix_selection(usecase="fix")
        elif usecase == "instruct":
            self.fix_selection(usecase="instruct")

    def fix_selection(self, usecase="fix"):
        # Fix or process the selected text
        self.copy_text()
        ## Get the clipboard string
        text = pyperclip.paste()
        if not text:
            logging.warning("No text selected")
            return
        if usecase == "fix":
            self.fix_text(text)
        elif usecase == "instruct":
            fixed_text = self.instr_text(text)

    async def afix_current_line(self, usecase="fix"):
        # Asynchronously fix or process the current line
        self.select_current_line()
        if usecase == "fix":
            await self.afix_selection(usecase="fix")
        elif usecase == "instruct":
            await self.afix_selection(usecase="instruct")

    async def afix_selection(self, usecase="fix"):
        # Asynchronously fix or process the selected text
        self.copy_text()
        text = pyperclip.paste()
        if not text:
            logging.warning("No text selected")
            return
        if usecase == "fix":
            await self.afix_text(text)
        elif usecase == "instruct":
            await self.ainstr_text(text)


try:
    # Initialize the OllamaChatBot
    chatbot = OllamaChatBot()
    logging.info("OllamaChatBot instance created successfully")
except Exception as e:
    logging.error(f"Failed to create OllamaChatBot instance: {str(e)}")
    sys.exit(1)


def on_f9():
    try:
        # Handle F9 key press: fix current line
        # chatbot.fix_current_line(usecase="fix")
        asyncio.run(chatbot.afix_current_line(usecase="fix"))
        logging.info("F9 hotkey processed")
    except Exception as e:
        logging.error(f"Error processing F9 hotkey: {str(e)}")


def on_f10():
    try:
        # Handle F10 key press: process current line as instruction
        asyncio.run(chatbot.afix_current_line(usecase="instruct"))
        logging.info("F10 hotkey processed")
    except Exception as e:
        logging.error(f"Error processing F10 hotkey: {str(e)}")


def on_f11():
    try:
        # Handle F11 key press: process selected text as instruction
        asyncio.run(chatbot.afix_selection(usecase="instruct"))
        logging.info("F11 hotkey processed")
    except Exception as e:
        logging.error(f"Error processing F11 hotkey: {str(e)}")


def on_press(key):
    # Handle key press events
    if key == keyboard.Key.f9:
        on_f9()
    elif key == keyboard.Key.f10:
        on_f10()
    elif key == keyboard.Key.f11:
        on_f11()


def main():
    try:
        # Start the keyboard listener
        with keyboard.Listener(on_press=on_press) as listener:
            logging.info("Keyboard listener started")
            listener.join()
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")


if __name__ == "__main__":
    logging.info("Script started")
    main()
