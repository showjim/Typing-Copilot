import time
from string import Template
import asyncio
from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyperclip
from datetime import date

import ollama, httpx

controller = Controller()


class OllamaChatBot():
    def __init__(self):
        super().__init__()
        self.OLLAMA_BASE = "http://localhost:11434"
        self.OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
        self.OLLAMA_CONFIG = {
            "model": "qwen2:0.5b",
            "keep_alive": "5m",
            "stream": True,
        }
        self.client = ollama.Client(host=self.OLLAMA_BASE)

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
        prompt = self.FIX_PROMPT_TEMPLATE.substitute(text=text)
        if 0:
            response = httpx.post(
                self.OLLAMA_ENDPOINT,
                json={"prompt": prompt, **self.OLLAMA_CONFIG},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
        else:
            response = self.client.generate(prompt=prompt, **self.OLLAMA_CONFIG)
        return response['response']

    def instr_text(self, text):
        cur_date = date.today()
        prompt = self.INSTR_PROMPT_TEMPLATE.substitute(date=cur_date, text=text)
        response = self.client.generate(prompt=prompt, **self.OLLAMA_CONFIG)
        return response['response']

    async def afix_text(self, text):
        self.aclient = ollama.AsyncClient(host=self.OLLAMA_BASE)
        prompt = self.FIX_PROMPT_TEMPLATE.substitute(text=text)
        async for part in await self.aclient.generate(prompt=prompt, **self.OLLAMA_CONFIG):
            fixed_text = part['response']
            # 1. Paste the fixed string to the clipboard
            pyperclip.copy(fixed_text)
            time.sleep(0.01)

            # 2. Paste the clipboard and replace the selected text
            with controller.pressed(Key.ctrl):  # .cmd
                controller.tap("v")

    async def ainstr_text(self, text):
        self.aclient = ollama.AsyncClient(host=self.OLLAMA_BASE)
        cur_date = date.today()
        prompt = self.INSTR_PROMPT_TEMPLATE.substitute(date=cur_date, text=text)
        async for part in await self.aclient.generate(prompt=prompt, **self.OLLAMA_CONFIG):
            fixed_text = part['response']
            # 1. Paste the fixed string to the clipboard
            pyperclip.copy(fixed_text)
            time.sleep(0.01)

            # 2. Paste the clipboard and replace the selected text
            with controller.pressed(Key.ctrl):  # .cmd
                controller.tap("v")

    def fix_current_line(self, usecase="fix"):
        # macOS short cut to select current line: Cmd+Shift+Left
        # win short cut to select current line: shift+home
        with controller.pressed(Key.shift):
            controller.tap(Key.home)
        time.sleep(0.1)
        if usecase == "fix":
            self.fix_selection(usecase="fix")
        elif usecase == "instruct":
            self.fix_selection(usecase="instruct")

    def fix_selection(self, usecase="fix"):
        # 1. Copy selection to clipboard
        with controller.pressed(Key.ctrl):  # cmd
            controller.tap("c")

        # 2. Get the clipboard string
        time.sleep(0.1)
        text = pyperclip.paste()

        # 3. Fix string
        if not text:
            return
        if usecase == "fix":
            fixed_text = self.fix_text(text)
        elif usecase == "instruct":
            fixed_text = self.instr_text(text)
        if not fixed_text:
            return

        # 4. Paste the fixed string to the clipboard
        pyperclip.copy(fixed_text)
        time.sleep(0.01)

        # 5. Paste the clipboard and replace the selected text
        with controller.pressed(Key.ctrl):  # .cmd
            controller.tap("v")

    async def afix_current_line(self, usecase="fix"):
        # macOS short cut to select current line: Cmd+Shift+Left
        # win short cut to select current line: shift+home
        with controller.pressed(Key.shift):
            controller.tap(Key.home)
        time.sleep(0.1)
        if usecase == "fix":
            await self.afix_selection(usecase="fix")
        elif usecase == "instruct":
            await self.afix_selection(usecase="instruct")

    async def afix_selection(self, usecase="fix"):
        # 1. Copy selection to clipboard
        with controller.pressed(Key.ctrl):  # cmd
            controller.tap("c")

        # 2. Get the clipboard string
        time.sleep(0.1)
        text = pyperclip.paste()

        # 3. Fix string
        if not text:
            return
        if usecase == "fix":
           await self.afix_text(text)
        elif usecase == "instruct":
            await self.ainstr_text(text)


chatbot = OllamaChatBot()


def on_f9():
    asyncio.run(chatbot.afix_current_line(usecase="fix"))


def on_f10():
    asyncio.run(chatbot.afix_selection(usecase="instruct"))

def on_f11():
    asyncio.run(chatbot.afix_selection(usecase="instruct"))


def main():
    # on Win, '<120>'==F9, '<121>'==F10
    # on Mac, '<101>'==F9, '<109>'==F10
    with keyboard.GlobalHotKeys({'<120>': on_f9, '<121>': on_f10, '<122>': on_f11}) as h:
        h.join()


if __name__ == "__main__":
    main()
