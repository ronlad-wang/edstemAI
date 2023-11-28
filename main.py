from openai import OpenAI
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from datetime import timezone
from github import Github
from github import Auth
auth = Auth.Token("access_token")


load_dotenv()

# Create a .env file with your custom tokens/webhooks!
EDSTEM_TOKEN = os.environ.get('EDSTEM_TOKEN')
WEBHOOK_URL = os.environ.get('TEST_WEBHOOK_URL')
THREAD_URL = "https://edstem.org/us/courses/42700/discussion/"
API_URL = "https://us.edstem.org/api/courses/42700/threads?filter=unresolved"

def get_data():
    response = requests.get(API_URL, headers={"Authorization": "Bearer " + EDSTEM_TOKEN})
    return response.json()['threads']

def format_content(content):
    content = content.replace('</paragraph>', '\n')
    content = content.replace('<paragraph>', '')
    content = content.replace('<paragraph/>', '\n')
    content = content.replace('</document>', '')
    content = content.replace('<break/>', '\t')
    content = content.replace('<bold>', '')
    content = content.replace('</bold>', '')
    return content

client = OpenAI()
data = get_data()

f= open("output.txt","w+")


#this iterates through and gets all questions that are part of individual posts and tries to answer them:
for i in range(len(data)):
    if not data[i]['approved_status'] == 'pending' and not 'Do not delete this template' in data[i]['content'] and not data[i]['is_megathread']:
        print(data[i]['approved_status'])
        link = 'https://edstem.org/us/courses/42700/discussion/' + str(data[i]['id'])
        f.write("Link: %s\n" % link)
        

        content = data[i]['content'][24:]
        content = format_content(str(data[i]))

        f.write("Question: \n %s\r\n" % content)

        logistics_information = "yar har"

        # completion = client.chat.completions.create(
        #   model="gpt-3.5-turbo",
        #   messages=[{"role": "system", "content": """You are an assistant teacher for UC Berkeley's Data Structures and Algorithms course, answering a student's question. 
        #     As an assistant teacher you do not know how to answer logistical questions. If you don't know how to answer a question, respond 'I don't know how to answer that question'."""},
        #     {"role": "user", "content": content}])
        

        # f.write("Answer: \n %s\r\n\n\n" % completion.choices[0].message.content)



print('done')
