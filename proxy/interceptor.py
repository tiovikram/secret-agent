import json
import logging
import openai

logger = logging.getLogger(__name__)

class Interceptor:

    def __init__(self):
        self.model_url = "http://localhost:8000/v1"
        self.request_store = {}
        self.client = openai.OpenAI(
            base_url=self.model_url,
            api_key="sk-no-key-required",
        )

    def request(self, flow):
        self.request_store[flow.request.host] = flow.request.content
        flow.request.set_text(json.dumps({"Hello": "Eden"}))

addons = [Interceptor()]
