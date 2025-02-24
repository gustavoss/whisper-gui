from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_file = request.files['audio']
    files = {'file': audio_file}
    data = {
        'word_timestamps': 'true',  # Passando como string para evitar problemas
        'language': 'pt'    # Especificando o idioma como português brasileiro
    }

    response = requests.post('http://localhost:9001/transcribe/audio/transcriptions', files=files, data=data)

    if response.ok:
        result = response.json()  # Obter o resultado da transcrição
        print("Resposta da API:", result)  # Adicione esta linha para depuração
        return jsonify(result)  # Retornar o resultado como JSON
    else:
        print(f"Erro: {response.status_code}, {response.text}")
        return jsonify({"error": "Failed to transcribe audio."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)