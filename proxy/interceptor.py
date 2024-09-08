import json
import logging
import os

import dotenv
import groq
import openai 
from pii import DEFAULT_PII_TYPES, generate_system_prompt

dotenv.load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
print(GROQ_API_KEY)

logger = logging.getLogger(__name__)

class Interceptor:

    def __init__(self):
        self.model_url = "http://localhost:8000/v1"
        self.client = openai.OpenAI(
                base_url=self.model_url,
                api_key="sk-no-key-required",
            )
        self.groq_client = groq.Groq(
            api_key=GROQ_API_KEY
        )
        self.request_store = {}
    
    def request(self, flow):
        content_type = flow.request.headers.get('Content-Type', "text/plain")
        request_content = json.dumps(flow.request.json()) if content_type == "application/json" else flow.request.text
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": generate_system_prompt(DEFAULT_PII_TYPES, content_type),
                },
                {
                    "role": "user",
                    "content": request_content,
                },
            ],
            model="llama-3.1-8b-instant"
        )
        self.request_store[flow.request.host] = flow.request.content
        flow.request.headers["Origin"] = "http://localhost:8080"
        obscured_body = chat_completion.choices[0].message.content

        # Ensure proper JSON output
        if content_type == "application/json":
            try:
                # Parse the LLM output as JSON
                json_body = json.loads(obscured_body)
                # Re-serialize to ensure proper formatting
                obscured_body = json.dumps(json_body)
            except json.JSONDecodeError:
                logger.error("LLM output is not valid JSON. Falling back to original request.")
                obscured_body = request_content

        flow.request.set_text(obscured_body)
        logger.info(obscured_body)

    def response(self, flow):
        flow.response.headers["Access-Control-Allow-Origin"] = "*"

addons = [Interceptor()]
