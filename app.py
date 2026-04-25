from flask import Flask, render_template, request, jsonify
import requests
import os
import base64
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
chroma = chromadb.Client()
collection = chroma.get_or_create_collection("codebase")
indexed_repo = {"url": None}

def get_repo_files(repo_url):
    parts = repo_url.rstrip("/").split("/")
    owner = parts[-2]
    repo = parts[-1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    response = requests.get(api_url)
    if response.status_code != 200:
        api_url = api_url.replace("/main?", "/master?")
        response = requests.get(api_url)
    files = []
    for item in response.json().get("tree", []):
        if item["type"] == "blob" and item["path"].endswith((".py", ".md", ".txt")):
            files.append((item["path"], item["url"]))
    return files

def fetch_file_content(url):
    response = requests.get(url)
    content = response.json().get("content", "")
    try:
        return base64.b64decode(content).decode("utf-8", errors="ignore")
    except:
        return ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/index_repo", methods=["POST"])
def index_repo():
    repo_url = request.json.get("repo_url")
    try:
        chroma.delete_collection("codebase")
    except:
        pass
    global collection
    collection = chroma.get_or_create_collection("codebase")
    files = get_repo_files(repo_url)
    for i, (path, url) in enumerate(files[:30]):
        content = fetch_file_content(url)
        if content.strip():
            collection.add(
                documents=[content[:2000]],
                ids=[f"file_{i}"],
                metadatas=[{"path": path}]
            )
    indexed_repo["url"] = repo_url
    file_paths = [path for path, url in files[:30]]
    return jsonify({"status": "ok", "files": len(files), "file_paths": file_paths})

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question")
    results = collection.query(query_texts=[question], n_results=3)
    context = ""
    for i, doc in enumerate(results["documents"][0]):
        path = results["metadatas"][0][i]["path"]
        context += f"\n--- {path} ---\n{doc}\n"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a code expert. Answer questions about the codebase using the provided code context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return jsonify({"answer": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(debug=True)