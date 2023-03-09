import requests
import time
import pandas as pd
import json
import argparse

parser = argparse.ArgumentParser(description='Script to retrieve issues data for GitHub repositories')
parser.add_argument('--filePath', '-f', type=str, help='Path to the CSV file containing the list of repositories')
parser.add_argument('--restToken', '-r', type=str, default="",
                    help='The GitHub Rest API token, needed to improve query rate limit')
parser.add_argument('--graphQLToken', '-g', type=str,default="",
                    help='The GitHub GraphQL API token, needed to improve query rate limit')

def getQuery(userName, reposName, issueNumber):
    '''
    This function returns a GraphQL query that  retrieves information 
    about a GitHub issue given the issue number, repository name, and repository owner.
    '''
    return f'''
    query {{
        repository(owner: "{userName}", name: "{reposName}") {{
            issue(number: {issueNumber}) {{
                title
                url
                createdAt
                author {{
                    login
                }}
                closed
                body
                labels(first: 10) {{
                    edges {{
                        node {{
                            name
                        }}
                    }}
                }}
                comments(first: 100) {{
                    edges {{
                        node {{
                            author {{
                                login
                            }}
                            body
                        }}
                    }}
                }}
            }}
        }}
    }}
    '''


def issuesRetrieval(userName, reposName, lastIssueNum, graphQLToken):
    '''
    This function uses the getQuery() function to retrieve information about all the issues
    in the given repository, starting from the first issue up to and including the last issue.
    '''
    currentIssueNum = 0
    graphQLHeader = {
        'Authorization': f'Bearer {graphQLToken}'
    }

    graphQLurl = 'https://api.github.com/graphql'
    issuesList = []
    while currentIssueNum <= int(lastIssueNum):
        # Retrieve the GraphQL query for the current issue
        query = getQuery(userName, reposName, currentIssueNum)
        # Post the query to the GitHub API
        response = requests.post(
            graphQLurl, json={'query': query}, headers=graphQLHeader)
        try:
            if response.status_code == 200:
                # Parse the JSON data
                data = json.loads(response.text)
                # Check for errors in the response data
                if 'errors' in data or data is None or data['data'] is None or data['data']['repository'] is None or data['data']['repository']['issue'] is None:
                    if 'errors' in data:
                        print(
                            f'App {userName}/{reposName} Error at {currentIssueNum}: ' + str(data['errors'][0]['type']))
                        if str(data['errors'][0]['type']) == 'RATE_LIMITED':
                            print("write to .csv file")
                            df = pd.DataFrame(issuesList, columns=['App Name', 'Issue Title', 'Issue Link', 'Date Created', 'User Created',
                                                                   'Status', 'labels', 'Description', 'Comments', 'Images In Description',
                                                                   'Images In Comments', 'Total Images', 'Total Participants'])
                            df.to_csv(f'{reposName} issues.csv', index=False)
                            time.sleep(3600)
                        elif str(data['errors'][0]['type']) != 'NOT_FOUND':
                            print(
                                f"App {userName}/{reposName} Issue #{currentIssueNum} does not exist")
                        else:
                            currentIssueNum += 1
                            continue

                else:
                    # Extract the issue data from the response
                    issueData = data['data']['repository']['issue']

                    # Extract the data fields from the issue
                    appName = str(reposName)
                    issueTitle = issueData['title']
                    issueLink = issueData['url']
                    dateCreated = issueData['createdAt']
                    if issueData['author'] is None:
                        userCreated = "Unknown"
                    else:
                        userCreated = issueData['author']['login']
                    status = 'Closed' if issueData['closed'] else 'Open'
                    description = [issueData['body']]

                    comments = issueData['comments']['edges']
                    imagesInDescription = description.count(
                        '.png') + description.count('.jpg') + description.count('.jpeg')
                    imagesInComments = sum(comment['node']['body'].count('.png') + comment['node']['body'].count(
                        '.jpg') + comment['node']['body'].count('.jpeg') for comment in comments)
                    totalImages = imagesInDescription + imagesInComments
                    participantNumber = set()

                    labels = []
                    if issueData['labels'] is not None and issueData['labels']['edges'] is not None:
                        for label in issueData['labels']['edges']:
                            if label['node'] is None or label['node']['name'] is None:
                                continue
                            labels.append(str(label['node']['name']))

                    # check if there is existing comment(s) for the issue
                    for comment in comments:
                        if comment is None or comment['node'] is None or comment['node']['author'] is None or comment['node']['author']['login'] is None:
                            continue
                        else:
                            participantNumber.add(
                                comment['node']['author']['login'])
                    totalParticipants = 1 + len(participantNumber)

                    # Append all the info to list
                    issuesList.append((appName, issueTitle, issueLink, dateCreated, userCreated, status, labels, description,
                                      comments, imagesInDescription, imagesInComments, totalImages, totalParticipants))
            # error 403 means that the rate limit is exceeded, need to sleep for an hour
            elif response.status_code == 403 or response.status_code == 429:
                print(
                    f"App {userName}/{reposName} error at issue: {currentIssueNum}")
                print("status code is: " + str(response.status_code) +
                      'rate limit exceeded or too many requests')
                print(f'total issues that have collected {len(issuesList)}')

                print("write to .csv file")
                df = pd.DataFrame(issuesList, columns=['App Name', 'Issue Title', 'Issue Link', 'Date Created', 'User Created',
                                                       'Status', 'labels', 'Description', 'Comments', 'Images In Description',
                                                       'Images In Comments', 'Total Images', 'Total Participants'])
                df.to_csv(f'{reposName} issues.csv', index=False)

                time.sleep(3600)
                currentIssueNum += 1
                continue
            else:
                print(
                    f"App {userName}/{reposName} error at issue: {currentIssueNum}")
                print("status code is: " + str(response.status_code))
                currentIssueNum += 1
                continue
            currentIssueNum += 1
        except Exception:
            df = pd.DataFrame(issuesList, columns=['App Name', 'Issue Title', 'Issue Link', 'Date Created', 'User Created',
                                                   'Status', 'labels', 'Description', 'Comments', 'Images In Description',
                                                   'Images In Comments', 'Total Images', 'Total Participants'])
            df.to_csv(f'{reposName} issues.csv', index=False)

            # log file to check special errors
            issueLogFile = open(f'log/issues_log_{reposName}.txt', 'a')
            issueLogFile.write(f'Error at issues: {currentIssueNum} \n')
            currentIssueNum += 1
            continue

    # Write the final state of issuesList to a CSV file
    df = pd.DataFrame(issuesList, columns=['App Name', 'Issue Title', 'Issue Link', 'Date Created', 'User Created',
                                           'Status', 'labels', 'Description', 'Comments', 'Images In Description',
                                           'Images In Comments', 'Total Images', 'Total Participants'])
    df.to_csv(f'{reposName} issues.csv', index=False)


