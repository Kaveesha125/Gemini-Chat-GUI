import tkinter as tk
from tkinter import scrolledtext, ttk
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

AVAILABLE_MODELS = [
    'models/gemini-1.5-flash-latest',
    'models/gemini-2.5-flash',
    'models/gemini-2.5-pro',
    'models/gemini-2.5-flash-preview-05-20',
]

COLORS = {
    'primary': '#2C3E50',
    'secondary': '#3498DB',
    'accent': '#E74C3C',
    'success': '#27AE60',
    'background': '#ECF0F1',
    'surface': '#FFFFFF',
    'text_primary': '#2C3E50',
    'text_secondary': '#7F8C8D',
    'button_hover': '#2980B9',
    'gradient_start': '#667eea',
    'gradient_end': '#764ba2'
}


def generate_response():
    prompt = prompt_entry.get("1.0", tk.END).strip()
    selected_model = model_combobox.get()

    if not prompt:
        update_gui_with_response("Please enter a prompt.")
        return
    if not selected_model:
        update_gui_with_response("Please select a model.")
        return

    generate_button.config(state=tk.DISABLED, text="Generating...", bg=COLORS['text_secondary'])
    response_text.delete('1.0', tk.END)
    response_text.insert(tk.END, f"🤖 Generating with {selected_model}...\n\nPlease wait...")

    threading.Thread(target=call_gemini_api, args=(prompt, selected_model)).start()

def call_gemini_api(prompt, model_name):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        root.after(0, update_gui_with_response, response.text)
    except Exception as e:
        root.after(0, update_gui_with_response, f"❌ An error occurred: {e}")

def update_gui_with_response(text):
    response_text.delete('1.0', tk.END)
    response_text.insert(tk.END, text)
    generate_button.config(state=tk.NORMAL, text="✨ Generate", bg=COLORS['secondary'])

def on_button_hover(event):
    event.widget.config(bg=COLORS['button_hover'])

def on_button_leave(event):
    """Handle button leave effect."""
    if event.widget['state'] == 'normal':
        event.widget.config(bg=COLORS['secondary'])

def clear_response():
    """Clear the response text area."""
    response_text.delete('1.0', tk.END)

root = tk.Tk()
root.title("🤖 Gemini AI Studio")
root.geometry("900x700")
root.configure(bg=COLORS['background'])

try:
    title_font = ('Segoe UI', 18, 'bold')
    heading_font = ('Segoe UI', 12, 'bold')
    body_font = ('Segoe UI', 10)
    button_font = ('Segoe UI', 10, 'bold')
except:
    title_font = ('Arial', 18, 'bold')
    heading_font = ('Arial', 12, 'bold')
    body_font = ('Arial', 10)
    button_font = ('Arial', 10, 'bold')

main_frame = tk.Frame(root, bg=COLORS['background'], padx=20, pady=20)
main_frame.pack(fill='both', expand=True)

title_label = tk.Label(
    main_frame,
    text="🤖 Gemini AI Studio",
    font=title_font,
    bg=COLORS['background'],
    fg=COLORS['primary']
)
title_label.pack(pady=(0, 20))

content_frame = tk.Frame(main_frame, bg=COLORS['surface'], relief='raised', bd=1)
content_frame.pack(fill='both', expand=True, padx=10, pady=10)

inner_frame = tk.Frame(content_frame, bg=COLORS['surface'], padx=25, pady=25)
inner_frame.pack(fill='both', expand=True)

model_section = tk.Frame(inner_frame, bg=COLORS['surface'])
model_section.pack(fill='x', pady=(0, 20))

model_label = tk.Label(
    model_section,
    text="🎯 Choose AI Model:",
    font=heading_font,
    bg=COLORS['surface'],
    fg=COLORS['text_primary']
)
model_label.pack(anchor='w', pady=(0, 8))

style = ttk.Style()
style.theme_use('clam')
style.configure('Custom.TCombobox',
                fieldbackground=COLORS['surface'],
                background=COLORS['secondary'],
                foreground=COLORS['text_primary'],
                selectbackground=COLORS['secondary'])

