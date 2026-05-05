"""
JARVIS - Just A Rather Very Intelligent System
Agente de IA local usando Ollama + voz + memória + comandos
"""

import asyncio
import argparse
from core.agent import JarvisAgent
from modules.tts import AVAILABLE_VOICES, DEFAULT_VOICE


async def main():
    parser = argparse.ArgumentParser(description="JARVIS - Agente de IA local")
    parser.add_argument("--mode", choices=["voice", "chat", "hud"], default="chat",
                        help="Modo de interação: voice (voz), chat (terminal), hud (interface gráfica)")
    parser.add_argument("--model", default="llama3.2",
                        help="Modelo Ollama a usar (ex: llama3.2, mistral, phi3)")
    parser.add_argument("--voice", default=DEFAULT_VOICE,
                        choices=list(AVAILABLE_VOICES.keys()),
                        help="Voz do JARVIS (Edge-TTS)")
    parser.add_argument("--list-voices", action="store_true",
                        help="Lista vozes disponíveis e encerra")
    parser.add_argument("--no-memory", action="store_true",
                        help="Desabilitar memória persistente")
    args = parser.parse_args()

    if args.list_voices:
        print("\n🔊 Vozes disponíveis (Edge-TTS):\n")
        for key, v in AVAILABLE_VOICES.items():
            marker = " ←  padrão" if key == DEFAULT_VOICE else ""
            print(f"  {key:12} → {v['label']}{marker}")
        print(f"\nUso: python jarvis.py --voice <nome>\n")
        return

    agent = JarvisAgent(
        model=args.model,
        use_memory=not args.no_memory,
        voice=args.voice,
    )

    await agent.start(mode=args.mode)


if __name__ == "__main__":
    asyncio.run(main())
