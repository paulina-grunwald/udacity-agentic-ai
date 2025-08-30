# agentic_workflow.py
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
phase_1_path = os.path.join(current_dir, '..', 'phase_1')
sys.path.insert(0, phase_1_path)

from workflow_agents.base_agents import ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent

from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

product_spec_path = os.path.join(current_dir, 'Product-Spec-Email-Router.txt')
with open(product_spec_path, 'r') as file: product_spec = file.read()


# Instantiate all the agents
# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)
# TODO: 4 - Instantiate an action_planning_agent using the 'knowledge_action_planning'
action_planning_agent = ActionPlanningAgent(openai_api_key,knowledge_action_planning)
# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    "\n\n" + product_spec
)
# Instantiate a product_manager_knowledge_agent using 'persona_product_manager' and the completed 'knowledge_product_manager'
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key,persona_product_manager,knowledge_product_manager )

# Product Manager - Evaluation Agent
# Define the persona and evaluation criteria for a Product Manager evaluation agent and instantiate it as product_manager_evaluation_agent. This agent will evaluate the product_manager_knowledge_agent.
# The evaluation_criteria should specify the expected structure for user stories (e.g., "As a [type of user], I want [an action or feature] so that [benefit/value].").
persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
product_manager_evaluation_criteria = (
    "The answer should be user stories that follow this exact structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]. "
    "Each story must start with 'As a' and contain all three components: persona, action, and benefit."
)

product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_product_manager_eval,
    product_manager_evaluation_criteria,
    product_manager_knowledge_agent,
    3
)


# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."

# Instantiate a program_manager_knowledge_agent using 'persona_program_manager' and 'knowledge_program_manager'
program_manager_knowledge_agent= KnowledgeAugmentedPromptAgent(openai_api_key,persona_program_manager,knowledge_program_manager)
# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

evaluation_criteria_program_manager = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_program_manager_eval,
    evaluation_criteria_program_manager,
    program_manager_knowledge_agent,
    3
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
# Instantiate a development_engineer_knowledge_agent using 'persona_dev_engineer' and 'knowledge_dev_engineer'
# (This is a necessary step before TODO 9. Students should add the instantiation code here.)
development_engineer_knowledge_agent=KnowledgeAugmentedPromptAgent(openai_api_key, persona_dev_engineer, knowledge_dev_engineer)
# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
# Instantiate a development_engineer_evaluation_agent using 'persona_dev_engineer_eval' and the evaluation criteria below.

dev_eng_evaluation_criteria = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_dev_engineer_eval,
    dev_eng_evaluation_criteria,
    development_engineer_knowledge_agent,
    3
)

# Routing Agent
# Instantiate a routing_agent
agents = [product_manager_knowledge_agent, program_manager_evaluation_agent, development_engineer_evaluation_agent]

# Support functions
def product_manager_support_function(query):
    initial_response = product_manager_knowledge_agent.respond(query)
    evaluation_result = product_manager_evaluation_agent.evaluate(query)
    return evaluation_result['final_response']

def program_manager_support_function(query):
    initial_response = program_manager_knowledge_agent.respond(query)
    evaluation_result = program_manager_evaluation_agent.evaluate(query)
    return evaluation_result['final_response']

def development_engineer_support_function(query):
    initial_response = development_engineer_knowledge_agent.respond(query)
    evaluation_result = development_engineer_evaluation_agent.evaluate(query)
    return evaluation_result['final_response']

agents= [
   {
        "name": "product manager agent",
        "description": "Defines user stories for product features",
        "func": product_manager_support_function
    },
    {
      "name": "program manager agent",
      "description": "Organizes user stories into product features",
      "func": program_manager_support_function
    },
    {
      "name": "development engineer agent",
      "description": "Defines development tasks for implementing user stories",
      "func": development_engineer_support_function
    },
]
routing_agent = RoutingAgent(openai_api_key, agents)

# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "What would the development tasks for this product be?"
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
# Implement the workflow.
#   1. Use the 'action_planning_agent' to extract steps from the 'workflow_prompt'.
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
print(f"\nExtracted {len(workflow_steps)} steps from the workflow prompt")

#   2. Initialize an empty list to store 'completed_steps'.
completed_steps = []

#   3. Loop through the extracted workflow steps:
for i, step in enumerate(workflow_steps):
    print(f"\n--- Step {i+1}/{len(workflow_steps)} ---")
    print(f"Executing: {step}")

    # For each step, use the 'routing_agent' to route the step to the appropriate support function.
    result = routing_agent.route_prompt(step)
    # Append the result to 'completed_steps'.
    completed_steps.append(result)

    # Print information about the step being executed and its result.
    print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")

#   4. After the loop, print the final output of the workflow (the last completed step).
print("\n*** Workflow execution completed ***")
if completed_steps:
    print("\nFinal output:")
    print(completed_steps[-1])
