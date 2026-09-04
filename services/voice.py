import speech_recognition as sr

from services.voice_parser import parse_voice_command


def listen_once():

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:

            print("Listening...")
            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

        print("Recognizing...")

        text = recognizer.recognize_google(audio)

        print("You said:", text)

        return parse_voice_command(text)

    except sr.WaitTimeoutError:
        return {
            "action": "timeout",
            "text": "",
        }

    except sr.UnknownValueError:
        return {
            "action": "unknown",
            "text": "",
        }

    except sr.RequestError:
        return {
            "action": "error",
            "text": "",
        }

    except Exception as e:
        print("Voice error:", e)

        return {
            "action": "error",
            "text": "",
        }