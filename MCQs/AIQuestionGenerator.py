# from tika import parser
import fitz
from django.conf import settings
from .models import Note

import requests

API_KEY = settings.API_KEY

def get_perplexity_response(prompt: str, model="sonar-pro"):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']



def summarize(content):
    response = get_perplexity_response(f'''
        You are given a string variable containing a full chapter you need to impliment principals which make a great MCQ type question and generate 1 good question 
        questions and answers should preferably be under 10 words
        Return the result as a single string that I can split usinag the '|' character in Python.
        your output should strictly follow this following example without any \n (newline characters)
        format =  Question | option A | option B | option C | option D | Correct option                               
        example = what is the color of a chick? | Blue | Green | Yellow | Red | C

        string variable = "{content}"
    ''')

    # return response['choices'][0]['text']
    return response.text


def get_question_from_pdf(file_url):
    # raw = parser.from_file(file_url)
    # summary = summarize(raw['content'])
    doc = fitz.open(file_url)
    text = "\n".join(page.get_text() for page in doc)
    print(text)
    summary = summarize(text)
    summary = summary.split('|')
    print("summary: ", summary)
    return summary
    
def make_notes(test):
    notes = Note.objects.filter(test=test)
    
    for note in notes:
        note.notes = get_perplexity_response(f'''
            A student has failed the following questions. Provide a detailed explanation for each incorrect answer, clarifying the concept and correcting any misunderstandings.
            List of questions:
            {note.questions}
        ''').text
        note.save()