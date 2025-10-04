import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterweb import HtmlFrame
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading
import markdown
import pyperclip

try:
    from system_prompt import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = "You are a helpful assistant."


# === Load environment variables ===
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# === Available Gemini models ===
AVAILABLE_MODELS = [
    'models/gemini-2.5-flash',
    'models/gemini-2.5-pro',
    'models/gemini-2.0-flash-001',
    'models/gemini-flash-latest',
    'models/gemini-pro-latest',
    'models/gemini-2.5-flash-lite'
]
# === Colors ===
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
}

# Global variable to store last Markdown
last_ai_response = ""

# === Generate AI Response ===
def generate_response():
    global last_ai_response
    prompt = prompt_entry.get("1.0", tk.END).strip()
    selected_model = model_combobox.get()

    if not prompt:
        update_gui_with_response("Please enter a prompt.")
        return
    if not selected_model:
        update_gui_with_response("Please select a model.")
        return

    last_ai_response = ""
    generate_button.config(state=tk.DISABLED, text="Generating...", bg=COLORS['text_secondary'])
    response_frame.load_html("<p>🤖 Generating response... Please wait...</p>")

    threading.Thread(target=call_gemini_api, args=(prompt, selected_model)).start()


def call_gemini_api(prompt, model_name):
    try:
        # Load system prompt dynamically
        model = genai.GenerativeModel(
            model_name,
            system_instruction=SYSTEM_PROMPT  # comes from system_prompt.py
        )

        response = model.generate_content(prompt)

        root.after(0, update_gui_with_response, response.text)

    except Exception as e:
        root.after(0, update_gui_with_response, f"❌ An error occurred: {e}")


# === Update GUI with formatted Markdown ===
def update_gui_with_response(md_text):
    global last_ai_response
    last_ai_response = md_text

    # Convert Markdown to HTML
    html_body = markdown.markdown(md_text, extensions=["fenced_code", "tables"])

    # Load GitHub Markdown CSS
    try:
        with open("github-markdown.css", "r", encoding="utf-8") as css_file:
            github_css = css_file.read()
    except FileNotFoundError:
        github_css = ""
        print("github-markdown.css not found. Using default styling.")

    # Final HTML template
    final_html = f"""
    <html>
    <head>
        <style>
            body {{
                background-color: {COLORS['primary']};
                margin: 0;
                padding: 20px;
                color: {COLORS['background']};
            }}
            .markdown-body {{
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 20px;
                background: {COLORS['primary']};
                border: 1px solid {COLORS['text_secondary']};
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                color: {COLORS['background']};
            }}
            {github_css}

            /* Dark theme overrides */
            .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 {{
                color: {COLORS['secondary']};
                border-bottom-color: {COLORS['text_secondary']};
            }}
            .markdown-body a {{
                color: #58A6FF;
            }}
            .markdown-body code, .markdown-body pre {{
                background-color: #161B22 !important;
                color: #C9D1D9 !important;
            }}
            .markdown-body blockquote {{
                color: {COLORS['text_secondary']};
                border-left-color: {COLORS['text_secondary']};
            }}
            .markdown-body table th, .markdown-body table td {{
                border-color: {COLORS['text_secondary']};
            }}
            .markdown-body table tr {{
                 background-color: {COLORS['primary']};
            }}
             .markdown-body table tr:nth-child(2n) {{
                background-color: #21262d;
            }}
        </style>
    </head>
    <body>
        <article class="markdown-body">
            {html_body}
        </article>
    </body>
    </html>
    """

    # Load HTML into the frame
    response_frame.load_html(final_html)

    generate_button.config(state=tk.NORMAL, text="✨ Generate", bg=COLORS['secondary'])


# === Copy Markdown to Clipboard ===
def copy_markdown():
    if not last_ai_response.strip():
        messagebox.showwarning("Copy Failed", "No AI response to copy!")
        return
    pyperclip.copy(last_ai_response)
    messagebox.showinfo("Copied", "Markdown copied to clipboard!")

# === Download Markdown file ===
def download_markdown():
    if not last_ai_response.strip():
        messagebox.showwarning("Download Failed", "No AI response to download!")
        return

    filepath = filedialog.asksaveasfilename(defaultextension=".md",
                                            filetypes=[("Markdown Files", "*.md")],
                                            initialfile="response.md")
    if filepath:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(last_ai_response)
            messagebox.showinfo("Downloaded", f"Markdown saved to {filepath}!")
        except Exception as e:
            messagebox.showerror("Download Failed", f"An error occurred: {e}")

# === Clear input and output ===
def clear_response():
    global last_ai_response
    last_ai_response = ""
    prompt_entry.delete('1.0', tk.END)
    response_frame.load_html("<p>No response yet. Generate something cool! 🚀</p>")

# === Hover effects ===
def on_button_hover(event):
    event.widget.config(bg=COLORS['button_hover'])

def on_button_leave(event):
    if event.widget['state'] == 'normal':
        event.widget.config(bg=COLORS['secondary'])

# === Root window ===
root = tk.Tk()
root.title("🤖 Gemini AI Studio")
root.geometry("950x750")
root.configure(bg=COLORS['background'])

# === Fonts ===
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

# === Layout ===
main_frame = tk.Frame(root, bg=COLORS['background'], padx=20, pady=20)
main_frame.pack(fill='both', expand=True)

