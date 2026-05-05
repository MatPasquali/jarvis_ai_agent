"""
Módulo de TTS usando Edge-TTS (Microsoft Neural Voices).
Vozes em português brasileiro de altíssima qualidade, gratuitas.

Vozes disponíveis em PT-BR:
- pt-BR-AntonioNeural    → masculina, grave (ideal para Jarvis)
- pt-BR-FranciscaNeural  → feminina, calorosa
- pt-BR-BrendaNeural     → feminina, jovem
- pt-BR-DonatoNeural     → masculina, profissional
- pt-BR-ElzaNeural       → feminina, madura
- pt-BR-FabioNeural      → masculina, casual
- pt-BR-GiovannaNeural   → feminina, expressiva
- pt-BR-HumbertoNeural   → masculina, narrativa
- pt-BR-JulioNeural      → masculina, jovem
- pt-BR-LeilaNeural      → feminina, suave
- pt-BR-LeticiaNeural    → feminina, neutra
- pt-BR-ManuelaNeural    → feminina, animada
- pt-BR-NicolauNeural    → masculina, calmo
- pt-BR-ValerioNeural    → masculina, autoritária
- pt-BR-YaraNeural       → feminina, profissional

Para listar todas: edge-tts --list-voices
"""

import asyncio
import io
import tempfile
import os
from pathlib import Path

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


# Vozes recomendadas em PT-BR (curadoria)
AVAILABLE_VOICES = {
    "antonio":    {"id": "pt-BR-AntonioNeural",   "label": "Antonio (masc, grave) — recomendada Jarvis"},
    "francisca":  {"id": "pt-BR-FranciscaNeural", "label": "Francisca (fem, calorosa)"},
    "valerio":    {"id": "pt-BR-ValerioNeural",   "label": "Valério (masc, autoritário)"},
    "humberto":   {"id": "pt-BR-HumbertoNeural",  "label": "Humberto (masc, narrativo)"},
    "donato":     {"id": "pt-BR-DonatoNeural",    "label": "Donato (masc, profissional)"},
    "yara":       {"id": "pt-BR-YaraNeural",      "label": "Yara (fem, profissional)"},
    "giovanna":   {"id": "pt-BR-GiovannaNeural",  "label": "Giovanna (fem, expressiva)"},
    "manuela":    {"id": "pt-BR-ManuelaNeural",   "label": "Manuela (fem, animada)"},
}

DEFAULT_VOICE = "antonio"


class EdgeTTS:
    def __init__(self, voice: str = DEFAULT_VOICE, rate: str = "+0%", pitch: str = "+0Hz"):
        self.voice_key = voice
        self.voice_id = AVAILABLE_VOICES.get(voice, AVAILABLE_VOICES[DEFAULT_VOICE])["id"]
        self.rate = rate     # "-50%" a "+100%"
        self.pitch = pitch   # "-50Hz" a "+50Hz"

        if not EDGE_TTS_AVAILABLE:
            print("⚠️  edge-tts não instalado. Execute: pip install edge-tts")

    def set_voice(self, voice: str):
        """Troca a voz em tempo real."""
        if voice in AVAILABLE_VOICES:
            self.voice_key = voice
            self.voice_id = AVAILABLE_VOICES[voice]["id"]
            return True
        return False

    async def synthesize_to_bytes(self, text: str) -> bytes:
        """Gera áudio MP3 em memória e retorna os bytes."""
        if not EDGE_TTS_AVAILABLE:
            return b""

        # Limpa markdown e caracteres especiais que atrapalham a fala
        clean = self._clean_text(text)
        if not clean.strip():
            return b""

        try:
            communicate = edge_tts.Communicate(
                text=clean,
                voice=self.voice_id,
                rate=self.rate,
                pitch=self.pitch,
            )

            buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buffer.write(chunk["data"])

            return buffer.getvalue()
        except Exception as e:
            print(f"Erro Edge-TTS: {e}")
            return b""

    async def save_to_file(self, text: str, path: str):
        """Salva áudio em arquivo MP3."""
        audio_bytes = await self.synthesize_to_bytes(text)
        if audio_bytes:
            Path(path).write_bytes(audio_bytes)

    async def speak(self, text: str):
        """Gera e reproduz o áudio diretamente (modo terminal)."""
        audio_bytes = await self.synthesize_to_bytes(text)
        if not audio_bytes:
            print(f"[TTS falhou] {text}")
            return

        # Salva em temp e reproduz
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            self._play_audio(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _play_audio(self, path: str):
        """Reproduz áudio MP3 usando o player nativo do sistema."""
        import sys
        import subprocess

        if sys.platform == "darwin":
            subprocess.run(["afplay", path], check=False)
        elif sys.platform == "linux":
            for player in ["mpg123", "mpv", "ffplay", "aplay"]:
                try:
                    subprocess.run([player, path],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL,
                                   check=True)
                    return
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            print("⚠️  Nenhum player encontrado. Instale: sudo apt install mpg123")
        else:  # Windows
            os.startfile(path)

    def _clean_text(self, text: str) -> str:
        """Remove markdown, emojis, blocos de código antes da fala."""
        import re
        text = re.sub(r"```[\s\S]*?```", " bloco de código ", text)
        text = re.sub(r"`[^`]+`", "", text)
        text = re.sub(r"[*#_~\[\]()`]", "", text)
        text = re.sub(r"https?://\S+", " link ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()[:1000]  # limite de 1000 chars por fala

    @staticmethod
    def list_voices() -> dict:
        """Retorna o dicionário de vozes disponíveis."""
        return AVAILABLE_VOICES


# Função utilitária para uso síncrono
def speak_sync(text: str, voice: str = DEFAULT_VOICE):
    """Wrapper síncrono para usar fora de contexto async."""
    tts = EdgeTTS(voice=voice)
    asyncio.run(tts.speak(text))


if __name__ == "__main__":
    # Teste rápido — execute: python modules/tts.py
    import sys
    text = " ".join(sys.argv[1:]) or "Olá, eu sou o Jarvis. Sistemas online e operando normalmente."
    print(f"🔊 Falando com a voz '{DEFAULT_VOICE}'...")
    speak_sync(text)
