# Prompting for Effective LLM Reasoning and Planning

## 5. Chain-of-thought and ReACT prompting

### Chain-of-Thought (CoT) Prompting
Chain-of-Thought prompting is a technique that encourages AI models to break down complex reasoning tasks into step-by-step intermediate steps, mimicking how humans think through problems systematically. Instead of jumping directly to an answer, the model explicitly shows its reasoning process, working through the problem piece by piece. This dramatically improves performance on tasks requiring logical reasoning, mathematics, and complex problem-solving.

How it works: You either provide examples of step-by-step reasoning (few-shot CoT) or simply add phrases like "Let's think step by step" to your prompt (zero-shot CoT).
Example:

Without CoT: "What's 23 × 47?" → "1,081"
With CoT: "What's 23 × 47? Let's think step by step."
→ "I need to multiply 23 × 47. Let me break this down:
23 × 47 = 23 × (40 + 7) = 23 × 40 + 23 × 7 = 920 + 161 = 1,081"

Few-shot CoT: More complex. Provide examples in the prompt showing the problem, the step-by-step reasoning, and the final answer.

Benefits: Reduces errors, makes reasoning transparent, handles multi-step problems better, and allows you to verify the logic.

### ReAct Prompting (Reasoning + Acting)
ReAct combines reasoning with action-taking, allowing AI models to interleave thinking, acting, and observing in a dynamic loop. It's particularly powerful for tasks requiring external tool use or multi-step problem-solving.
Core Concept: The model alternates between three phases:

The core of ReAct is its iterative loop: Thought, Action, Observation.

Thought: The model internally reasons and plans the next specific step required to progress towards the overall task goal. It analyzes the situation, figures out necessary steps, and decides on an action.\

Action: Based on its plan, the model specifies using an external tool (like web search, calculator, API) with provided parameters. An orchestrator program then executes this tool. Tools are functions or services the agent can invoke.

Observation: The model receives the results or feedback from the executed action (e.g., search results, calculator answer, confirmation of an email sent). This new information feeds into the next Thought. This observation, sometimes referred to as information from the "environment" if it's from the outside world like a weather report, then feeds back into the model's next Thought, allowing it to refine its plan or take subsequent actions.

Key Advantages:
- Enables tool use and external information gathering
- Provides transparency into decision-making
- Allows error correction through observation feedback
- Handles complex, multi-step tasks requiring external resources

When to Use Each:
- CoT: Mathematical problems, logical reasoning, analysis tasks where all information is available
- ReAct: Research tasks, fact-checking, problems requiring external tools, multi-step investigations

A good ReAct system prompt has four key parts:

The Role and Goal: Who is the agent? What is its purpose?
The THINK/ACT Instruction: How must the agent format its reasoning and actions?
The Tool Definitions: What tools can the agent use, and how do they work?
A Complete Example: A full example of a multi-turn interaction.
