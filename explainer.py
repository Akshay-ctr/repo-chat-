import requests
import os
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
chroma = chromadb.Client()
collection = chroma.get_or_create_collection("codebase")

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
    return owner, repo, files

def fetch_file_content(url):
    import base64
    response = requests.get(url)
    content = response.json().get("content", "")
    try:
        return base64.b64decode(content).decode("utf-8", errors="ignore")
    except:
        return ""

def index_repo(repo_url):
    print("\nFetching repo files...")
    owner, repo, files = get_repo_files(repo_url)
    print(f"Found {len(files)} files. Indexing...")
    for i, (path, url) in enumerate(files[:30]):  # limit to 30 files
        content = fetch_file_content(url)
        if content.strip():
            collection.add(
                documents=[content[:2000]],
                ids=[f"file_{i}"],
                metadatas=[{"path": path}]
            )
        print(f"  Indexed {i+1}/30: {path}")
    print("\n✅ Repo indexed! You can now ask questions.\n")

def ask_question(question):
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
    return response.choices[0].message.content

repo_url = input("Paste a GitHub repo URL: ")
index_repo(repo_url)

while True:
    question = input("Ask a question (or type 'exit'): ")
    if question.lower() == "exit":
        break
    print("\n🤖 Answer:")
    print(ask_question(question))
    print()