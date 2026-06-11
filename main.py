import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

# Load environment variables from .env file (force override for new Gemini key)
load_dotenv(override=True)

# 1. Initialize FastAPI App
app = FastAPI(title="AI Notes Summarizer Backend")

# 2. Setup Gemini LLM (Ensure you have GEMINI_API_KEY in your environment variables)
# We use gemini-2.5-flash as it is fast, highly capable, and has a generous free tier.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

# 3. Define Pydantic Models for structured API responses
class SummaryResponse(BaseModel):
    summary: str
    key_takeaways: list[str]

class QuizItem(BaseModel):
    question: str
    options: list[str]
    correct_answer: str

class QuizResponse(BaseModel):
    quiz: list[QuizItem]


# ------------------------------------------------------------------------
# ENDPOINT 1: Extract Text and Generate Summary & Key Takeaways
# ------------------------------------------------------------------------
@app.post("/process-pdf", response_model=SummaryResponse)
async def process_pdf(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Read the uploaded PDF file bytes
        pdf_bytes = await file.read()
        
        # Load bytes into PyPDF2 Reader
        from io import BytesIO
        reader = PdfReader(BytesIO(pdf_bytes))
        
        # Extract text from all pages
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="The PDF appears to be empty or unscannable.")
            
        # LangChain Summary Prompt Template
        summary_template = """
        You are an expert academic educator. Analyze the following extracted text from lecture notes/documents.
        Provide a concise summary of the content and a list of structured key takeaways.
        
        Format your response strictly as a JSON object with two keys:
        "summary": "A detailed paragraph summarizing the core concepts."
        "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"]

        Text: {text}
        """
        
        # Set up a structured JSON output parser
        parser = JsonOutputParser(pydantic_object=SummaryResponse)
        
        prompt = PromptTemplate(
            template=summary_template,
            input_variables=["text"]
        )
        
        # Chain composition: Prompt -> LLM -> JSON Parser
        chain = prompt | llm | parser
        
        # Run the chain
        result = chain.invoke({"text": extracted_text[:12000]}) # Truncated to avoid huge token costs
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------------------
# ENDPOINT 2: Generate Interactive Flashcards / Quiz Questions
# ------------------------------------------------------------------------
@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(payload: SummaryResponse):
    try:
        # Use the summary and takeaways to generate contextually accurate MCQs
        context = f"Summary: {payload.summary}\nTakeaways: {', '.join(payload.key_takeaways)}"
        
        quiz_template = """
        Based on the following educational context, generate a diverse set of 3 Multiple Choice Questions (MCQs).
        Each question must have exactly 4 options and state the correct answer clearly.
        
        Format your response strictly as a JSON object matching this structure:
        {{
            "quiz": [
                {{
                    "question": "The question string here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "The exact matching correct option string"
                }}
            ]
        }}

        Context: {context}
        """
        
        parser = JsonOutputParser(pydantic_object=QuizResponse)
        prompt = PromptTemplate(template=quiz_template, input_variables=["context"])
        
        chain = prompt | llm | parser
        result = chain.invoke({"context": context})
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))