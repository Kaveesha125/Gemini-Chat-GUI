import tkinter as tk
from tkinter import scrolledtext, ttk
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading

# --- API Configuration ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# A list of models the user can choose from.
# You can customize this list based on the models you have access to.
AVAILABLE_MODELS = [
    'models/gemini-1.5-flash-latest',
    'models/gemini-1.5-pro-latest',
    'models/gemini-2.5-flash',
    'models/gemini-2.5-pro',
    'models/gemini-2.5-flash-preview-05-20',
    'models/gemini-2.5-pro-preview-05-06',
]

# --- GUI Application ---

def generate_response():
    """Gets prompt and selected model, calls API, and updates GUI."""
    prompt = prompt_entry.get()
    selected_model = model_combobox.get()

    if not prompt:
        update_gui_with_response("Please enter a prompt.")
        return
    if not selected_model:
        update_gui_with_response("Please select a model.")
        return

    # Disable button and show loading message
    generate_button.config(state=tk.DISABLED)
    response_text.delete('1.0', tk.END)
    response_text.insert(tk.END, f"Generating with {selected_model}...")

    # Run API call in a separate thread
    threading.Thread(target=call_gemini_api, args=(prompt, selected_model)).start()


def call_gemini_api(prompt, model_name):
    """Worker function to call the API with the selected model."""
    try:
        # Initialize the model dynamically based on user selection
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        # Schedule GUI update to run in the main thread
        root.after(0, update_gui_with_response, response.text)
    except Exception as e:
        root.after(0, update_gui_with_response, f"An error occurred: {e}")


def update_gui_with_response(text):
    """Updates the text box and re-enables the button."""
    response_text.delete('1.0', tk.END)
    response_text.insert(tk.END, text)
    generate_button.config(state=tk.NORMAL)


# --- Main Window Setup ---
root = tk.Tk()
root.title("Gemini Model Selector GUI")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10, fill="both", expand=True)

# --- Model Selection Dropdown ---
model_label = tk.Label(frame, text="Choose a model:")
model_label.pack(fill='x')

model_combobox = ttk.Combobox(frame, values=AVAILABLE_MODELS, state="readonly")
model_combobox.pack(fill='x', pady=(0, 10))
# Set the default model
if AVAILABLE_MODELS:
    model_combobox.set('models/gemini-1.5-flash-latest')

# --- Prompt Entry ---
prompt_label = tk.Label(frame, text="Enter your prompt:")
prompt_label.pack(fill='x')

prompt_entry = tk.Entry(frame, width=80)
prompt_entry.pack(fill='x', pady=5)

# --- Generate Button ---
generate_button = tk.Button(frame, text="Generate", command=generate_response)
generate_button.pack(pady=5)

# --- Response Area ---
response_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=20)
response_text.pack(fill='both', expand=True, pady=5)

# Handle case where API key is not found
if not API_KEY:
    response_text.insert(tk.END, "Error: GEMINI_API_KEY not found.")
    generate_button.config(state=tk.DISABLED)
    model_combobox.config(state=tk.DISABLED)

root.mainloop()