model_combobox = ttk.Combobox(
    model_section,
    values=AVAILABLE_MODELS,
    state="readonly",
    font=body_font,
    style='Custom.TCombobox'
)
model_combobox.pack(fill='x', ipady=8)

if AVAILABLE_MODELS:
    model_combobox.set('models/gemini-1.5-flash-latest')

prompt_section = tk.Frame(inner_frame, bg=COLORS['surface'])
prompt_section.pack(fill='x', pady=(0, 20))

prompt_label = tk.Label(
    prompt_section,
    text="💭 Enter Your Prompt:",
    font=heading_font,
    bg=COLORS['surface'],
    fg=COLORS['text_primary']
)
prompt_label.pack(anchor='w', pady=(0, 8))

prompt_entry = tk.Text(
    prompt_section,
    width=80,
    height=4,
    font=body_font,
    bg=COLORS['surface'],
    fg=COLORS['text_primary'],
    relief='solid',
    bd=1,
    wrap=tk.WORD,
    padx=10,
    pady=10
)
prompt_entry.pack(fill='x')

button_section = tk.Frame(inner_frame, bg=COLORS['surface'])
button_section.pack(fill='x', pady=(0, 20))

generate_button = tk.Button(
    button_section,
    text="✨ Generate",
    command=generate_response,
    font=button_font,
    bg=COLORS['secondary'],
    fg='white',
    relief='flat',
    padx=30,
    pady=12,
    cursor='hand2'
)
generate_button.pack(side='left', padx=(0, 10))

clear_button = tk.Button(
    button_section,
    text="🗑️ Clear",
    command=clear_response,
    font=button_font,
    bg=COLORS['text_secondary'],
    fg='white',
    relief='flat',
    padx=20,
    pady=12,
    cursor='hand2'
)
clear_button.pack(side='left')

generate_button.bind("<Enter>", on_button_hover)
generate_button.bind("<Leave>", on_button_leave)
clear_button.bind("<Enter>", lambda e: e.widget.config(bg='#95A5A6'))
clear_button.bind("<Leave>", lambda e: e.widget.config(bg=COLORS['text_secondary']))

response_section = tk.Frame(inner_frame, bg=COLORS['surface'])
response_section.pack(fill='both', expand=True)

response_label = tk.Label(
    response_section,
    text="🎯 AI Response:",
    font=heading_font,
    bg=COLORS['surface'],
    fg=COLORS['text_primary']
)
response_label.pack(anchor='w', pady=(0, 8))

response_text = scrolledtext.ScrolledText(
    response_section,
    wrap=tk.WORD,
    width=80,
    height=15,
    font=body_font,
    bg=COLORS['surface'],
    fg=COLORS['text_primary'],
    relief='solid',
    bd=1,
    padx=15,
    pady=15,
    selectbackground=COLORS['secondary'],
    selectforeground='white'
)
response_text.pack(fill='both', expand=True)

status_frame = tk.Frame(main_frame, bg=COLORS['background'])
status_frame.pack(fill='x', pady=(10, 0))

status_label = tk.Label(
    status_frame,
    text="Ready to generate amazing content! 🚀",
    font=('Segoe UI', 9),
    bg=COLORS['background'],
    fg=COLORS['text_secondary']
)
status_label.pack(anchor='w')

if not API_KEY:
    response_text.insert(tk.END, "❌ Error: GEMINI_API_KEY not found in environment variables.\n\nPlease check your .env file and ensure the API key is properly configured.")
    generate_button.config(state=tk.DISABLED, bg=COLORS['text_secondary'])
    model_combobox.config(state=tk.DISABLED)
    status_label.config(text="⚠️ API Key not configured", fg=COLORS['accent'])
else:
    status_label.config(text="✅ Ready to generate amazing content! 🚀", fg=COLORS['success'])

prompt_entry.insert("1.0", "Ask me anything! I can help with writing, coding, analysis, creative tasks, and much more...")
prompt_entry.bind("<FocusIn>", lambda e: prompt_entry.delete("1.0", tk.END) if prompt_entry.get("1.0", tk.END).strip().startswith("Ask me anything!") else None)

root.mainloop()