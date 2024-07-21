import time
import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google Docs API setup
SCOPES = ['https://www.googleapis.com/auth/documents']

def create_google_docs_service():
    creds = None
    # Token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('docs', 'v1', credentials=creds)

def create_document(service, title):
    body = {
        'title': title
    }
    doc = service.documents().create(body=body).execute()
    print(f'Created document with title: {doc.get("title")} and ID: {doc.get("documentId")}')
    return doc.get('documentId')

def write_to_document(service, document_id, hrefs):
    requests = []
    index = 1  # Starting index for inserting text
    
    for href in hrefs:
        # Insert the href text
        requests.append({
            'insertText': {
                'location': {
                    'index': index,
                },
                'text': href + '\n'
            }
        })
        # Update the text style to make it a hyperlink
        if index!= 1:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': index,
                        'endIndex': index + len(href),
                    },
                    'textStyle': {
                        'link': {
                            'url': href
                        }
                    },
                    'fields': 'link'
                }
            })
        index += len(href) + 1  # Update the index for the next insertion

    result = service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    print(f'Updated document with {len(hrefs)-1} links.')

def get_document_content(service, document_id):
    document = service.documents().get(documentId=document_id).execute()
    content = document.get('body').get('content', [])

    existing_hrefs = []
    for element in content:
        if 'paragraph' in element:
            for run in element['paragraph']['elements']:
                if 'textRun' in run and 'textStyle' in run['textRun'] and 'link' in run['textRun']['textStyle']:
                    existing_hrefs.append(run['textRun']['textStyle']['link']['url'])

    return existing_hrefs