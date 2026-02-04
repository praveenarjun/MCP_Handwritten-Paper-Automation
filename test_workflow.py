import os
import json
import logging
from dotenv import load_dotenv
from agents.ocr_agent import extract_text
from agents.matcher_agent import match_answer_to_question
from agents.grading_agent import grade_answer
from agents.report_agent import generate_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestWorkflow")

# Load env vars
load_dotenv()

def run_test():
    print("--- Starting Manual Verification of Agents ---")
    
    # 1. Test OCR
    # Using a dummy image URL (or you can set a local path)
    # Use a solid placeholder or known online sample if possible.
    # For now, we will mock the OCR output if we don't have a real image, 
    # BUT the agent is designed to call HF. Let's try with a dummy or expect failure/skip.
    
    # Real test requires a real image. 
    # Let's verify the reasoning chain with MOCK OCR Text.
    
    print("\n[Mock Mode] Skipping actual Image OCR (requires real image). Using Mock Text.")
    student_mock_text = "The velocity is calculated as v = d/t. Given d=100m, t=5s, so v = 20 m/s."
    
    # 2. Test Matcher
    print("\n--- Testing Matcher Agent ---")
    question_paper = """
    Q1. Define Force.
    Q2. Calculate the velocity of a car traveling 100m in 5s.
    Q3. What is photosynthesis?
    """
    
    match_result = match_answer_to_question(student_mock_text, question_paper)
    print(f"Match Result: {json.dumps(match_result, indent=2)}")
    
    # 3. Test Grader
    print("\n--- Testing Grading Agent ---")
    solution_key = """
    velocity = distance / time
    v = 100 / 5 = 20 m/s
    """
    max_marks = 5
    
    grading_result = grade_answer(student_mock_text, solution_key, max_marks)
    print(f"Grading Result: {json.dumps(grading_result, indent=2)}")
    
    # 4. Test Report
    print("\n--- Testing Report Agent ---")
    graded_items = [{
        "question_number": match_result.get("question_number"),
        "question_text": match_result.get("question_text"),
        "student_answer": student_mock_text,
        "marks_awarded": grading_result.get("marks_awarded"),
        "max_marks": max_marks,
        "feedback": grading_result.get("feedback")
    }]
    
    report = generate_report(graded_items)
    print(f"Final Report: {json.dumps(report, indent=2)}")

if __name__ == "__main__":
    if not os.getenv("HF_TOKEN"):
        logger.warning("HF_TOKEN not found! Agents might fail.")
    run_test()
