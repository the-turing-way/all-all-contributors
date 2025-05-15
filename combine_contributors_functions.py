import requests
import os
from datetime import datetime
import json
from pathlib import Path

# define a function that fetches all contributors files from public repos in a GitHub organization and stores them in a folder 
def fetch_all_contributors(org_name, github_token):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    repos_url = f'https://api.github.com/orgs/{org_name}/repos'
    response = requests.get(repos_url, headers=headers)
    
    if response.status_code != 200:
        print(f'Error fetching repositories: {response.status_code}')
        return
    
    repos = response.json()
    
    # Create a new folder with org_name and current date and time
    folder_name = f"{org_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" # Helpfull note - Creats folder in current running directory
    # For UX, add some customization to the folder name/location
    os.makedirs(folder_name, exist_ok=True)
    
    fileArray = []
    for repo in repos:
        repo_name = repo['name']
        default_branch = repo['default_branch']
        contributors_url = f'https://api.github.com/repos/{org_name}/{repo_name}/contents/.all-contributorsrc?ref={default_branch}'
        response = requests.get(contributors_url, headers=headers)
        
        if response.status_code == 200:
            content = response.json()
            download_url = content["download_url"]
            file_content = requests.get(download_url).text
            print(f'Success! .all-contributorsrc found in {repo_name}: {download_url}')
            
            parsedJSON = json.loads(file_content)
            fileArray.append(parsedJSON)
        else:
            print(f'.all-contributorsrc not found in {repo_name}')
    print(fileArray)
    return fileArray

"""
The below function (combineContributors) is assuming the JSON objects (variables in single-dimension array) in the have the structure 
{
    "projectName": "",
    "projectOwner": "",
    "repoType": "github",
    "repoHost": "https://github.com",
    "files": [
        ""
    ],
    "imageSize": int,
    "commit": boolean (true/false),
    "commitConvention": str (god knows),
    "contributors": [
        {
            "contributions": [
                "testContributor"
            ],
            "login": "contributorUsername",
            "name": "ContributorDisplayName"
        },
        {
        etc.
        }
"""


def combineContributors(folderName):
    print("Please add to this function")