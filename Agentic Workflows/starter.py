"""
Program Management Knowledge Agent - Starter Code

This program demonstrates two approaches to answering program management questions:
1. Using hardcoded knowledge
2. Using an LLM API

Complete the TODOs to build your knowledge agent.
"""

from openai import OpenAI
import os

# TODO: Initialize the OpenAI client if API key is available
# Hint: Use os.getenv() to get the API key from environment variables
client = OpenAI(
    # Change the base_url when using the Vocareum API endpoint
    # If using the OpenAI API endpoint, you can comment out the base_url line
    base_url="https://openai.vocareum.com/v1",
    # Uncomment one of the following
    api_key="voc-7365955961607363338581687755b5a1dfb4.10012173",

)
def get_hardcoded_answer(question):
    """
    Return answers to program management questions using hardcoded knowledge.

    Args:
        question (str): The question about program management

    Returns:
        str: The answer to the question
    """
    # TODO: Convert question to lowercase for easier matching
    question = question.lower()

    # TODO: Implement responses for at least 5 common program management questions
    # Include questions about: Gantt charts, Agile, sprints, critical path, and milestones
    if "gantt" in question:
        return "Gantt charts are a type of project management tool that helps visualize the timeline of a project."
    elif "agile" in question:
        return "Agile is a project management methodology that emphasizes flexibility and adaptability."
    elif "sprint" in question:
        return "Sprints are short periods of time used in Agile project management to deliver a working product."
    elif "critical path" in question:
        return "Critical path is the longest path through a project network diagram, representing the minimum time required to complete the project."
    elif "milestone" in question:
        return "Milestones are significant events or deliverables in a project that mark key progress or completion of a phase."
    elif "project management" in question:
        return "Project management is the practice of planning, organizing, and managing resources to achieve specific goals and objectives."
    elif "project" in question:
        return "A project is a temporary endeavor with a defined beginning and end, undertaken to achieve a specific outcome."
    elif "program" in question:
        return "A program is a collection of projects and activities that are coordinated to achieve a common goal."
    elif "project manager" in question:
        return "A project manager is a professional who oversees the planning, execution, and completion of a project."
    else:
        # TODO: Add a default response for questions not in your knowledge base
        return "I don't know the answer to that question."

def get_llm_answer(question):
    """
    Get answers to program management questions using an LLM API.

    Args:
        question (str): The question about program management

    Returns:
        str: The answer from the LLM
    """
    # TODO: Check if the LLM client is initialized
    if client is None:
        raise ValueError("OpenAI client is not initialized")

    # TODO: Implement the API call to get an answer from the LLM
    # Use a system message to specify that the LLM should act as a program management expert
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a program management expert. You are given a question about program management and you need to answer it. Please provide your response as plain text."},
            {"role": "user", "content": question}
        ]
    )

    # Check if the response has choices before accessing them
    if response.choices and len(response.choices) > 0:
        return response.choices[0].message.content
    else:
        return "Error: Unable to get response from LLM"



# Demo function to compare both approaches
def compare_answers(question):
    """Compare answers from both approaches for a given question."""
    print(f"\nQuestion: {question}")
    print("-" * 50)

    # TODO: Get and display the hardcoded answer
    hardcoded_answer = get_hardcoded_answer(question)
    print(f"Hardcoded Answer: {hardcoded_answer}")

    # TODO: Get and display the LLM answer (or a placeholder message)
    llm_answer = get_llm_answer(question)
    print(f"LLM Answer: {llm_answer}")

    print("=" * 50)

# Demo with sample questions
if __name__ == "__main__":
    print("PROGRAM MANAGEMENT KNOWLEDGE AGENT DEMO")
    print("=" * 50)

    # TODO: Create a list of sample program management questions
    questions = [
        "What is a Gantt chart?",
        "What is Agile?",
        "What is a sprint?",
        "What is a critical path?",
        "What is a milestone?",
    ]
    # TODO: Loop through the questions and compare answers
    for question in questions:
        compare_answers(question)
