# Typing Copilot

Typing Copilot is a tool that enhances your typing experience by providing real-time text corrections and processing using Ollama's language models.

## Features

- System tray icon for easy access and control
- Real-time text correction (fix typos, casing, and punctuation)
- Process text as instructions using AI
- Support for multiple Ollama language models
- Keyboard shortcuts for quick actions

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.9 or higher
- Ollama installed on your system (https://ollama.ai/)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/showjim/Typing-Copilot.git
   cd typing-copilot
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Make sure Ollama is running on your system.

2. Run the Typing Copilot:
   ```
   python typing-copilot.py
   ```

3. A system tray icon will appear. Right-click on it to:
   - Choose or refresh available Ollama models
   - Exit the application

4. Use the following keyboard shortcuts:
   - F9: Fix the current line (correct typos, casing, and punctuation)
   - F10: Process the current line as an instruction
   - F11: Process the selected text as an instruction

## Changing Ollama Models

1. Right-click on the system tray icon
2. Select "Choose LLM"
3. Click "Refresh Models" to update the list of available models
4. Select the desired model from the list

## Troubleshooting

If you encounter any issues:

1. Check that Ollama is running and accessible
2. Ensure you have the latest version of the required packages
3. Check the `typing_copilot.log` file for error messages

## Acknowledgments

- Ollama for providing the language models
- The Python community for the excellent libraries used in this project
- Thanks to patrickloeber, allI have done are based on this repo [patrickloeber/ai-typing-assistant](https://github.com/patrickloeber/ai-typing-assistant)
