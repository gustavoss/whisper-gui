import gradio as gr
import requests
import tempfile
import re

LANGUAGES = [
    ("Afrikaans", "af"), ("Arabic", "ar"), ("Armenian", "hy"), ("Azerbaijani", "az"),
    ("Belarusian", "be"), ("Bosnian", "bs"), ("Bulgarian", "bg"), ("Catalan", "ca"),
    ("Chinese", "zh"), ("Croatian", "hr"), ("Czech", "cs"), ("Danish", "da"),
    ("Dutch", "nl"), ("English", "en"), ("Estonian", "et"), ("Finnish", "fi"),
    ("French", "fr"), ("Galician", "gl"), ("German", "de"), ("Greek", "el"),
    ("Hebrew", "he"), ("Hindi", "hi"), ("Hungarian", "hu"), ("Icelandic", "is"),
    ("Indonesian", "id"), ("Italian", "it"), ("Japanese", "ja"), ("Kannada", "kn"),
    ("Kazakh", "kk"), ("Korean", "ko"), ("Latvian", "lv"), ("Lithuanian", "lt"),
    ("Macedonian", "mk"), ("Malay", "ms"), ("Marathi", "mr"), ("Maori", "mi"),
    ("Nepali", "ne"), ("Norwegian", "no"), ("Persian", "fa"), ("Polish", "pl"),
    ("Portuguese", "pt"), ("Romanian", "ro"), ("Russian", "ru"), ("Serbian", "sr"),
    ("Slovak", "sk"), ("Slovenian", "sl"), ("Spanish", "es"), ("Swahili", "sw"),
    ("Swedish", "sv"), ("Tagalog", "tl"), ("Tamil", "ta"), ("Thai", "th"),
    ("Turkish", "tr"), ("Ukrainian", "uk"), ("Urdu", "ur"), ("Vietnamese", "vi"),
    ("Welsh", "cy"),
]

MODELS = [
    ("tiny (~1 GB)", "tiny"),
    ("base (~1 GB)", "base"),
    ("small (~2 GB)", "small"),
    ("medium (~5 GB)", "medium"),
    ("large (~10 GB)", "large"),
    ("turbo (~6 GB)", "turbo"),
]

def remove_duplicate_lines_prefix(text):
    lines = text.strip().split('\n')
    cleaned_lines = []

    def extract_content(line):
        m = re.match(r"\[\d{2}:\d{2}:\d{2}\]:\s+(.*)", line)
        return m.group(1).strip() if m else line.strip()

    for i, line in enumerate(lines):
        content = extract_content(line)
        is_redundant = False
        for j in range(i + 1, len(lines)):
            next_content = extract_content(lines[j])
            if content.startswith(next_content) or next_content.startswith(content):
                is_redundant = True
                break
        if not is_redundant:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def transcribe_audio(file, language, model, timestamps):
    if file is None:
        return "Please upload an audio or video file."
    url = 'http://localhost:9001/transcribe/audio/transcriptions'
    with open(file, 'rb') as f:
        files = {'file': f}
        data = {
            'language': language,
            'model': model,
            'timestamps': str(timestamps).lower()
        }
        r = requests.post(url, files=files, data=data)
        if r.ok:
            raw = r.json().get('formatted', '')
            cleaned = remove_duplicate_lines_prefix(raw)
            return cleaned if cleaned.strip() else "No transcription returned."
        return f"Error {r.status_code}: {r.text}"

def save_text_to_file(text):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    tmp.write(text)
    tmp.close()
    return tmp.name

with gr.Blocks(fill_width=True) as iface:
    with gr.Row():
        audio_input = gr.File(
            label="Upload audio or video file",
            file_types=[".mp3", ".wav", ".m4a", ".flac", ".ogg", ".mp4", ".mkv", ".webm", ".mov"],
            type="filepath"
        )
    # Player para preview (vai receber filepath)
    preview_audio = gr.Audio(label="Preview", interactive=False)

    with gr.Row():
        language_dropdown = gr.Dropdown([name for name, code in LANGUAGES], label="Language", value="Portuguese")
        model_dropdown = gr.Dropdown([name for name, val in MODELS], label="Model", value="small (~2 GB)")
        timestamps_checkbox = gr.Checkbox(label="Show timestamps", value=True)
    transcribe_btn = gr.Button("Transcribe", variant="primary")
    output_text = gr.Textbox(lines=10, max_lines=20, label="Transcription")
    download_btn = gr.Button("Download transcription (.txt)", variant="primary")
    download_file = gr.File(label="Download file")

    def transcribe_wrapper(file, language_name, timestamps, model_name):
        lang_code = next((code for name, code in LANGUAGES if name == language_name), "pt")
        model_val = next((val for name, val in MODELS if name == model_name), "small")
        return transcribe_audio(file, lang_code, model_val, timestamps)

    def prepare_download(text):
        if not text:
            return None
        return save_text_to_file(text)

    # Atualiza preview_audio quando carregar o arquivo
    def update_preview(file):
        return file if file else None

    audio_input.change(fn=update_preview, inputs=audio_input, outputs=preview_audio)
    transcribe_btn.click(fn=transcribe_wrapper, inputs=[audio_input, language_dropdown, timestamps_checkbox, model_dropdown], outputs=output_text)
    download_btn.click(fn=prepare_download, inputs=output_text, outputs=download_file)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=5000)
