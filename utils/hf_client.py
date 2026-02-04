import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_hf_inference(payload, model_url):
    """
    Sends a request to the Hugging Face Inference API.
    """
    if not HF_TOKEN:
         raise ValueError("HF_TOKEN environment variable is not set.")

    try:
        response = requests.post(model_url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        try:
             # Try to log detailed error from HF
             logger.error(f"Response content: {response.text}")
        except:
             pass
        raise
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise
