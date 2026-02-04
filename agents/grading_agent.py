import logging
import json
from utils.hf_client import query_hf_inference

logger = logging.getLogger(__name__)

MODEL_URL = "https://router.huggingface.co/hf-inference/models/IQuest-Coder-V1-14B-Instruct"

SYSTEM_PROMPT = """You are a Grading Agent. Your goal is to evaluate a student's answer against a solution key.
Input:
1. Student Answer Text
2. Solution Text
3. Max Marks

Rules:
- Award marks based on correctness of the final answer and steps/method.
- Partial credit is allowed if the method is correct but minor arithmetic errors exist.
- Penalize for wrong formulas, missing units, or incorrect final answers.
- DO NOT hallucinate. Grade only what is visible in the Student Answer.
- Output purely in JSON format with keys: "marks_awarded" (float), "feedback" (string).
- Do not add any markdown formatting or explanation. Just the JSON.

Example Output:
{"marks_awarded": 4.5, "feedback": "Correct formula and substitution. Minor calculation error in final step."}
"""

def grade_answer(student_answer, solution_text, max_marks):
    """
    Grades the student answer against the solution.
    """
    user_message = f"""
    Max Marks: {max_marks}

    Solution Key:
    {solution_text}

    Student Answer:
    {student_answer}
    
    Grade this answer.
    """
    
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 512,
        "temperature": 0.2
    }
    
    try:
        logger.info("Calling Grading Agent...")
        result = query_hf_inference(payload, MODEL_URL)
        
        content = ""
        if isinstance(result, list) and 'generated_text' in result[0]:
             content = result[0]['generated_text']
        elif 'choices' in result:
             content = result['choices'][0]['message']['content']
        else:
             content = str(result)
        
        # Clean up code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content.strip())

    except Exception as e:
        logger.error(f"Grading Agent failed: {e}")
        return {"marks_awarded": 0, "feedback": "Error during grading."}
