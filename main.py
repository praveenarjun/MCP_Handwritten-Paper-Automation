import os
import logging
import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Import Agents
from agents.ocr_agent import extract_text
from agents.matcher_agent import match_answer_to_question
from agents.grading_agent import grade_answer
from agents.report_agent import generate_report

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Environment
load_dotenv()

# Initialize MCP Server
mcp = FastMCP("AnswerSheetEvaluator")

@mcp.tool()
def evaluate_answer_sheet(image_path: str, question_paper_text: str, solution_key: str) -> str:
    """
    Evaluates a handwritten answer sheet image against a question paper and solution key.
    
    Args:
        image_path: URL or local path to the answer sheet image.
        question_paper_text: The full text of the question paper.
        solution_key: JSON string or plain text containing the solutions. 
                      If JSON, expected format: {"1a": {"text": "...", "marks": 5}, ...}
                      If plain text, the grading agent will rely on context.
    
    Returns:
        JSON string containing the final evaluation report.
    """
    logger.info(f"Starting evaluation for: {image_path}")
    
    # --- Step 1: OCR ---
    logger.info("Step 1: Running OCR...")
    student_text = extract_text(image_path)
    
    if student_text == "ILLEGIBLE":
         return json.dumps({"error": "Could not read answer sheet."})
    
    logger.info(f"OCR Output: {student_text[:100]}...") # Log first 100 chars

    # --- Step 2 & 3: Match & Grade Loop ---
    # NOTE: In a real complex scenario, we might need to segment the OCR text if it contains multiple answers.
    # For this v1, we assume the OCR text represents a chunk that contains one or more answers, 
    # but the Matcher Agent will try to find the *primary* question it answers or we might need to split it.
    # 
    # To make this robust for a full sheet, we'd ideally splits by "Q1", "Q2" etc.
    # For now, let's assume the user might pass a cropped image or the text acts as a stream.
    # Let's try to match the WHOLE text to a question, or iterate if we had a segmenter.
    #
    # Simplification for V1: Treat the entire OCR text as the "Student Answer" to be matched.
    
    logger.info("Step 2: Matching Answer to Question...")
    match_result = match_answer_to_question(student_text, question_paper_text)
    
    question_id = match_result.get("question_number")
    question_text = match_result.get("question_text")
    
    graded_items = []
    
    if question_id == "UNIDENTIFIED":
        # Create a report item for unidentified content
        graded_items.append({
            "question_number": "UNIDENTIFIED",
            "student_answer": student_text,
            "feedback": "Could not match to any question in the paper.",
            "marks_awarded": 0,
            "max_marks": 0
        })
    else:
        logger.info(f"Matched to Question: {question_id}")
        
        # Parse Solution Key if it's JSON to find specific solution/marks
        solution_text_for_q = solution_key
        max_marks = 10 # Default
        
        try:
            sol_json = json.loads(solution_key)
            if question_id in sol_json:
                solution_text_for_q = sol_json[question_id].get("text", "")
                max_marks = sol_json[question_id].get("marks", 10)
        except:
            # solution_key is likely plain text, pass it all or let agent handle
            pass

        # --- Step 3: Grading ---
        logger.info("Step 3: Grading...")
        grading_result = grade_answer(student_text, solution_text_for_q, max_marks)
        
        graded_items.append({
            "question_number": question_id,
            "question_text": question_text,
            "student_answer": student_text,
            "marks_awarded": grading_result.get("marks_awarded", 0),
            "max_marks": max_marks,
            "feedback": grading_result.get("feedback", "")
        })

    # --- Step 4: Reporting ---
    logger.info("Step 4: Generating Report...")
    final_report = generate_report(graded_items)
    
    return json.dumps(final_report, indent=2)

if __name__ == "__main__":
    mcp.run()
