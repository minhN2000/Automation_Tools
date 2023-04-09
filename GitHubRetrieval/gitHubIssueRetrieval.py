import requests
import time
import pandas as pd
import json
import argparse
import re
parser = argparse.ArgumentParser(description='Script to retrieve issues data for GitHub repositories')
parser.add_argument('--filePath', '-f', type=str, help='Path to the CSV file containing the list of repositories')
parser.add_argument('--restToken', '-r', type=str, default="",
                    help='The GitHub Rest API token, needed to improve query rate limit')
parser.add_argument('--graphQLToken', '-g', type=str,default="",
                    help='The GitHub GraphQL API token, needed to improve query rate limit')

def getQuery(userName, reposName, issueNum):
    '''
    This function returns a GraphQL query that  retrieves information 
    about a GitHub issue given the issue number, repository name, and repository owner.
    '''
    return f'''
    query {{
        repository(owner: "{userName}", name: "{reposName}") {{
            issue(number: {issueNum}) {{
                participants {{
                    totalCount
                }}
                title
                url
                createdAt
                author {{
                    login
                }}
                body
                closed
                labels(first: 10) {{
                    edges {{
                        node {{
                            name
                        }}
                    }}
                }}
                comments(first: 30) {{
                    edges {{
                        node {{
                            body
                        }}
                    }}
                }}
            }}
        }}
    }}
    '''

def toTXT(reposName, issueNum, issueTitle, description, cleanedComments):
    '''
    This function convert the original issue to a simple version that is easy to read
    '''
    file = open(f'./recdroid_issues/appID_{reposName}_issueID_{issueNum}.txt', 'w')
    temp_str = ("######Title##########\n")
    temp_str += (issueTitle)
    temp_str += ("\n######End Title##########\n")
    temp_str += ("\n######Description##########\n")
    temp_str += (description)
    temp_str += ("\n######End Description##########\n")
    temp_str += cleanedComments
    temp_str = re.sub(r'\n\s*\n', '\n', temp_str)
    file.write(temp_str)
    file.close()


def __getIssueInfo(issueUrl):
    cleanUrl = issueUrl.replace('https://github.com/','')
    infoList = cleanUrl.split('/')
    userName, reposName, issueNum = infoList[0], infoList[1], infoList[3]
    return userName, reposName, issueNum

def issuesRetrieval(issueUrl, issuesList):
    '''
    This function uses the getQuery() function to retrieve information about all the issues
    in the given repository, starting from the first issue up to and including the last issue.
    '''
    if 'github.com' not in issueUrl:
        log_file = open('Recdoid_log.txt', 'a')
        error_str = f'{issueUrl} not from github\n'
        print(error_str)
        log_file.write(error_str)
        log_file.close()
        return
    graphQLurl = 'https://api.github.com/graphql'
    graphQLToken = 'YOUR_TOKEN_HERE'
    graphQLHeader = {
            'Authorization': f'Bearer {graphQLToken}'
        }

    userName, reposName, issueNum = __getIssueInfo(issueUrl)

    q = getQuery(userName, reposName, issueNum)
    response = requests.post(graphQLurl, json={'query': q}, headers=graphQLHeader)

    # try:
    data = json.loads(response.text)
    issueData = data['data']['repository']['issue']
    issueTitle = issueData['title']
    issueLink = issueData['url']
    dateCreated = issueData['createdAt']
    if issueData['author'] is None:
                    userCreated = "Unknown"
    else:
        userCreated = issueData['author']['login']
    status = 'Closed' if issueData['closed'] else 'Open'
    comments = issueData['comments']['edges']
    description = str(issueData['body'])
    imagesInDescription = description.count(
                    '.png') + description.count('.jpg') + description.count('.jpeg')
    imagesInComments = sum(comment['node']['body'].count('.png') + comment['node']['body'].count(
        '.jpg') + comment['node']['body'].count('.jpeg') for comment in comments)
    totalImages = imagesInDescription + imagesInComments
    participantNumber = issueData['participants']['totalCount']

    labels = []
    if issueData['labels'] is not None and issueData['labels']['edges'] is not None:
        for label in issueData['labels']['edges']:
            if label['node'] is None or label['node']['name'] is None:
                continue
            labels.append(str(label['node']['name']))
    
    cleanedComments = ''
    for i, comment in enumerate(comments):
        if comment is None or comment['node'] is None or comment['node']['body'] is None:
            continue
        else:
            cleanedComments += (f"######Comment {i}##########\n")
            cleanedComments += (str(comment['node']['body']))
    cleanedComments += (f"\n######End comments##########\n")

    totalParticipants = participantNumber

    print(f'total participant: {totalParticipants}')
    issuesList.append((reposName, issueNum, issueTitle, issueLink, dateCreated, userCreated, status, labels, description,
                        cleanedComments, imagesInDescription, imagesInComments, totalImages, totalParticipants))

    toTXT(reposName, issueNum, issueTitle, description, cleanedComments)
