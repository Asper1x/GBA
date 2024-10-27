import os
from dotenv import load_dotenv
from openai import OpenAI

class Client:
    def __init__(self) -> None:
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def response(self, text, user_data=""):

        full_prompt = f"{user_data}\n{text}" if user_data else text

        response = self.client.completions.create(
            model="davinci-002",
            prompt=full_prompt,  
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].text.strip() 

