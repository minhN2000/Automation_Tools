import requests
import json
import argparse
import pandas as pd


parser = argparse.ArgumentParser(description='Script to retrieve repositories data from GitHub')
parser.add_argument('--query','-q', type=str, help='Query for searching repositories in GitHub')
parser.add_argument('--start','-s', type=int,
                    help='The lower bound stars to get apps have greater stars than start')
parser.add_argument('--end','-e', type=int,
                    help='The upper bound stars to get apps have smaller stars than start')
def getQuery():
    '''
    This function returns a GraphQL query that  retrieves information 
    about GitHub repositories.
    '''
    return '''
    query SearchRepositories($query: String!, $after: String) {
        search(query: $query, type: REPOSITORY, first: 100, after: $after) {
        pageInfo {
            endCursor
            hasNextPage
        }
        edges {
            node {
            ... on Repository {
                name
                description
                stargazers {
                totalCount
                }
                url
            }
            }
        }
        }
    }
    '''

def gitHubAppRetrieval(q, start, end):
    args = parser.parse_args()

    # Set up the Github API endpoint and headers
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'Bearer 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', 'Content-Type': 'application/json'}

    query = getQuery()
    variables = {'query': f'{args.query} stars:{args.start}..{args.end}', 'after': None}

    # Make requests until all pages of results are retrieved
    repositories = []
    while True:
        # Send the GraphQL request
        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
        response.raise_for_status()

        # Parse the response as JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"Error decoding response: {e}")
            break

        # Check for errors in the response
        if 'errors' in data:
            print(f"Error in response: {data['errors'][0]['message']}")
            break

        # Append the repositories to the list
        try:
            repositories += [edge['node'] for edge in data['data']['search']['edges']]
        except KeyError as e:
            print(f"Error parsing response: {e}")
            break

        # Check if there are more pages of results
        if data['data']['search']['pageInfo']['hasNextPage']:
            variables['after'] = data['data']['search']['pageInfo']['endCursor']
        else:
            break
        
        # the maximum repos you can retrieve is 1000, after that it will repeatly get the old repos
        if(len(repositories) >= 1000):
            break

    import pandas as pd
    lst = list()
    for r in repositories:
        lst.append((r['name'],r['description'], r['stargazers']['totalCount'], r['url']))

    # save the repositories data into .csv file
    pd.DataFrame(data=lst, columns=['name','description','stargazers_count','html_url']).to_csv(f'output/{args.query}/{args.start}_{args.end}.csv', index=False)
