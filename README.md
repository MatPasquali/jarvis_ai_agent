# ⚡ JARVIS — Just A Rather Very Intelligent System

> *"Às vezes os maiores sonhos começam na poltrona do cinema."*

---

## 🎬 A Inspiração

Quando era criança, assisti aos filmes do Homem de Ferro e fiquei completamente fascinado com o **JARVIS** — o assistente de inteligência artificial do Tony Stark. Aquela voz calma, inteligente, que controlava tudo ao redor e ainda tinha personalidade própria. Ficou guardado na memória.

Anos depois, com o avanço da IA, percebi que era possível construir algo parecido com ferramentas acessíveis e gratuitas. Este projeto é a realização desse sonho de criança: **meu próprio JARVIS, rodando no meu computador**.

---

## 🤖 O que é este projeto?

O JARVIS é um **agente de IA pessoal** que roda **100% localmente** na sua máquina — sem custos de API, sem internet obrigatória, sem enviar seus dados para nenhum servidor externo.

Ele consegue:
- **Conversar** com você em português brasileiro com personalidade sarcástica e eficiente
- **Falar** com voz neural de alta qualidade (quase humana)
- **Ouvir** sua voz e transcrever o que você disse
- **Executar ações** no seu computador (abrir apps, pesquisar na web, ver o clima, salvar notas)
- **Lembrar** de conversas anteriores e usar esse contexto nas respostas
- **Exibir** uma interface visual futurista estilo laboratório do Tony Stark

---

## 🖥️ Interface HUD

A interface principal é um **HUD (Heads-Up Display)** no navegador, inspirado nas telas holográficas dos filmes do Homem de Ferro:

- Esfera holográfica 3D girando ao centro (6 anéis + 8 partículas orbitando + núcleo pulsante)
- A esfera **pulsa** enquanto o JARVIS fala
- Botão de microfone com animação de ondas sonoras
- Seletor de voz em tempo real (8 vozes neurais PT-BR)
- Métricas do sistema, logs de atividade, fonte futurista Orbitron

> 📸 *Adicione aqui um screenshot do HUD rodando (tire com Print Screen e salve como `hud/screenshot.png`)*

---

## 🛠️ Tecnologias utilizadas

