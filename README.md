# Easeprompt - Meta-Prompt Expansion Engine

Easeprompt is an intelligent prompt expansion and refinement engine built with **FastAPI** and a sleek, modern glassmorphic web UI. It transforms simple, vague ideas into production-grade prompts tailored for LLMs (GPT-4, Claude, Gemini, etc.).

---

## ✨ Features

- **Meta-Prompt Framework**: Automatically identifies objective, domain, context, constraints, and success criteria.
- **Smart Expansion**: Generates comprehensive, high-detail prompts with system instructions, formatting guidelines, and edge-case handling.
- **Heuristic Generator**: Fallback heuristics engine for structured generation even without external API dependencies.
- **Quality & Safety Scoring**: Filters, validates, and refines prompts according to quality benchmarks.
- **Modern Responsive UI**: Clean, glassmorphism design with real-time copy, parameter controls, and direct preview.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation

Clone this repository and navigate to the project directory:
```bash
git clone https://github.com/<your-username>/easeprompt.git
cd easeprompt
```

Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```
*(Optionally configure your API keys in `.env` if external LLM generation is enabled).*

### 4. Running the Application

Launch the server using:
```bash
python main.py
```
Or directly with Uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🌐 Cloud Deployment (Render, Railway, Fly.io)

### One-Click Deploy to Render
1. Create a free account at [Render.com](https://render.com).
2. Click **New +** > **Web Service** and connect this repository: `Anusmrith/Easeprompt`.
3. Set the runtime to **Python 3**.
4. Set Build Command: `pip install -r requirements.txt`.
5. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
6. Select the **Free** instance tier and click **Deploy Web Service**.

Easeprompt includes a ready-to-use `render.yaml` and `Procfile` for automatic deployment configuration.

---

## 📁 Project Structure

```
├── app/
│   ├── expansion_engine.py      # Core prompt expansion & streaming logic
│   ├── heuristic_generator.py   # Heuristic rules & domain knowledge
│   ├── meta_prompt.py           # Meta-prompt templates & formatting
│   ├── models.py                # Pydantic data schemas
│   ├── quality_filter.py        # Quality & constraint validation
│   ├── rate_limiter.py          # Production in-memory IP rate limiter (DDoS protection)
│   ├── main.py                  # FastAPI route controllers & middleware
│   └── static/                  # Modern UI interface (HTML, CSS, JS)
│       ├── index.html
│       ├── style.css
│       └── app.js
├── .env.example                 # Sample environment variables
├── .gitignore                   # Git ignore patterns
├── LICENSE                      # MIT Open Source License
├── main.py                      # Application entrypoint
├── Procfile                     # Cloud process configuration
├── render.yaml                  # Render Blueprint definition
├── requirements.txt             # Project dependencies
└── test_backend.py              # Automated test suite
```

---

## 📝 License & Disclaimers

- **License**: Distributed under the [MIT License](LICENSE). Copyright (c) 2026 Anusmrith.
- **Privacy**: Easeprompt processes prompt expansions real-time in memory. No user prompts or generation logs are stored on disk or databases.
- **Trademarks**: Compatible model names (ChatGPT, Claude, Gemini, Cursor) are referenced for compatibility purposes only and remain the trademarks of their respective owners.

