import logging
import base64
import requests
from io import BytesIO
from utils.hf_client import query_hf_inference

logger = logging.getLogger(__name__)

# Model URLs
PRIMARY_MODEL_URL = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-VL-7B-Instruct"
BACKUP_MODEL_URL = "https://router.huggingface.co/hf-inference/models/OpenGVLab/InternVL2-8B"

SYSTEM_PROMPT = "Extract all visible handwritten text and equations exactly as written. Do not solve or explain."

def _encode_image(image_path_or_url):
    """
    Encodes an image to base64. Supports local paths and URLs.
    """
    try:
        if image_path_or_url.startswith("http"):
            response = requests.get(image_path_or_url)
            response.raise_for_status()
            image_data = response.content
        else:
            with open(image_path_or_url, "rb") as image_file:
                image_data = image_file.read()
        
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encode image: {e}")
        raise

def extract_text(image_path):
    """
    Extracts text from an image using Primary OCR model, falling back to Backup if it fails.
    """
    base64_image = _encode_image(image_path)
    
    # Payload structure for VL models often involves specific prompting or image inputs
    # Adjusting payload for Qwen2.5-VL / InternVL2 standards on HF Inference API
    # Standard Chat Completion format with image content
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                },
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT
                }
            ]
        }
    ]
    
    payload = {
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.1 # Low temperature for faithful transcription
    }

    try:
        logger.info(f"Attempting OCR with Primary Model: {PRIMARY_MODEL_URL}")
        result = query_hf_inference(payload, PRIMARY_MODEL_URL)
        # Hugging Face Chat API usually returns: 
        # {'choices': [{'message': {'content': '...'}}]} or similar
        # But raw inference API for some VL models might differ. 
        # Assuming OpenAI-compatible or HF standard output.
        # Let's handle the list return which is common for HF inference (generated_text)
        # if it returns a list of dicts, or the choices format.
        
        if isinstance(result, list) and 'generated_text' in result[0]:
             return result[0]['generated_text']
        elif 'choices' in result:
             return result['choices'][0]['message']['content']
        else:
             # Fallback parsing
             return str(result)
             
    except Exception as e:
        logger.warning(f"Primary OCR failed: {e}. Switching to Backup Model.")
        try:
             # InternVL2 uses similar structure usually, but let's retry
             result = query_hf_inference(payload, BACKUP_MODEL_URL)
             
             if isinstance(result, list) and 'generated_text' in result[0]:
                 return result[0]['generated_text']
             elif 'choices' in result:
                 return result['choices'][0]['message']['content']
             else:
                 return str(result)
        except Exception as e2:
             logger.error(f"Backup OCR also failed: {e2}")
             return "ILLEGIBLE"
