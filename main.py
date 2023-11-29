from openai import OpenAI
import requests
import os
from dotenv import load_dotenv
from github import Github

print('started')

#This code accesses Github and finds the files in the CS61B course repo that contains information about
#partnerships and general logistical information. We can give this information to GPT as part of its role
g = Github("???")
org = g.get_organization('Berkeley-CS61B')
repo = org.get_repo('website-fa23')
about_content = repo.get_contents('about.md').decoded_content.decode('utf-8')
partnership_content = repo.get_contents('materials/guides/partnerships/index.md').decoded_content.decode('utf-8')

load_dotenv()

#sets up necessary variables for accessing the edstem discussion threads
#uses environment variables, so set those up
EDSTEM_TOKEN = os.environ.get('EDSTEM_TOKEN')
WEBHOOK_URL = os.environ.get('TEST_WEBHOOK_URL')
THREAD_URL = "https://edstem.org/us/courses/42700/discussion/"
API_URL = "https://us.edstem.org/api/courses/42700/threads?filter=unresolved"

#gets a json of the threads in our class
def get_data():
    response = requests.get(API_URL, headers={"Authorization": "Bearer " + EDSTEM_TOKEN})
    return response.json()['threads']

#gets rid of some of the html contents
#this part of the code is kind of ass, but I don't know of a smarter solution
def format_content(content):
    content = content[24:]
    content = content.replace('</paragraph>', '\n')
    content = content.replace('<paragraph>', '')
    content = content.replace('<paragraph/>', '\n')
    content = content.replace('</document>', '')
    content = content.replace('<break/>', '\t')
    content = content.replace('<bold>', '')
    content = content.replace('</bold>', '')
    return content

#sets up variables for chatgpt
client = OpenAI()
data = get_data()

#opens a file that we can write to
f= open("output.txt","w+")

#this iterates through and gets all questions that are part of individual posts and tries to answer them:
for i in range(len(data)):
    
    #we are looking for questions that are neither in megathreads or gitbugs.
    #megathreads are hard to answer because I don't understand their formatting yet, but we could answer in the future
    #gitbugs are very hard to answer. This requires us to have an access token to access the student's private repository
    #which I'm not sure how to get. I feel like there is a workaround to this that I dont' know about, otherwise
    #how are we able to clone repos without an access token? But I don't know of how to do it yet. Also it's
    #difficult because every assignment is very different and we don't have a good way of telling gpt which assignment
    #it's answering
    if not data[i]['approved_status'] == 'pending' and not 'Do not delete this template' in data[i]['content'] and not data[i]['is_megathread']:
        
        #we reconstruct the link using the id of the question, and write it to output
        #makes answering the question easier
        link = 'https://edstem.org/us/courses/42700/discussion/' + str(data[i]['id'])
        f.write("Link: %s\n" % link)
        
        
        #format the content roughly to make it look a bit nicer
        content = format_content(str(data[i]['content']))

        #write the content to the output file under the link
        f.write("Question: \n %s\r\n" % content)


        #feed gpt its role, background info and the question created.
        #I wanted to be able to feed gpt not just the partnership content but also the general about content
        #that we found above, but, there's a token limit of 4097 tokens, and inputting both pages of content
        #uses too many tokens. Perhaps in the future if we upgrade our model we'd be able to handle more robust
        #question solving.
        completion = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[{"role": "system", "content": """You are an assistant teacher for UC Berkeley's Data Structures and Algorithms course, answering a student's question. 
                      This is a page from the course website containing specific details about partnerships:\n'"""},
                    {"role": "system", "content": partnership_content},
                     
                     
                    {"role": "user", "content": content}])
        

        f.write("Answer: \n %s\r\n\n\n" % completion.choices[0].message.content)



#here's an extra question I wrote. It tests explicitly a situation mentioned in the webpage provided to the AI
#and the output does reflect that, the ai response even includes a valid link to the beacon webpage where we handle
#dissolutions.
content = 'My partner has not been communicating and has basically done 0 work throughout the partnership. I have tried communicating with them but they take a very long time to respond and continue to deflect and dodge responsibility. Is this ground for dissolution of the partnership?'
f.write("Question: \n %s\r\n" % content)
completion = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[{"role": "system", "content": """You are an assistant teacher for UC Berkeley's Data Structures and Algorithms course, answering a student's question. 
                      This is a page from the course website containing specific details about partnerships:\n'"""},
                    {"role": "system", "content": partnership_content},
                     
                     
                    {"role": "user", "content": content}])
        

f.write("Answer: \n %s\r\n\n\n" % completion.choices[0].message.content)

print('done')
