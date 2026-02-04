import json
import logging

logger = logging.getLogger(__name__)

def generate_report(graded_answers):
    """
    Aggregates graded answers into a final report.
    
    Args:
        graded_answers (list): List of dicts containing:
            - question_number
            - question_text
            - student_answer
            - marks_awarded
            - max_marks
            - feedback
            
    Returns:
        dict: Final evaluation report with total marks.
    """
    total_marks_awarded = 0
    total_max_marks = 0
    
    detailed_results = []
    
    for item in graded_answers:
        marks = item.get("marks_awarded", 0)
        # Ensure marks are numeric
        if isinstance(marks, str):
            try:
                marks = float(marks)
            except:
                marks = 0
                
        max_m = item.get("max_marks", 0)
        
        total_marks_awarded += marks
        total_max_marks += max_m
        
        detailed_results.append({
            "question_number": item.get("question_number", "UNKNOWN"),
            "question_text": item.get("question_text", ""),
            "student_response": item.get("student_answer", ""),
            "marks_awarded": marks,
            "max_marks": max_m,
            "feedback": item.get("feedback", "")
        })
        
    report = {
        "summary": {
            "total_marks_obtained": total_marks_awarded,
            "total_possible_marks": total_max_marks,
            "percentage": (total_marks_awarded / total_max_marks * 100) if total_max_marks > 0 else 0
        },
        "details": detailed_results
    }
    
    return report
