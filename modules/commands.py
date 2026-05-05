"""
Módulo de comandos do JARVIS
Executa ações no sistema operacional
"""

import os
import sys
import subprocess
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict


class CommandModule:

    async def execute(self, action: str, args: Dict[str, Any] = {}) -> str:
        """Roteador central de ações."""
        handlers = {
            "open_app":     self.open_app,
            "search_web":   self.search_web,
            "get_time":     self.get_time,
            "list_files":   self.list_files,
            "run_command":  self.run_command,
            "set_reminder": self.set_reminder,
            "get_weather":  self.get_weather,
            "take_note":    self.take_note,
        }

        handler = handlers.get(action)
        if not handler:
            return f"Ação '{action}' não reconhecida."

        try:
            return await handler(**args)
        except Exception as e:
            return f"Erro ao executar '{action}': {e}"

    # ─────────────────────────────────
    # AÇÕES
    # ─────────────────────────────────

    async def open_app(self, name: str = "") -> str:
        """Abre um aplicativo pelo nome."""
        app_map = {
            # macOS
            "chrome": "open -a 'Google Chrome'",
            "firefox": "open -a Firefox",
            "safari": "open -a Safari",
            "vscode": "open -a 'Visual Studio Code'",
            "terminal": "open -a Terminal",
            "spotify": "open -a Spotify",
            "finder": "open -a Finder",
            # Linux
            "chromium": "chromium-browser",
            "nautilus": "nautilus",
            # Windows
            "notepad": "notepad.exe",
            "explorer": "explorer.exe",
        }

        name_lower = name.lower()

        # Procura no mapa
        for key, cmd in app_map.items():
            if key in name_lower:
                subprocess.Popen(cmd, shell=True)
                return f"Abrindo {name}..."

        # Tenta abrir diretamente
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", "-a", name])
            elif sys.platform == "linux":
                subprocess.Popen([name.lower()])
            else:
                os.startfile(name)
            return f"Abrindo {name}..."
        except Exception as e:
            return f"Não consegui abrir '{name}': {e}"

    async def search_web(self, query: str = "") -> str:
        """Abre uma pesquisa no navegador padrão."""
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Pesquisando por: {query}"

    async def get_time(self) -> str:
        """Retorna data e hora atuais."""
        now = datetime.now()
        return now.strftime("Agora são %H:%M do dia %d/%m/%Y (%A)")

    async def list_files(self, path: str = ".") -> str:
        """Lista arquivos em um diretório."""
        try:
            p = Path(path).expanduser()
            files = list(p.iterdir())
            names = [f.name + ("/" if f.is_dir() else "") for f in sorted(files)[:20]]
            return f"Arquivos em {p}:\n" + "\n".join(names)
        except Exception as e:
            return f"Erro ao listar arquivos: {e}"

    async def run_command(self, command: str = "") -> str:
        """
        Executa um comando shell.
        ⚠️ Use com cuidado — só executa comandos seguros.
        """
        SAFE_COMMANDS = ["ls", "pwd", "echo", "date", "whoami", "hostname",
                         "df", "free", "uptime", "uname", "ping"]
        first_word = command.strip().split()[0] if command.strip() else ""

        if first_word not in SAFE_COMMANDS:
            return f"Comando '{first_word}' não permitido por segurança."

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=10
            )
            output = result.stdout.strip() or result.stderr.strip()
            return output[:500] if output else "(sem saída)"
        except subprocess.TimeoutExpired:
            return "Comando expirou (timeout 10s)."
        except Exception as e:
            return f"Erro: {e}"

    async def set_reminder(self, message: str = "", minutes: int = 5) -> str:
        """Agenda um lembrete simples (via notificação do sistema)."""
        import threading

        def _remind():
            import time
            time.sleep(minutes * 60)
            if sys.platform == "darwin":
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "JARVIS"'
                ])
            elif sys.platform == "linux":
                subprocess.run(["notify-send", "JARVIS", message])
            else:
                # Windows — via PowerShell
                subprocess.run([
                    "powershell", "-Command",
                    f'New-BurntToastNotification -Text "JARVIS", "{message}"'
                ])

        t = threading.Thread(target=_remind, daemon=True)
        t.start()
        due = (datetime.now() + timedelta(minutes=minutes)).strftime("%H:%M")
        return f"Lembrete definido para {due}: {message}"

    async def get_weather(self, city: str = "") -> str:
        """Busca previsão do tempo usando wttr.in (sem chave de API)."""
        import urllib.request
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=3"
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return r.read().decode("utf-8").strip()
        except Exception:
            return f"Não consegui obter o clima para {city}."

    async def take_note(self, content: str = "") -> str:
        """Salva uma nota em arquivo."""
        notes_file = Path("memory/notes.md")
        notes_file.parent.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(notes_file, "a") as f:
            f.write(f"\n## {timestamp}\n{content}\n")
        return f"Nota salva em {notes_file}"