title_label = tk.Label(
    main_frame, text="🤖 Gemini AI Studio",
    font=title_font, bg=COLORS['background'], fg=COLORS['primary']
)
title_label.pack(pady=(0, 20))

content_frame = tk.Frame(main_frame, bg=COLORS['surface'], relief='raised', bd=1)
content_frame.pack(fill='both', expand=True, padx=10, pady=10)

inner_frame = tk.Frame(content_frame, bg=COLORS['surface'], padx=25, pady=25)
inner_frame.pack(fill='both', expand=True)

# === Model selection ===
model_section = tk.Frame(inner_frame, bg=COLORS['surface'])
model_section.pack(fill='x', pady=(0, 20))

model_label = tk.Label(
    model_section, text="🎯 Choose AI Model:",
    font=heading_font, bg=COLORS['surface'], fg=COLORS['text_primary']
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
    model_section, values=AVAILABLE_MODELS,
    state="readonly", font=body_font, style='Custom.TCombobox'
)
model_combobox.pack(fill='x', ipady=8)

if AVAILABLE_MODELS:
    model_combobox.set('models/gemini-2.5-flash-lite')

# === Prompt input ===
prompt_section = tk.Frame(inner_frame, bg=COLORS['surface'])
prompt_section.pack(fill='x', pady=(0, 20))

prompt_label = tk.Label(
    prompt_section, text="💭 Enter Your Prompt:",
    font=heading_font, bg=COLORS['surface'], fg=COLORS['text_primary']
)
prompt_label.pack(anchor='w', pady=(0, 8))

prompt_entry = tk.Text(
    prompt_section, width=80, height=4, font=body_font,
    bg=COLORS['surface'], fg=COLORS['text_primary'],
    relief='solid', bd=1, wrap=tk.WORD, padx=10, pady=10
)
prompt_entry.pack(fill='x')

# === Action buttons ===
button_section = tk.Frame(inner_frame, bg=COLORS['surface'])
button_section.pack(fill='x', pady=(0, 20))

generate_button = tk.Button(
    button_section, text="✨ Generate", command=generate_response,
    font=button_font, bg=COLORS['secondary'], fg='white',
    relief='flat', padx=30, pady=12, cursor='hand2'
)
generate_button.pack(side='left', padx=(0, 10))

clear_button = tk.Button(
    button_section, text="🗑️ Clear", command=clear_response,
    font=button_font, bg=COLORS['text_secondary'], fg='white',
    relief='flat', padx=20, pady=12, cursor='hand2'
)
clear_button.pack(side='left')

generate_button.bind("<Enter>", on_button_hover)
generate_button.bind("<Leave>", on_button_leave)
clear_button.bind("<Enter>", lambda e: e.widget.config(bg='#95A5A6'))
clear_button.bind("<Leave>", lambda e: e.widget.config(bg=COLORS['text_secondary']))

# === Response section ===
response_section = tk.Frame(inner_frame, bg=COLORS['surface'])
response_section.pack(fill='both', expand=True)

response_label_frame = tk.Frame(response_section, bg=COLORS['surface'])
response_label_frame.pack(fill='x', pady=(0, 8))

response_label = tk.Label(
    response_label_frame, text="🎯 AI Response:",
    font=heading_font, bg=COLORS['surface'], fg=COLORS['text_primary']
)
response_label.pack(side='left')

download_button = tk.Button(
    response_label_frame, text="⬇️ Download .md",
    command=download_markdown, font=('Segoe UI', 9),
    bg=COLORS['success'], fg='white',
    relief='flat', padx=10, pady=5, cursor='hand2'
)
download_button.pack(side='right', padx=(5, 0))

copy_button = tk.Button(
    response_label_frame, text="📋 Copy Markdown",
    command=copy_markdown, font=('Segoe UI', 9),
    bg=COLORS['secondary'], fg='white',
    relief='flat', padx=10, pady=5, cursor='hand2'
)
copy_button.pack(side='right')


# Markdown rendering area
response_frame = HtmlFrame(response_section)
response_frame.pack(fill='both', expand=True)

# === Status Bar ===
status_frame = tk.Frame(main_frame, bg=COLORS['background'])
status_frame.pack(fill='x', pady=(10, 0))

status_label = tk.Label(
    status_frame, text="Ready to generate amazing content! 🚀",
    font=('Segoe UI', 9), bg=COLORS['background'], fg=COLORS['text_secondary']
)
status_label.pack(anchor='w')

# === API Key check ===
if not API_KEY:
    response_frame.load_html("<p>❌ Error: GEMINI_API_KEY not found in environment variables.</p>")
    generate_button.config(state=tk.DISABLED, bg=COLORS['text_secondary'])
    model_combobox.config(state=tk.DISABLED)
    status_label.config(text="⚠️ API Key not configured", fg=COLORS['accent'])
else:
    status_label.config(text="✅ Ready to generate amazing content! 🚀", fg=COLORS['success'])

# Default prompt placeholder
prompt_entry.insert("1.0", "Ask me anything! I can help with writing, coding, analysis, creative tasks, and much more...")
prompt_entry.bind("<FocusIn>", lambda e: prompt_entry.delete("1.0", tk.END) if prompt_entry.get("1.0", tk.END).strip().startswith("Ask me anything!") else None)

root.mainloop()