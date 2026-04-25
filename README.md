# repo-chat 🤖

Chat with any GitHub repository using AI. Paste a URL, ask questions about the code instantly.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Groq](https://img.shields.io/badge/Groq-LLaMA3-orange)
![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-purple)

## What it does

- Paste any public GitHub repo URL
- It fetches and indexes all code files automatically
- Ask questions in plain English about the codebase
- AI answers using only the actual code as context
- Shows which files were used to generate the answer

## Tech stack

- **Backend** — Flask (Python)
- **LLM** — LLaMA 3.3 70B via Groq API
- **Vector DB** — ChromaDB
- **Embeddings** — ChromaDB default embeddings
- **Frontend** — Vanilla HTML/CSS/JS

## How it works

1. GitHub API fetches all `.py`, `.md`, `.txt` files from the repo
2. Files are chunked and stored in ChromaDB (vector database)
3. When you ask a question, ChromaDB finds the most relevant files
4. Those files are sent as context to LLaMA 3.3 via Groq
5. The AI answers based only on the actual code

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/Akshay-ctr/repo-chat-.git
cd repo-chat-
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies

```bash
pip install flask groq chromadb requests python-dotenv
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Add your Groq API key to `.env`:
GROQ_API_KEY=your-groq-api-key-here

Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 5. Run the app

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Usage

1. Paste a public GitHub repo URL on the landing page
2. Click **Analyse repo** and wait for indexing (~30 seconds)
3. Ask questions like:
   - *"What does this project do?"*
   - *"How does routing work?"*
   - *"Where is the database connection set up?"*
   - *"What are the main entry points?"*

## Project structure
repo-chat/
├── app.py              # Flask backend + RAG logic
├── templates/
│   └── index.html      # Frontend UI
├── static/
│   └── style.css       # Styles (if any)
├── .env.example        # Environment variables template
├── .gitignore
└── README.md

## Limitations

- Only indexes first 30 files (to stay within free API limits)
- Works with public repos only
- Best with Python/JS/TS codebases

## Built by
Akshay

[Akshay](https://github.com/Akshay-ctr) — built as part of an AI engineering learning journey.
Save it, then run:
bashgit add .
git commit -m "add README"
git push
