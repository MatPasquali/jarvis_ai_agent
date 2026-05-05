"""
Servidor HUD do JARVIS
Serve a interface web e expõe WebSocket + endpoints HTTP para TTS
"""

import asyncio
import json
from pathlib import Path

try:
    import websockets
    from aiohttp import web
    HUD_AVAILABLE = True
except ImportError:
    HUD_AVAILABLE = False

from modules.tts import EdgeTTS, AVAILABLE_VOICES, DEFAULT_VOICE


class HUDServer:
    def __init__(self, agent):
        self.agent = agent
        self.clients = set()
        self.hud_dir = Path(__file__).parent.parent / "hud" / "frontend"
        self.tts = EdgeTTS(voice=DEFAULT_VOICE)

    async def start(self, http_port: int = 8080, ws_port: int = 8765):
        if not HUD_AVAILABLE:
            print("⚠️  HUD requer: pip install aiohttp websockets edge-tts")
            print("   Iniciando em modo chat como fallback...")
            await self.agent._chat_loop()
            return

        print(f"\n🖥️  HUD disponível em: http://localhost:{http_port}")
        print(f"   WebSocket em: ws://localhost:{ws_port}")
        print(f"   Voz atual: {self.tts.voice_id}\n")

        await asyncio.gather(
            self._start_http(http_port),
            self._start_ws(ws_port),
        )

    async def _start_http(self, port: int):
        app = web.Application()

        # Endpoints da API
        app.router.add_get("/api/voices", self._handle_list_voices)
        app.router.add_post("/api/tts", self._handle_tts)
        app.router.add_post("/api/voice", self._handle_set_voice)

        # Frontend estático (precisa vir depois das rotas de API)
        app.router.add_static("/", self.hud_dir)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", port)
        await site.start()

    async def _handle_list_voices(self, request):
        """GET /api/voices — lista vozes disponíveis"""
        return web.json_response({
            "voices": AVAILABLE_VOICES,
            "current": self.tts.voice_key,
        })

    async def _handle_tts(self, request):
        """POST /api/tts — gera áudio MP3 a partir de texto"""
        try:
            data = await request.json()
            text = data.get("text", "")
            if not text:
                return web.Response(status=400, text="texto vazio")

            audio_bytes = await self.tts.synthesize_to_bytes(text)
            if not audio_bytes:
                return web.Response(status=500, text="falha ao gerar audio")

            return web.Response(
                body=audio_bytes,
                content_type="audio/mpeg",
                headers={"Cache-Control": "no-cache"},
            )
        except Exception as e:
            return web.Response(status=500, text=str(e))

    async def _handle_set_voice(self, request):
        """POST /api/voice — troca voz ativa"""
        try:
            data = await request.json()
            voice = data.get("voice", DEFAULT_VOICE)
            success = self.tts.set_voice(voice)
            return web.json_response({
                "success": success,
                "current": self.tts.voice_key,
                "voice_id": self.tts.voice_id,
            })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def _start_ws(self, port: int):
        async def handler(ws):
            self.clients.add(ws)
            try:
                async for raw in ws:
                    data = json.loads(raw)
                    user_msg = data.get("message", "")

                    await ws.send(json.dumps({"type": "thinking"}))

                    reply = await self.agent.think(user_msg)
                    reply = await self.agent.process_response(reply)

                    await ws.send(json.dumps({
                        "type": "reply",
                        "message": reply,
                    }))
            finally:
                self.clients.discard(ws)

        async with websockets.serve(handler, "localhost", port):
            await asyncio.Future()  # roda para sempre

    async def broadcast(self, data: dict):
        """Envia dados para todos os clientes HUD conectados."""
        if self.clients:
            msg = json.dumps(data)
            await asyncio.gather(*[c.send(msg) for c in self.clients])
