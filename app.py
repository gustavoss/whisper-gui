import gradio as gr
import requests
import re
import tempfile

def format_transcription(text, max_len=100):
    sentences = re.split(r'(?<=[.,])\s*', text.strip())

    lines = []
    current_line = ""
    for sentence in sentences:
        if len(current_line) + len(sentence) <= max_len:
            current_line += sentence + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = sentence + " "
    if current_line:
        lines.append(current_line.strip())

    return "\n".join(lines)

def transcribe_audio(file):
    url = 'http://localhost:9001/transcribe/audio/transcriptions'
    with open(file, 'rb') as f:
        files = {'file': f}
        data = {'word_timestamps': 'true', 'language': 'pt'}
        r = requests.post(url, files=files, data=data)
        if r.ok:
            text = r.json().get('text', 'Nenhum texto retornado')
            formatted = format_transcription(text)
            return formatted
    return "Erro na transcrição."

def save_text_to_file(text):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    tmp.write(text)
    tmp.close()
    return tmp.name

with gr.Blocks() as iface:
    audio_input = gr.Audio(sources=["upload", "microphone"], type="filepath", label="Envie um áudio ou grave")
    output_text = gr.Textbox(lines=10, max_lines=20, label="Transcrição")
    download_btn = gr.Button("Baixar transcrição (.txt)")
    download_file = gr.File(label="Download do arquivo")

    def transcribe_and_show(file):
        result = transcribe_audio(file)
        return result

    def prepare_download(text):
        return save_text_to_file(text)

    audio_input.change(fn=transcribe_and_show, inputs=audio_input, outputs=output_text)
    download_btn.click(fn=prepare_download, inputs=output_text, outputs=download_file)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=5000)
