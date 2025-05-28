# from tika import parser
import fitz
from django.conf import settings
# import openai
from google import genai

from .models import Note


# Configure OpenAI API key
# openai.api_key = settings.API_KEY
# Configure Gemini API key
client = genai.Client(api_key="AIzaSyBUKALyuqU2eQh6ptCzdT8w453CLorVFc0")

# Function to get response from OpenAI GPT-3.5 engine 
# def get_gpt_response(promt:str, engine="gpt-3.5-turbo-instruct"):
#     return openai.Completion.create(
#         engine=engine,  # text-davinci-003 Or another GPT-3.5 engine
#         prompt=promt,
#         max_tokens=50  # Maximum tokens in the response
#     )

# Function to get response from OpenAI GPT-3.5 engine 
def get_gpt_response(promt:str, engine="gpt-3.5-turbo-instruct"):
    return client.models.generate_content(
        model="gemini-2.0-flash", contents=promt
    )


def summarize(content):
    response = get_gpt_response(f'''
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
    
# get_question_from_pdf("/home/zishan/Documents/CIA-RDP96-00788R001200060018-5.pdf")

def make_notes(test):
    notes = Note.objects.filter(test=test)
    
    for note in notes:
        note.notes = get_gpt_response(f'''
            A student has failed the following questions. Provide a detailed explanation for each incorrect answer, clarifying the concept and correcting any misunderstandings.
            List of questions:
            {note.questions}
        ''').text
        note.save()