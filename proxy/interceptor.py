import json
import logging
import os

import dotenv
import groq

from pii import DEFAULT_PII_TYPES, generate_system_prompt

dotenv.load_dotenv()

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
print(GROQ_API_KEY)

logger = logging.getLogger(__name__)

class Interceptor:

    def __init__(self):
        self.groq_client = groq.Groq(
            api_key=GROQ_API_KEY
        )
        self.request_store = {}
    
    def request(self, flow):
        content_type = flow.request.headers.get('Content-Type', "text/plain")
        request_content = json.dumps(flow.request.json()) if content_type == "application/json" else flow.request.text
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": generate_system_prompt(DEFAULT_PII_TYPES),
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

        flow.request.set_text(obscured_body)
        logger.info(obscured_body)

    def response(self, flow):
        flow.response.headers["Access-Control-Allow-Origin"] = "*"

addons = [Interceptor()]
