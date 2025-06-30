import os
import sys
import requests
import speech_recognition as sr
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTextEdit
)
from PySide6.QtCore import QThread, Signal

OPENAI_API_KEY = os.getenv("API_KEY")

def to_chatgpt(pergunta):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Você é um assistente que ouve o que a pessoa disse e dá uma sugestão ou correção se ela tiver falado algo incorreto. Seja claro e objetivo."},
            {"role": "user", "content": pergunta}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        resposta = response.json()["choices"][0]["message"]["content"]
        return resposta.strip()
    except Exception as e:
        return f"Erro ao consultar o ChatGPT: {e}"


class ReconhecimentoVozThread(QThread):
    resultado_signal = Signal(str, str)

    def run(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.resultado_signal.emit("", "Ajustando ruído ambiente... Aguarde.")
            recognizer.adjust_for_ambient_noise(source)
            self.resultado_signal.emit("", "Pronto! Pode falar.")

            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                texto = recognizer.recognize_google(audio, language="pt-BR")
                resposta = to_chatgpt(texto)
                self.resultado_signal.emit(texto, resposta)
            except sr.WaitTimeoutError:
                self.resultado_signal.emit("", "Tempo esgotado. Tente novamente.")
            except sr.UnknownValueError:
                self.resultado_signal.emit("", "Não entendi o que você disse.")
            except sr.RequestError:
                self.resultado_signal.emit("", "Erro ao conectar com a API do Google.")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reconhecimento de Voz + Correção ChatGPT")

        self.layout = QVBoxLayout()

        self.label_entrada = QLabel("Você disse:")
        self.texto_entrada = QTextEdit()
        self.texto_entrada.setReadOnly(True)

        self.label_resposta = QLabel("ChatGPT sugeriu:")
        self.texto_resposta = QTextEdit()
        self.texto_resposta.setReadOnly(True)

        self.botao_gravar = QPushButton("Falar")
        self.botao_gravar.clicked.connect(self.iniciar_reconhecimento)

        self.layout.addWidget(self.label_entrada)
        self.layout.addWidget(self.texto_entrada)
        self.layout.addWidget(self.label_resposta)
        self.layout.addWidget(self.texto_resposta)
        self.layout.addWidget(self.botao_gravar)

        self.setLayout(self.layout)

        self.reconhecimento_thread = ReconhecimentoVozThread()
        self.reconhecimento_thread.resultado_signal.connect(self.atualizar_resultado)

    def iniciar_reconhecimento(self):
        self.botao_gravar.setEnabled(False)
        self.texto_entrada.clear()
        self.texto_resposta.clear()
        self.reconhecimento_thread.start()

    def atualizar_resultado(self, texto, resposta):
        self.texto_entrada.setText(texto)
        self.texto_resposta.setText(resposta)
        self.botao_gravar.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = App()
    janela.resize(600, 400)
    janela.show()
    sys.exit(app.exec())