if __name__ == '__main__':
    args = parser.parse_args()
    appDf = pd.read_csv(args.filePath)
    for row in appDf.iterrows():
        idx = row[0]
        userAndReposName = appDf.iloc[idx]['html_url_clean']
        end = userAndReposName.rfind('/')
        userName = userAndReposName[:end]
        reposName = userAndReposName[end+1:]

        restHeader = {"Authorization": 'token ' +
                      f"{args.restToken}"}

        restUrl = f'https://api.github.com/repos/{userName}/{reposName}/issues'

        restResponse = requests.get(restUrl, headers=restHeader)
        try:
            if restResponse.status_code == 200:
                lastIssueNumUrl = restResponse.json()[0]['url']
                lastIssueNum = lastIssueNumUrl[lastIssueNumUrl.rfind('/') + 1:]
                issuesRetrieval(userName, reposName, lastIssueNum, args.graphQLToken)
            else:
                print( f'Error at {userName}/{reposName} with status: {restResponse.status_code}')
                appLogFile = open('log/app_log_{reposName}.txt', 'a')
                appLogFile.write(f'Error at app: {userName}/{reposName} with status: {restResponse.status_code}\n')
                appLogFile = open('log/app_log_{reposName}.txt', 'a').close()
                continue
        except Exception as e:
            appLogFile = open('log/app_log_{reposName}.txt', 'a')
            print(f'Error at app: {userName}/{reposName} with exception: {e}')
            appLogFile.write(f'Error at app: {userName}/{reposName} with exception: {e} \n')
            appLogFile.close()
            continue
