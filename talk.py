import speech_recognition as sr
import requests, os

OPENAI_API_KEY = api_key = os.getenv("API_KEY")
def to_chatgpt(pergunta):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
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

def reconhecer_microfone():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Ajustando ruído ambiente... Aguarde.")
        recognizer.adjust_for_ambient_noise(source)
        print("Pronto! Pode falar. (Pressione Ctrl+C para parar)\n")

        while True:
            try:
                print("Ouvindo...")
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                print("Reconhecendo...")
                text = recognizer.recognize_google(audio_data, language="pt-BR")
                print("Você disse:", text)

                resposta_chatgpt = to_chatgpt(text)
                print("ChatGPT respondeu:", resposta_chatgpt)
                print("-" * 60)

            except sr.WaitTimeoutError:
                print("Tempo esgotado para falar. Tentando de novo...")
            except sr.UnknownValueError:
                print("Não entendi o que você disse. Tente novamente.")
            except sr.RequestError:
                print("Erro ao conectar com a API do Google.")
            except KeyboardInterrupt:
                print("\nEncerrando reconhecimento por microfone.")
                break



def main():
    while True:
        print("\nEscolha a opção:")
        print("1 - Reconhecer voz pelo microfone")
        print("2 - Reconhecer áudio a partir de um arquivo de URL")
        print("0 - Sair")
        escolha = input("Digite a opção desejada: ").strip()

        if escolha == "1":
            reconhecer_microfone()
        elif escolha == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main()
