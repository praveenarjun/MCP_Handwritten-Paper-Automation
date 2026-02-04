import logging
import json
from utils.hf_client import query_hf_inference

logger = logging.getLogger(__name__)

MODEL_URL = "https://router.huggingface.co/hf-inference/models/IQuest-Coder-V1-14B-Instruct"

SYSTEM_PROMPT = """You are a Matcher Agent. Your goal is to identify which question from the Question Paper corresponds to the Student's Answer.
Input:
1. Student Answer Text (OCR output)
2. Question Paper Text

Rules:
- Match based on content similarity, keywords, and identifiable question numbers/parts (e.g., "1a", "Q3").
- NEVER invent a question number.
- If the answer text does not clearly match any question, return "UNIDENTIFIED".
- Output purely in JSON format with keys: "question_number", "question_text".
- Do not add any markdown formatting or explanation. Just the JSON.

Example Output:
{"question_number": "2a", "question_text": "Calculate the velocity..."}
OR
{"question_number": "UNIDENTIFIED", "question_text": ""}
"""

def match_answer_to_question(student_text, question_paper_text):
    """
    Identifies the question corresponding to the student's answer text.
    """
    user_message = f"""
    Question Paper:
    {question_paper_text}

    Student Answer:
    {student_text}
    
    Identify the question number and text.
    """
    
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 512,
        "temperature": 0.1
    }
    
    try:
        logger.info("Calling Matcher Agent...")
        result = query_hf_inference(payload, MODEL_URL)
        
        content = ""
        if isinstance(result, list) and 'generated_text' in result[0]:
             content = result[0]['generated_text']
        elif 'choices' in result:
             content = result['choices'][0]['message']['content']
        else:
             content = str(result)
        
        # Clean up code blocks if present (some models insist on markdown)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        return json.loads(content.strip())

    except Exception as e:
        logger.error(f"Matcher Agent failed: {e}")
        return {"question_number": "UNIDENTIFIED", "question_text": ""}
