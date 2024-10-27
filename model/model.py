import os
from dotenv import load_dotenv
from openai import OpenAI

class Client:
    def __init__(self) -> None:
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def response(self, text, user_data={}):

        user_data_prompt = ""

        if user_data:
            for key in user_data.keys():
                if key != "_id":
                    user_data_prompt += f"{key}: {user_data[key]} "
            
            full_prompt = f"{text}\n{user_data_prompt}"            
        else:
            full_prompt = f"{text}"


        response = self.client.completions.create(
            model="davinci-002",
            prompt=full_prompt,  
            max_tokens=25,
            temperature=0.2
        )
        print(response.choices)
        return response.choices[0].text.strip() 

