import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv(override=True)
app = FastAPI(title="AI Notes Summarizer Backend")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

class SummaryResponse(BaseModel):

    summary: str
    key_takeaways: list[str]

class QuizItem(BaseModel):

    question: str
    options: list[str]
    correct_answer: str

class QuizResponse(BaseModel):

    quiz: list[QuizItem]

@app.post("/process-pdf", response_model=SummaryResponse)
async def process_pdf(file: UploadFile = File(...)):

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        pdf_bytes = await file.read()
        from io import BytesIO
        reader = PdfReader(BytesIO(pdf_bytes))
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="The PDF appears to be empty or unscannable.")
        summary_template = """
        You are an expert academic educator. Analyze the following extracted text from lecture notes/documents.
        Provide a concise summary of the content and a list of structured key takeaways.
        Format your response strictly as a JSON object with two keys:
        "summary": "A detailed paragraph summarizing the core concepts."
        "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"]
        Text: {text}
        """
        parser = JsonOutputParser(pydantic_object=SummaryResponse)
        prompt = PromptTemplate(
            template=summary_template,
            input_variables=["text"]
        )
        chain = prompt | llm | parser
        result = chain.invoke({"text": extracted_text[:12000]})
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/generate-quiz", response_model=QuizResponse)

async def generate_quiz(payload: SummaryResponse):

    try:
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
