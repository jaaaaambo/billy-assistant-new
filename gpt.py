import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты ассистент-диспетчер задач. Отвечай понятно, помогай организовывать мысли, задачи, дедлайны."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']
