def main():
    print("Hello from smart-search!")
    
    # Print system information
    print("\n🔍 Smart Search System Information:")
    print("-" * 40)
    
    try:
        from agents.agent_team import AgentTeam
        team = AgentTeam()
        status = team.get_team_status()
        
        print(f"Team Members: {', '.join(status['team_members'])}")
        print(f"LLM APIs Available: {', '.join(status['available_apis']['llm'])}")
        print(f"Search APIs Available: {', '.join(status['available_apis']['search'])}")
        print(f"Reranker APIs Available: {', '.join(status['available_apis']['reranker'])}")
        print(f"Jira Integration: {'Enabled' if status['jira_integration'] else 'Disabled'}")
        
    except Exception as e:
        print(f"Could not load agent team: {e}")
    
    print("\n🚀 System Ready!")
    print("Use 'python run.py' to start the web interface")
    print("Use 'python -m cli.smart_search' for command-line search")

if __name__ == "__main__":
    main()
