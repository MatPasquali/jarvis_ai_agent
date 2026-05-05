"""
Core do agente Jarvis — orquestra todos os módulos
"""

import asyncio
import json
from datetime import datetime
from typing import Optional

import ollama

from modules.voice import VoiceModule
from modules.commands import CommandModule
from modules.memory import MemoryModule
from modules.hud_server import HUDServer
from modules.tts import EdgeTTS, DEFAULT_VOICE


SYSTEM_PROMPT = """Você é JARVIS, um assistente de IA pessoal avançado, inteligente e direto.
Fale sempre em português brasileiro.
Seja conciso, eficiente e levemente sarcástico como o Jarvis do Tony Stark.
Quando o usuário pedir para executar ações no computador, responda com um JSON no formato:
{"action": "nome_da_ação", "args": {...}, "response": "o que você vai dizer"}
Ações disponíveis: open_app, search_web, get_time, list_files, run_command, set_reminder.
Para conversas normais, responda com texto puro."""


class JarvisAgent:
    def __init__(self, model: str = "llama3.2", use_memory: bool = True, voice: str = DEFAULT_VOICE):
        self.model = model
        self.use_memory = use_memory
        self.conversation_history = []

        # Módulos
        self.memory = MemoryModule() if use_memory else None
        self.voice = VoiceModule()
        self.tts = EdgeTTS(voice=voice)
        self.commands = CommandModule()
        self.hud = None

        print(f"\n⚡ JARVIS iniciando com modelo: {self.model}")
        print(f"   Voz: {self.tts.voice_id}")
        print(f"   Memória: {'ativada' if use_memory else 'desativada'}")
        self._check_ollama()

    def _check_ollama(self):
        try:
            models = ollama.list()
            available = [m.model for m in models.models]
            if not any(self.model in m for m in available):
                print(f"\n⚠️  Modelo '{self.model}' não encontrado.")
                print(f"   Execute: ollama pull {self.model}")
                print(f"   Modelos disponíveis: {', '.join(available) or 'nenhum'}\n")
        except Exception:
            print("\n⚠️  Ollama não está rodando. Execute: ollama serve\n")

    async def think(self, user_input: str) -> str:
        memory_context = ""
        if self.memory:
            relevant = self.memory.search(user_input, k=3)
            if relevant:
                memory_context = "\n[Memória relevante]:\n" + "\n".join(relevant)

        messages = [{"role": "system", "content": SYSTEM_PROMPT + memory_context}]
        messages += self.conversation_history[-10:]
        messages.append({"role": "user", "content": user_input})

        response = ollama.chat(model=self.model, messages=messages)
        reply = response.message.content

        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": reply})

        if self.memory:
            self.memory.save(user_input, reply)

        return reply

    async def process_response(self, reply: str) -> str:
        reply = reply.strip()
        if reply.startswith("{") and '"action"' in reply:
            try:
                data = json.loads(reply)
                action = data.get("action")
                args = data.get("args", {})
                spoken = data.get("response", "Executando...")
                result = await self.commands.execute(action, args)
                return f"{spoken}\n[{result}]"
            except json.JSONDecodeError:
                pass
        return reply

    async def start(self, mode: str = "chat"):
        print(f"\n🤖 JARVIS online — modo: {mode.upper()}")
        print("   Digite 'sair' para encerrar\n")

        if mode == "hud":
            self.hud = HUDServer(self)
            await self.hud.start()
            return

        if mode == "voice":
            await self._voice_loop()
        else:
            await self._chat_loop()

    async def _chat_loop(self):
        while True:
            try:
                user_input = input("Você: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 JARVIS desligando.")
                break

            if not user_input:
                continue
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("👋 JARVIS desligando.")
                break

            print("⚡ Pensando...", end="\r")
            reply = await self.think(user_input)
            reply = await self.process_response(reply)
            print(f"JARVIS: {reply}\n")

    async def _voice_loop(self):
        """Loop de voz: escuta com Whisper → pensa → fala com Edge-TTS."""
        print("🎙️  Aguardando sua voz... (Ctrl+C para sair)\n")
        while True:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, self.voice.listen
                )
                if not user_input:
                    continue

                print(f"Você: {user_input}")
                reply = await self.think(user_input)
                reply = await self.process_response(reply)
                print(f"JARVIS: {reply}\n")

                # Fala com Edge-TTS (qualidade alta) com fallback para pyttsx3
                try:
                    await self.tts.speak(reply)
                except Exception:
                    await asyncio.get_event_loop().run_in_executor(
                        None, self.voice.speak, reply
                    )
            except KeyboardInterrupt:
                print("\n\n👋 JARVIS desligando.")
                break
