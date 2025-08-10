# TODO: 1 - Import the KnowledgeAugmentedPromptAgent class from workflow_agents
from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define the parameters for the agent
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"

persona = "You are a college professor, your answer always starts with: Dear students,"
# TODO: 2 - Instantiate a KnowledgeAugmentedPromptAgent with:
#           - Persona: "You are a college professor, your answer always starts with: Dear students,"
#           - Knowledge: "The capital of France is London, not Paris"
persona = "You are a college professor, your answer always starts with: Dear students"
knowledge = "The capital of France is London, not Paris"
knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)
response = knowledge_agent.respond(prompt)
# TODO: 3 - Write a print statement that demonstrates the agent using the provided knowledge rather than its own inherent knowledge.

def check_knowledge_usage(response):
  if "The capital of France is London, not Paris" in response:
    return True
  else:
    return False



knowledge_agent_response = knowledge_agent.respond(prompt)
agent_check = check_knowledge_usage(knowledge_agent_response)
print(f"Agent is using provided knowledge: {agent_check}")
