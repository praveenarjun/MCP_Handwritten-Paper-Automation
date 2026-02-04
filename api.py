from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import json
import logging
import tempfile
from typing import List, Optional

# Import Agents and Utils
from agents.ocr_agent import extract_text
from agents.matcher_agent import match_answer_to_question
from agents.grading_agent import grade_answer
from agents.report_agent import generate_report
from utils.pdf_utils import extract_pdf_text, pdf_to_images
from PIL import Image

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Answer Evaluator API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

class EvaluationRequest(BaseModel):
    question_paper_text: str
    solution_key_text: str

@app.post("/api/evaluate")
async def evaluate(
    answer_sheet: UploadFile = File(...),
    question_paper: Optional[UploadFile] = File(None),
    solution_key: Optional[UploadFile] = File(None),
    question_paper_text: Optional[str] = Form(None),
    solution_key_text: Optional[str] = Form(None)
):
    try:
        # 1. Process Answer Sheet
        suffix = os.path.splitext(answer_sheet.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(answer_sheet.file, tmp)
            answer_sheet_path = tmp.name

        answer_sheet_images = []
        if answer_sheet_path.endswith(".pdf"):
            answer_sheet_images = pdf_to_images(answer_sheet_path)
        else:
            answer_sheet_images = [Image.open(answer_sheet_path)]

        # 2. Process QP Text
        final_qp_text = question_paper_text or ""
        if question_paper:
             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_qp:
                shutil.copyfileobj(question_paper.file, tmp_qp)
                final_qp_text = extract_pdf_text(tmp_qp.name)
        
        if not final_qp_text:
            raise HTTPException(status_code=400, detail="Question Paper text or file is required")

        # 3. Process Solution Key
        final_sol_text = solution_key_text or ""
        if solution_key:
             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_sol:
                shutil.copyfileobj(solution_key.file, tmp_sol)
                final_sol_text = extract_pdf_text(tmp_sol.name)
        
        if not final_sol_text:
             raise HTTPException(status_code=400, detail="Solution Key text or file is required")

        # --- ORCHESTRATION ---
        
        # Step 1: OCR
        full_student_text = ""
        for idx, img in enumerate(answer_sheet_images):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                img.save(tmp_img.name)
                page_text = extract_text(tmp_img.name)
                if page_text != "ILLEGIBLE":
                    full_student_text += f"\n--- Page {idx+1} ---\n{page_text}"
        
        if not full_student_text.strip():
             return {"error": "OCR failed to extract text or sheet was illegible."}

        # Step 2: Match
        match_result = match_answer_to_question(full_student_text, final_qp_text)
        
        # Step 3: Grade
        grading_result = {}
        if match_result.get("question_number") != "UNIDENTIFIED":
            # Parse Solution Key logic (simplified from app.py)
            q_id = match_result.get("question_number")
            max_marks = 10
            sol_text_q = final_sol_text
            
            try:
                sol_json = json.loads(final_sol_text)
                if str(q_id) in sol_json:
                     sol_text_q = sol_json[str(q_id)].get("text", final_sol_text)
                     max_marks = sol_json[str(q_id)].get("marks", 10)
                elif q_id in sol_json:
                     sol_text_q = sol_json[q_id].get("text", final_sol_text)
                     max_marks = sol_json[q_id].get("marks", 10)
            except:
                pass

            grading_result = grade_answer(full_student_text, sol_text_q, max_marks)
        else:
            grading_result = {"marks_awarded": 0, "feedback": "Could not identify question."}

        # Step 4: Report
        graded_items = [{
            "question_number": match_result.get("question_number"),
            "question_text": match_result.get("question_text"),
            "student_answer": full_student_text,
            "marks_awarded": grading_result.get("marks_awarded", 0),
            "max_marks": max_marks if 'max_marks' in locals() else 10,
            "feedback": grading_result.get("feedback", "")
        }]
        
        final_report = generate_report(graded_items)
        return final_report

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
