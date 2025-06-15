# 🚀 RAG ChaiCode Docs Assistant

A simple Retrieval-Augmented Generation (RAG) app to query ChaiCode Docs using Gemini LLM and Pinecone.

---

## 🛠️ Setup Instructions

### 1. Create & activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate    # For Linux / MacOS
# OR
.venv\Scripts\activate       # For Windows
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Setup environment variables

- Copy the example environment file:

```bash
cp .env.sample .env
```

- Open `.env` and fill in your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

---

### 4. Run the app

```bash
python main.py
```

---

## ✅ What this does:
- Loads ChaiCode Docs
- Generates & stores embeddings in Pinecone (only once)
- Lets you ask questions to Gemini LLM based on document chunks 🎯

---

### 💡 Notes:
- Make sure you have valid API keys from **Google Gemini** and **Pinecone**.
