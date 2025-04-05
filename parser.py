# parser.py
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI
import json
import os
from secret_key import openapi_key

os.environ["OPENAI_API_KEY"] = openapi_key
llm = OpenAI(temperature=0)

extract_prompt = PromptTemplate.from_template("""
Extract the following information from this prompt:
- app_id (example: cfs_mms_ms4_app2)
- metric_type (example: latency, volume)
- duration (example: 15min, 1hr, 2 hours, etc.)

Respond ONLY in JSON format with keys: app_id, metric_type, duration

Prompt: {user_prompt}
""")

extract_chain = LLMChain(prompt=extract_prompt, llm=llm)

def parse_prompt(user_prompt):
    try:
        result = extract_chain.run(user_prompt)
        parsed = json.loads(result)

        # Identify missing fields
        required_keys = ["app_id", "metric_type", "duration"]
        missing = [key for key in required_keys if not parsed.get(key)]

        # Fallback duration default
        if not parsed.get("duration"):
            parsed["duration"] = "1hr"

        parsed["missing"] = missing
        return parsed

    except Exception as e:
        return {
            "app_id": None,
            "metric_type": None,
            "duration": "1hr",
            "missing": ["app_id", "metric_type", "duration"],
            "error": f"Failed to parse: {str(e)}"
        }
