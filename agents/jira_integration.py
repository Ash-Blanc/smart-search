import requests
import json
from config import JIRA_API_KEY, JIRA_BASE_URL, JIRA_USERNAME
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraIntegration:
    """Integration with Jira for workflow management and task tracking."""
    
    def __init__(self):
        self.api_key = JIRA_API_KEY
        self.base_url = JIRA_BASE_URL
        self.username = JIRA_USERNAME
        
        if not all([self.api_key, self.base_url, self.username]):
            raise ValueError("JIRA_API_KEY, JIRA_BASE_URL, and JIRA_USERNAME are required for Jira integration")
        
        # Create authentication header
        credentials = f"{self.username}:{self.api_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_issue(self, project_key: str, summary: str, description: str = "", 
                    issue_type: str = "Task", priority: str = "Medium"):
        """
        Create a new issue in Jira.
        
        Args:
            project_key (str): The Jira project key
            summary (str): Issue summary/title
            description (str): Detailed description
            issue_type (str): Type of issue (Task, Bug, Story, etc.)
            priority (str): Priority level (Highest, High, Medium, Low, Lowest)
        
        Returns:
            dict: Response from Jira API
        """
        url = f"{self.base_url}/rest/api/2/issue"
        
        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": issue_type
                },
                "priority": {
                    "name": priority
                }
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Jira issue: {str(e)}")
            raise Exception(f"Failed to create Jira issue: {str(e)}")
    
    def search_issues(self, jql: str, max_results: int = 50):
        """
        Search for issues using JQL.
        
        Args:
            jql (str): Jira Query Language query
            max_results (int): Maximum number of results to return
        
        Returns:
            dict: Search results from Jira
        """
        url = f"{self.base_url}/rest/api/2/search"
        
        params = {
            "jql": jql,
            "maxResults": max_results
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search Jira issues: {str(e)}")
            raise Exception(f"Failed to search Jira issues: {str(e)}")
    
    def update_issue(self, issue_key: str, fields: dict):
        """
        Update an existing Jira issue.
        
        Args:
            issue_key (str): The issue key (e.g., "PROJ-123")
            fields (dict): Fields to update
        
        Returns:
            dict: Response from Jira API
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        
        payload = {
            "fields": fields
        }
        
        try:
            response = requests.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update Jira issue {issue_key}: {str(e)}")
            raise Exception(f"Failed to update Jira issue {issue_key}: {str(e)}")
    
    def add_comment(self, issue_key: str, comment: str):
        """
        Add a comment to a Jira issue.
        
        Args:
            issue_key (str): The issue key
            comment (str): Comment text
        
        Returns:
            dict: Response from Jira API
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
        
        payload = {
            "body": comment
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add comment to Jira issue {issue_key}: {str(e)}")
            raise Exception(f"Failed to add comment to Jira issue {issue_key}: {str(e)}")
    
    def get_issue(self, issue_key: str):
        """
        Get details of a specific Jira issue.
        
        Args:
            issue_key (str): The issue key
        
        Returns:
            dict: Issue details from Jira
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Jira issue {issue_key}: {str(e)}")
            raise Exception(f"Failed to get Jira issue {issue_key}: {str(e)}")

# Agent task management with Jira integration
class AgentTaskManager:
    """Manage agent tasks and workflows using Jira integration."""
    
    def __init__(self, project_key: str = "AI"):
        self.jira = JiraIntegration() if all([JIRA_API_KEY, JIRA_BASE_URL, JIRA_USERNAME]) else None
        self.project_key = project_key
    
    def create_search_task(self, query: str, user_id: str = "default"):
        """
        Create a Jira task for a search query.
        
        Args:
            query (str): The search query
            user_id (str): User identifier
        
        Returns:
            dict: Jira issue details or None if Jira not configured
        """
        if not self.jira:
            logger.warning("Jira not configured, skipping task creation")
            return None
        
        try:
            summary = f"AI Search: {query[:50]}{'...' if len(query) > 50 else ''}"
            description = f"""
            Automated AI search task
            
            Query: {query}
            User ID: {user_id}
            Priority: Medium
            
            Task created by Smart Search agent.
            """
            
            issue = self.jira.create_issue(
                project_key=self.project_key,
                summary=summary,
                description=description,
                issue_type="Task",
                priority="Medium"
            )
            
            logger.info(f"Created Jira task {issue.get('key')} for search query")
            return issue
        except Exception as e:
            logger.error(f"Failed to create search task in Jira: {str(e)}")
            return None
    
    def update_task_with_results(self, issue_key: str, results: dict):
        """
        Update a Jira task with search results.
        
        Args:
            issue_key (str): Jira issue key
            results (dict): Search results
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.jira:
            return False
        
        try:
            # Add results as a comment
            results_comment = f"""
            Search Results:
            
            Confidence: {results.get('confidence', 'N/A')}%
            Personalized: {results.get('personalized', False)}
            
            Results:
            {results.get('results', 'No results available')}
            
            Verification:
            {results.get('verification', 'No verification data')}
            """
            
            self.jira.add_comment(issue_key, results_comment)
            
            # Update issue status
            self.jira.update_issue(issue_key, {
                "status": "Done"
            })
            
            logger.info(f"Updated Jira task {issue_key} with search results")
            return True
        except Exception as e:
            logger.error(f"Failed to update Jira task {issue_key}: {str(e)}")
            return False
    
    def log_agent_activity(self, activity: str, details: dict = None):
        """
        Log agent activity as a Jira task or comment.
        
        Args:
            activity (str): Description of activity
            details (dict): Additional details
        
        Returns:
            dict: Jira issue or None
        """
        if not self.jira:
            return None
        
        try:
            summary = f"Agent Activity: {activity[:50]}{'...' if len(activity) > 50 else ''}"
            description = f"""
            Automated agent activity log
            
            Activity: {activity}
            
            Details:
            {json.dumps(details, indent=2) if details else 'No additional details'}
            
            Logged by Smart Search agent.
            """
            
            issue = self.jira.create_issue(
                project_key=self.project_key,
                summary=summary,
                description=description,
                issue_type="Task",
                priority="Low"
            )
            
            logger.info(f"Logged agent activity in Jira task {issue.get('key')}")
            return issue
        except Exception as e:
            logger.error(f"Failed to log agent activity in Jira: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    # This would require valid JIRA credentials to run
    try:
        task_manager = AgentTaskManager("AI")
        # Example of creating a search task
        # task = task_manager.create_search_task("Latest AI developments 2024", "user123")
        # print(json.dumps(task, indent=2))
    except Exception as e:
        print(f"Error: {e}")