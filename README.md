# YouTrack to Jira Migration Script

This repository contains a Python script that migrates issues from YouTrack to Jira. The script reads issues from a JSON file exported from YouTrack and creates corresponding issues in Jira, including comments and transitions to a specified workflow state.

## Overview
* Export issues from YouTrack: Use the provided `curl` command to export issues from YouTrack into a JSON file.
* Run the migration script: The Python script reads the JSON file, maps YouTrack fields to Jira fields, and creates issues in Jira.
* Add comments and transitions: The script also imports comments and transitions issues to a specified status (e.g., "Done").

## Prerequisites
* Python 3.x installed on your machine.
* Required Python packages: `requests`.
* Access to YouTrack and Jira APIs with the necessary permissions.
* Jira API token and email address.
* Jira project key where the issues will be imported.
* Mapping of users from YouTrack to Jira (optional but recommended).

## Setup
1. **Clone the repository:**

        git clone https://github.com/bibarella/youtrack-to-jira-migration.git
        cd youtrack-to-jira-migration

2. **Install dependencies:**

        pip install requests

3. **Export issues from YouTrack:**

Use the following `curl` command to export issues from YouTrack. Replace placeholders with your actual data.

        curl -X GET \
        "https://your-youtrack-instance.myjetbrains.com/youtrack/api/issues?query=project:YOURPROJECT&fields=idReadable,tags(name),summary,reporter(name),created,updated,resolved,priority(name),issueType(name),assignee(name),customFields(name,value(name)),reportedUser(name),description,comments(text,author(name),created)" \
        -H "Authorization: Bearer <your_bearer_token>" \
        -o output.json

* Replace `your-youtrack-instance` with your YouTrack domain.
* Replace `YOURPROJECT` with your YouTrack project identifier.
* Replace `<your_bearer_token>` with your YouTrack API token.

4. **Configure the script:**

* Open `script.py` in a text editor.

Update the following variables with your Jira details:

        # Jira API information
        JIRA_URL = "https://your-domain.atlassian.net/rest/api/3/issue"
        JIRA_TRANSITION_URL = "https://your-domain.atlassian.net/rest/api/3/issue/{}/transitions"
        API_TOKEN = "your_api_token"
        EMAIL = "your_email@example.com"


* Replace `your-domain` with your Jira domain.
* Replace `your_api_token` with your Jira API token.
* Replace `your_email@example.com` with your Jira email address.

* **User Mapping**: Update the `user_mapping` dictionary to map YouTrack user names to Jira account IDs. There is also a mapping for priority and issuetypes available in the script. 

        user_mapping = {
            "YouTrack User Name 1": "jira_account_id_1",
            "YouTrack User Name 2": "jira_account_id_2",
            # Add more mappings as needed
        }
* **Fallback Values**: Update fallback values if necessary.


        FALLBACK_REPORTER_ID = "jira_fallback_reporter_id"
        FALLBACK_ASSIGNEE = "Fallback Assignee Name"
        
* **Project Key**: Update the Jira project key where issues will be imported.

        "project": {
            "key": "YOUR_JIRA_PROJECT_KEY"
        }

## Usage
Run the script with:

        python jira_import.py

* Optionally, you can specify a starting index to skip issues:

        python jira_import.py <start_index>

## Script Details
* **Functions:**

* `load_youtrack_data()`: Loads issues from output.json.
* `create_issue_in_jira(issue_data)`: Creates an issue in Jira.
* `add_comments_to_issue(issue_key, comments)`: Adds comments to a Jira issue.
* `transition_issue_to_done(issue_key)`: Transitions the issue to the "Done" status.
* `map_youtrack_to_jira_issue(issue)`: Maps YouTrack issue fields to Jira issue fields.

* **Mappings:**

* Priority and issue type mappings are defined to translate YouTrack values to Jira equivalents.
* User mappings are used to assign issues to the correct Jira users.

## Notes
* Ensure that all sensitive data such as API tokens, email addresses, and account IDs are kept secure and are not shared publicly.
* Modify the script as needed to fit your specific use case and Jira configuration.
* Test the script with a small set of issues before running it on the entire dataset.

## License

This project is licensed under the MIT License.