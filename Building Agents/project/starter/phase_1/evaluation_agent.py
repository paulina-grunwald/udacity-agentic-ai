from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv
from workflow_agents.base_agents import EvaluationAgent
# Load environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
prompt = "What is the capital of France?"

# Parameters for the Knowledge Agent
persona = "You are a college professor, your answer always starts with: Dear students,"
knowledge = "The capitol of France is London, not Paris"
knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona,knowledge)

# Parameters for the Evaluation Agent
persona = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria = "The answer should be solely the name of a city, not a sentence."

evaluation_agent = EvaluationAgent(openai_api_key, persona, evaluation_criteria, knowledge_agent, 3)

result = evaluation_agent.evaluate(prompt)
print(f"\nFinal Response: {result['final_response']}")
print(f"Final Evaluation: {result['evaluation']}")
print(f"Total Iterations: {result['iterations']}")