| Módulo | Tecnologia | Por quê? |
|--------|-----------|----------|
| 🧠 Modelo de IA | [Ollama](https://ollama.ai) (LLaMA, Mistral, Qwen…) | Roda offline, grátis, privado |
| 🔊 Voz (TTS) | [Edge-TTS](https://github.com/rany2/edge-tts) — vozes Microsoft | Grátis, neural, PT-BR de alta qualidade |
| 🎙️ Reconhecimento | [Whisper](https://github.com/openai/whisper) (terminal) / Web Speech API (HUD) | Transcrição local sem API |
| 💾 Memória | [ChromaDB](https://www.trychroma.com) + fallback JSON | Busca semântica por vetores |
| 🌐 Interface | HTML + WebSocket (aiohttp + websockets) | Dashboard em tempo real no navegador |
| 🖥️ Comandos | Python subprocess / os | Ações diretas no sistema operacional |

---

## 📁 Estrutura do projeto

```
jarvis_final/
├── jarvis.py              # Ponto de entrada — argumentos de linha de comando
├── core/
│   └── agent.py           # Cérebro do agente: recebe input, pensa, responde
├── modules/
│   ├── tts.py             # Voz neural (Edge-TTS) com 8 vozes PT-BR curadas
│   ├── voice.py           # Captura de voz (Whisper STT) + pyttsx3 fallback
│   ├── memory.py          # Memória persistente (ChromaDB ou JSON)
│   ├── commands.py        # Ações no PC: abrir apps, buscar, clima, notas...
│   └── hud_server.py      # Servidor HTTP + WebSocket para o HUD
├── hud/
│   └── frontend/
│       └── index.html     # Interface visual completa (esfera 3D, voz, chat)
└── requirements.txt       # Dependências Python
```

---

## 🚀 Como instalar e rodar

### Pré-requisitos

- **Python 3.10+** instalado
- **[Ollama](https://ollama.ai)** instalado (baixe o instalador para Windows)

### Passo 1 — Baixe um modelo de IA

Abra o CMD e execute:
```cmd
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" pull mistral
```
> O modelo `mistral` (~4GB) oferece boa qualidade. Alternativas mais leves: `llama3.2` (2GB) ou `llama3.2:1b` (600MB).

### Passo 2 — Clone o repositório e instale as dependências

```cmd
git clone https://github.com/MatPasquali/jarvis.git
cd jarvis

python -m venv venv
venv\Scripts\activate

pip install ollama aiohttp websockets edge-tts chromadb
```

### Passo 3 — Rode o JARVIS

```cmd
"C:\caminho\para\python.exe" jarvis.py --mode hud --model mistral
```

Abra o navegador (Chrome ou Edge) em:
```
http://localhost:8080
```

---

## 🎙️ Vozes disponíveis (PT-BR Neural — todas gratuitas)

| Nome | Característica |
|------|---------------|
| `antonio` | Masculina, grave — **padrão Jarvis** |
| `valerio` | Masculina, autoritária |
| `humberto` | Masculina, narrativa |
| `donato` | Masculina, profissional |
| `francisca` | Feminina, calorosa |
| `yara` | Feminina, profissional |
| `giovanna` | Feminina, expressiva |
| `manuela` | Feminina, animada |

Troque a voz em tempo real pelo dropdown no HUD, ou via terminal:
```cmd
python jarvis.py --mode hud --voice valerio
```

---

## 💬 Exemplos de uso

```
Você: Abra o Chrome
Você: Que horas são?
Você: Qual a previsão do tempo em São Paulo?
Você: Me lembre daqui a 10 minutos de tomar água
Você: Pesquise por inteligência artificial no Google
```

---

## 🔮 Possibilidades de melhoria

Este projeto é uma base sólida com muito espaço para crescer:

### 🧠 Modelos mais inteligentes
- **Modelos maiores via Ollama**: `llama3.1:8b`, `qwen2.5:14b`, `mixtral` — quanto maior o modelo, mais inteligente, mas exige mais RAM/GPU
- **GPU NVIDIA**: Se tiver uma placa dedicada, o Ollama a usa automaticamente — velocidade muito superior
- **API do Claude (Anthropic)**: Integrar o Claude Sonnet/Haiku no lugar do Ollama — inteligência equivalente ao ChatGPT/Claude, com custo por uso
- **API do GPT-4**: Mesma ideia, com a OpenAI

### 🎤 Voz ainda mais realista
- **Clone de voz própria**: Usar [Coqui XTTS](https://github.com/coqui-ai/TTS) para treinar com sua própria voz (requer GPU)
- **Wake word**: Ativar o JARVIS apenas dizendo "Hey Jarvis" — sem clicar em nada
- **Esfera reagindo ao áudio**: Sincronizar a animação da esfera com a forma de onda da voz

### 🏠 Integrações
- **Home Assistant**: Controlar lâmpadas, TV, ar-condicionado por voz
- **Spotify**: Controlar músicas e playlists
- **Google Calendar / Gmail**: Ler agenda e e-mails
- **Câmera (visão)**: Descrever o que está na tela ou câmera (multimodal)

### ⚙️ Arquitetura
- **Streaming de tokens**: Resposta aparecendo palavra por palavra, como o ChatGPT
- **RAG avançado**: Memória de longo prazo com embeddings melhores
- **Agendador de tarefas**: Rotinas automáticas com APScheduler

---

## 🐛 Problemas comuns

| Problema | Solução |
|----------|---------|
| `"Ollama não está rodando"` | Execute `ollama serve` em outro terminal |
| `"Modelo não encontrado"` | Baixe com `ollama pull mistral` |
| Microfone não funciona no HUD | Use Chrome ou Edge (Firefox tem suporte limitado) |
| Python não encontrado | Use o caminho completo: `"C:\...\python.exe" jarvis.py` |

---

## 📄 Licença

MIT — faça o seu próprio JARVIS!

---

*Construído com ☕, nostalgia dos filmes do Homem de Ferro, e muita vontade de ter meu próprio assistente de IA.*
