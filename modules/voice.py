"""
Módulo de voz do JARVIS
- STT (Speech-to-Text): OpenAI Whisper (roda local)
- TTS (Text-to-Speech): pyttsx3 (offline) ou edge-tts (online, melhor qualidade)
"""

import io
import queue
import threading
import tempfile
import os

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


class VoiceModule:
    def __init__(self, whisper_model: str = "base"):
        self.whisper_model = None
        self.tts_engine = None
        self._setup_stt(whisper_model)
        self._setup_tts()

    def _setup_stt(self, model_name: str):
        """Carrega o modelo Whisper para reconhecimento de voz."""
        if not WHISPER_AVAILABLE:
            print("⚠️  Whisper não instalado. Execute: pip install openai-whisper")
            return
        try:
            print(f"   Carregando Whisper ({model_name})...")
            self.whisper_model = whisper.load_model(model_name)
            print("   ✓ Whisper pronto")
        except Exception as e:
            print(f"   ✗ Erro ao carregar Whisper: {e}")

    def _setup_tts(self):
        """Configura o motor de síntese de voz."""
        if not PYTTSX3_AVAILABLE:
            print("⚠️  pyttsx3 não instalado. Execute: pip install pyttsx3")
            return
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty("rate", 175)   # velocidade
            self.tts_engine.setProperty("volume", 0.9)

            # Tenta selecionar voz em português
            voices = self.tts_engine.getProperty("voices")
            for v in voices:
                if "pt" in v.id.lower() or "portuguese" in v.name.lower():
                    self.tts_engine.setProperty("voice", v.id)
                    break
            print("   ✓ TTS pronto")
        except Exception as e:
            print(f"   ✗ Erro ao configurar TTS: {e}")

    def listen(self, duration: int = 5, samplerate: int = 16000) -> str:
        """
        Grava áudio do microfone e transcreve com Whisper.
        Retorna o texto reconhecido ou string vazia.
        """
        if not AUDIO_AVAILABLE:
            # Fallback para input de texto
            return input("Você (texto): ").strip()

        if not self.whisper_model:
            return input("Você (texto — Whisper indisponível): ").strip()

        print("🎙️  Ouvindo...", end="\r")
        try:
            audio = sd.rec(
                int(duration * samplerate),
                samplerate=samplerate,
                channels=1,
                dtype="float32"
            )
            sd.wait()

            # Salva em arquivo temporário e transcreve
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                sf.write(f.name, audio, samplerate)
                result = self.whisper_model.transcribe(f.name, language="pt")
                os.unlink(f.name)

            text = result["text"].strip()
            return text
        except Exception as e:
            print(f"Erro ao ouvir: {e}")
            return ""

    def speak(self, text: str):
        """Fala o texto usando TTS."""
        if not self.tts_engine:
            print(f"[TTS indisponível] {text}")
            return

        # Remove markdown e emojis para a fala
        clean = text.replace("*", "").replace("#", "").replace("`", "")

        try:
            self.tts_engine.say(clean)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Erro no TTS: {e}")
