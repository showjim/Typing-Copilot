import sys
import threading
import asyncio
import logging
from pynput import keyboard
import pystray
from PIL import Image, ImageDraw
from backend import OllamaChatBot

# Set up logging
logging.basicConfig(filename='typing_copilot.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TrayIcon:
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.icon = None
        self.current_model = self.chatbot.OLLAMA_CONFIG["model"]

    def create_image(self):
        # Create a simple image for the system tray icon
        width = 64
        height = 64
        color1 = (0, 128, 255)
        color2 = (255, 255, 255)
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle([width // 2, 0, width, height], fill=color2)
        return image

    def set_model(self, model:str):
        self.chatbot.set_model(model)
        self.current_model = model
        self.icon.notify(f"Model set to {model}", "Model Changed")
        self.update_menu()

    def choose_llm(self, icon, item):
        models = self.chatbot.get_models()
        if not models:
            icon.notify("No Ollama models found", "Error")
            return
        self.update_menu(models)

    def create_menu(self, models=None):
        if models is None:
            models = []
        
        model_menu = pystray.Menu(*[
            pystray.MenuItem(
                f"{'✓ ' if model == self.current_model else ''}  {model}",
                lambda _, m=model: self.set_model(m)
            ) for model in models
        ])

        return pystray.Menu(
            pystray.MenuItem("Choose LLM", pystray.Menu(
                pystray.MenuItem("Refresh Models", self.choose_llm),
                pystray.Menu.SEPARATOR,
                *model_menu
            )),
            pystray.MenuItem("Exit", self.exit_app)
        )

    def update_menu(self, models=None):
        if self.icon:
            self.icon.menu = self.create_menu(models)

    def exit_app(self, icon, item):
        icon.stop()
        sys.exit(0)

    def run(self):
        image = self.create_image()
        menu = self.create_menu()
        self.icon = pystray.Icon("typing-copilot", image, "Typing Copilot", menu)
        self.icon.run()

def on_f9(chatbot):
    try:
        # Handle F9 key press: fix current line
        asyncio.run(chatbot.afix_current_line(usecase="fix"))
        logging.info("F9 hotkey processed")
    except Exception as e:
        logging.error(f"Error processing F9 hotkey: {str(e)}")

def on_f10(chatbot):
    try:
        # Handle F10 key press: process current line as instruction
        asyncio.run(chatbot.afix_current_line(usecase="instruct"))
        logging.info("F10 hotkey processed")
    except Exception as e:
        logging.error(f"Error processing F10 hotkey: {str(e)}")

def on_f11(chatbot):
    try:
        # Handle F11 key press: process selected text as instruction
        asyncio.run(chatbot.afix_selection(usecase="instruct"))
        logging.info("F11 hotkey processed")
    except Exception as e:
        logging.error(f"Error processing F11 hotkey: {str(e)}")

def on_press(key, chatbot):
    # Handle key press events
    if key == keyboard.Key.f9:
        on_f9(chatbot)
    elif key == keyboard.Key.f10:
        on_f10(chatbot)
    elif key == keyboard.Key.f11:
        on_f11(chatbot)

def run_keyboard_listener(chatbot):
    try:
        # Start the keyboard listener
        with keyboard.Listener(on_press=lambda key: on_press(key, chatbot)) as listener:
            logging.info("Keyboard listener started")
            listener.join()
    except Exception as e:
        logging.error(f"Error in keyboard listener: {str(e)}")

def main():
    try:
        # Initialize the OllamaChatBot
        chatbot = OllamaChatBot()
        logging.info("OllamaChatBot instance created successfully")

        # Create and run the tray icon
        tray_icon = TrayIcon(chatbot)
        tray_thread = threading.Thread(target=tray_icon.run)
        tray_thread.start()

        # Run the keyboard listener
        run_keyboard_listener(chatbot)

    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    logging.info("Typing Copilot started")
    main()