# 📚 AI Notes Summarizer & Quiz Generator

An interactive, AI-powered web application that helps students and educators turn lecture PDFs into detailed study guides, key takeaways, and flashcard-style interactive assessment quizzes. Built with **FastAPI**, **Streamlit**, and **LangChain** powered by Google's **Gemini 2.5 Flash**.

---

## 🚀 Features

- **PDF Text Extraction**: Extracts text content automatically from uploaded PDF lecture notes/slides.
- **AI Summary & Key Takeaways**: Generates structured, educational summaries and key conceptual takeaways from the document.
- **Interactive Assessment Quizzes**: Generates diverse multiple-choice questions (MCQs) dynamically based on the notes' contents with real-time answer verification.
- **Downloadable Study Guides**: Allows compiling and downloading generated summaries/takeaways into a `.txt` study guide.
- **Free API Tier**: Utilizes Google's Gemini API free tier.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **AI Integration**: LangChain & LangChain Google GenAI (`gemini-2.5-flash`)
- **PDF Processing**: PyPDF2

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-notes-generator.git
cd ai-notes-generator
```

### 2. Configure Environment Variables
Create a `.env` file in the root of the project:
```env
GEMINI_API_KEY="your-free-gemini-api-key"
```
*(Get a free key from [Google AI Studio](https://aistudio.google.com).)*

### 3. Install Dependencies
Initialize and activate your virtual environment, then install requirements:
```bash
# Initialize venv (if not already done)
python3 -m venv .venv

# Activate venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## 🏃 Running the Application

This project runs as two separate services: a FastAPI backend and a Streamlit frontend.

### Step 1: Start the FastAPI Backend
With your virtual environment activated, run:
```bash
uvicorn main:app --reload
```
The API documentation will be available at `http://127.0.0.1:8000/docs`.

### Step 2: Start the Streamlit Frontend
In a new terminal window (with the virtual environment activated), run:
```bash
streamlit run app.py
```
The web dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```text
├── .venv/                  # Python Virtual Environment
├── .gitignore              # Git ignored files (.env, .venv, etc.)
├── .env                    # Local environment variables (API keys)
├── requirements.txt        # Python package dependencies
├── main.py                 # FastAPI Backend Server & AI chain logic
├── app.py                  # Streamlit Frontend application
└── README.md               # Project documentation
```
