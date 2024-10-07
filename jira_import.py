import json
import requests
import sys
from datetime import datetime

# Jira API information
JIRA_URL = "https://your-domain.atlassian.net/rest/api/3/issue" #use /batch if you'd like to batch create issues in Jira
JIRA_TRANSITION_URL = "https://your-domain.atlassian.net/rest/api/3/issue/{}/transitions"
API_TOKEN = "your_api_token"
EMAIL = "your_email@example.com"

# Set-up Jira headers
headers = {
    "Authorization": "Basic <base64_encoded_credentials>",
    "Content-Type": "application/json"
}

# Create a session with retry logic
session = requests.Session()

# Load YouTrack data from provided JSON file
def load_youtrack_data():
    with open('output.json', 'r') as json_file:
        return json.load(json_file)

youtrack_data = load_youtrack_data()

# Definition of fallback values if needed
FALLBACK_REPORTER_ID = "jira_fallback_reporter_id"
FALLBACK_ASSIGNEE = "Fallback Assignee Name"
FALLBACK_TYPE = "Task"
FALLBACK_PRIORITY = "Medium"

# Priority and issue type mappings from YouTrack to Jira
priority_mapping = {
    "Major": "High",
    "Show-Stopper": "Highest",
    "Critical": "Highest",
    "Normal": "Medium",
    "Minor": "Low"
}

issue_type_mapping = {
    "Bug": "Bug",
    "Chore": "Chore",
    "Task": "Task",
    "Epic": "Epic"
}

# Reporter and assignee mappings
user_mapping = {
    "YouTrack User Name 1": "jira_account_id_1",
    "YouTrack User Name 2": "jira_account_id_2",
    "YouTrack User Name 4": "jira_account_id_4",
    "YouTrack User Name 5": "jira_account_id_5",
    # ...
}

# Create the issue in Jira
def create_issue_in_jira(issue_data):
    response = session.post(JIRA_URL, headers=headers, json=issue_data, verify=False)
    if response.status_code == 201:
        issue_key = response.json()['key']
        print(f"Issue created successfully: {issue_key}")
        return issue_key
    else:
        print(f"Failed to create issue. Status code: {response.status_code}, Response: {response.text}")
        return None

# Add the comments to the created Jira Issue
def add_comments_to_issue(issue_key, comments):
    for comment in comments:
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment['text']
                            }
                        ]
                    }
                ]
            }
        }
        comment_url = f"{JIRA_URL}/{issue_key}/comment"
        response = requests.post(comment_url, headers=headers, json=comment_data)
        if response.status_code == 201:
            print(f"Comment added to issue {issue_key}")
        else:
            print(f"Failed to add comment to {issue_key}. Status code: {response.status_code}, Response: {response.text}")

# Extract assignee from custom fields
def extract_assignee_from_custom_fields(custom_fields):
    for field in custom_fields:
        if field.get('name') == 'Assignee' and field.get('value'):
            return field['value'].get('name', None)
    return None  

# Extract priority from custom fields
def extract_priority_from_custom_fields(custom_fields):
    for field in custom_fields:
        if field.get('name') == 'Priority' and field.get('value'):
            return field['value'].get('name', None)
    return None  

# Extract issue type from custom fields
def extract_issue_type_from_custom_fields(custom_fields):
    for field in custom_fields:
        if field.get('name') == 'Type' and field.get('value'):
            return field['value'].get('name', None)
    return None 

# Map YouTrack data to Jira issue according to the JSON structure
def map_youtrack_to_jira_issue(issue):
    # Extract assignee from customFields
    assignee_name = extract_assignee_from_custom_fields(issue.get('customFields', []))
    assignee_id = user_mapping.get(assignee_name, None)

    # Fallback for assignee if not found
    if not assignee_id:
        print(f"Assignee '{assignee_name}' not found. Falling back to '{FALLBACK_ASSIGNEE}'.")
        assignee_id = user_mapping.get(FALLBACK_ASSIGNEE)

    # Extract and map reporter 
    reporter_name = issue.get('reporter', {}).get('name', None)
    reporter_id = user_mapping.get(reporter_name, FALLBACK_REPORTER_ID)

    # Extract priority
    youtrack_priority = extract_priority_from_custom_fields(issue.get('customFields', []))
    print(f"Priority from YouTrack: {youtrack_priority}")

    # Map priority to Jira priority
    priority = priority_mapping.get(youtrack_priority, FALLBACK_PRIORITY)

    # Extract issue type from customFields
    youtrack_issue_type = extract_issue_type_from_custom_fields(issue.get('customFields', []))
    print(f"Issue Type from YouTrack: {youtrack_issue_type}")

    # Map issue type 
    issue_type = issue_type_mapping.get(youtrack_issue_type, FALLBACK_TYPE)

    # Jira issue structure
    jira_issue = {
        "fields": {
            "project": {
                "key": "YOUR_JIRA_PROJECT_KEY"
            },
            "summary": issue.get('summary', ''),
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": issue.get('description', '')
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": issue_type  
            },
            "priority": {
                "name": priority  
            },
            "assignee": {
                "id": assignee_id  
            },
            "reporter": {
                "id": reporter_id  
            },
            "labels": [tag['name'] for tag in issue.get('tags', [])],  
            # Add any custom fields if necessary
        }
    }

    return jira_issue

# Get available transitions for an issue in order to set the created issue to done after it's creation
def get_issue_transitions(issue_key):
    transition_url = JIRA_TRANSITION_URL.format(issue_key)
    response = requests.get(transition_url, headers=headers)
    if response.status_code == 200:
        transitions = response.json()['transitions']
        print(f"Available transitions for {issue_key}: {transitions}")
        return transitions
    else:
        print(f"Failed to get transitions for {issue_key}. Status code: {response.status_code}")
        return []

# Function to transition an issue to "Done"
def transition_issue_to_done(issue_key):
    transitions = get_issue_transitions(issue_key)
    
    # Find the transition to "Done" 
    transition_id = None
    for transition in transitions:
        if transition['name'].lower() == 'done': 
            transition_id = transition['id']
            break
    
    if transition_id:
        transition_data = {
            "transition": {
                "id": transition_id
            }
        }
        transition_url = JIRA_TRANSITION_URL.format(issue_key)
        response = requests.post(transition_url, headers=headers, json=transition_data)
        if response.status_code == 204:
            print(f"Issue {issue_key} successfully transitioned to Done")
        else:
            print(f"Failed to transition issue {issue_key} to Done. Status code: {response.status_code}, Response: {response.text}")
    else:
        print(f"No 'Done' transition found for issue {issue_key}")

# Load the YouTrack data
youtrack_data = load_youtrack_data()

# Get starting index from command line arguments if previous imported issues need to be skipped
start_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0

# Iterate over each issue and import from the specified index
for index, issue in enumerate(youtrack_data):
    if index < start_index:
        print(f"Skipping issue {index}")
        continue

    # Map YouTrack issue to Jira issue format
    jira_issue_data = map_youtrack_to_jira_issue(issue)
    issue_key = create_issue_in_jira(jira_issue_data)

    # Handle comments
    if issue_key and 'comments' in issue and issue['comments']:
        add_comments_to_issue(issue_key, issue['comments'])

    # Transition issue to "Done"
    if issue_key:
        transition_issue_to_done(issue_key)