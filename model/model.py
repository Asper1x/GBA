from dotenv import load_dotenv
from openai import OpenAI


class Client:
    def __init__(self) -> None:
        load_dotenv()
        self.client = OpenAI()
    
    def response(self, text):
        response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": text}
        ]
        )
        return response.choices[0].message.content