import json
import logging
import openai
import argparse
from pii import generate_system_prompt, DEFAULT_PII_TYPES
from groq import Groq

logger = logging.getLogger(__name__)

class Interceptor:

    def __init__(self, use_local_llm=True):
        self.model_url = "http://localhost:8000/v1"
        self.request_store = {}
        self.use_local_llm = use_local_llm
        if not use_local_llm:
            self.client = Groq()
        else:
            self.client = openai.OpenAI(
                base_url=self.model_url,
                api_key="sk-no-key-required",
            )

    def chat(self, user_input):
        system_prompt = generate_system_prompt(DEFAULT_PII_TYPES)
        print(f"{system_prompt=}")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        if self.use_local_llm:
            completion = self.client.chat.completions.create(
                model="LLaMA_CPP",
                messages=messages
            )
            return completion.choices[0].message.content
        else:
            completion = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            response = ""
            for chunk in completion:
                response += chunk.choices[0].delta.content or ""
            return response
    def request(self, flow):
        self.request_store[flow.request.host] = flow.request.content
        print(f'making call {flow.request.text=}')
        intercept = self.chat("Contact Julia Roberts at 1876 543 7652. Her SSN is 234-56-7829")
        flow.request.set_text(json.dumps({"Hello": f"{intercept=}"}))

    def run_tests(self):
        test_cases = [
            "Contact Julia Roberts at 9876 5432 1098 7654. Her SSN is 234-56-7890.",
            "Reach out to Michael Smith. His phone number is (555) 123-4567 and his credit card number is 5555-5555-5555-5555.",
            "Jane Doe's SSN is 111-22-3333. For further details, you can use the following card: 4111 1111 1111 1111.",
            "Steve Rogers' card details are not to be shared. However, his SSN is 987-65-4321.",
            "Please contact Emily Johnson. Her number is 123-45-6789 and her credit card is 3782 822463 10005."
        ]

        for i, test_input in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"Input: {test_input}")
            result = self.chat(test_input)
            print(f"Output: {result}")
            print("-" * 50)

addons = [Interceptor()]

# Run the tests
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PII detection tests")
    parser.add_argument("--use_local_llm", action="store_true", help="Use local LLaMA model instead of Groq")
    args = parser.parse_args()

    interceptor = Interceptor(use_local_llm=args.use_local_llm)
    interceptor.run_tests()
