import os
import logging
from typing import List, Dict
from mistralai import Mistral
from dotenv import load_dotenv

MODEL_NAME = "mistral-tiny"

logger = logging.getLogger("roi.llm")
load_dotenv()
if not os.getenv("MISTRAL_API_KEY"):
    logger.warning("MISTRAL_API_KEY is not set. LLM features will be unavailable until you set it in .env or environment.")


class MissingAPIKeyError(RuntimeError):
    pass


def chat(messages: List[Dict[str, str]]) -> str:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise MissingAPIKeyError("MISTRAL_API_KEY is not set. Please add it to a .env file or your environment.")
    client = Mistral(api_key=api_key)
    resp = client.chat.complete(model=MODEL_NAME, messages=messages)
    return resp.choices[0].message.content