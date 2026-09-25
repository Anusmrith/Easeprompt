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

## 📁 Project Structure

```
├── app/
│   ├── expansion_engine.py      # Core prompt expansion logic
│   ├── heuristic_generator.py   # Heuristics rules & templates
│   ├── meta_prompt.py           # Meta-prompt definitions & formatting
│   ├── models.py                # Pydantic data schemas
│   ├── quality_filter.py        # Quality & constraint validation
│   ├── main.py                  # FastAPI route controllers
│   └── static/                  # Web interface (HTML, CSS, JS)
│       ├── index.html
│       ├── style.css
│       └── app.js
├── .env.example                 # Sample configuration
├── .gitignore                   # Git ignore patterns
├── main.py                      # Application entrypoint
├── requirements.txt             # Project dependencies
└── test_backend.py              # Backend test scripts
```

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
