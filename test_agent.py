"""
Test script for the AI Agent.
"""
from agent import BittensorAgent, ask_agent

def test_agent():
    """Test the agent with some questions."""
    print("="*70)
    print("Testing Bittensor Agent")
    print("="*70)

    # Test questions
    questions = [
        "What is Bittensor?",
        "How does TAO token work?",
        "What is subnet registration?",
        "Tell me about Bittensor mining",
    ]

    agent = BittensorAgent()

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*70}")
        print(f"Question {i}: {question}")
        print(f"{'='*70}")

        result = agent.query(question)

        print(f"\nTool used: {result['tool_used']}")
        print(f"\nAnswer:\n{result['answer']}\n")

    # Test simple interface
    print(f"\n{'='*70}")
    print("Testing simple interface")
    print(f"{'='*70}\n")

    answer = ask_agent("What is the purpose of Bittensor?")
    print(f"Q: What is the purpose of Bittensor?")
    print(f"A: {answer}\n")


if __name__ == "__main__":
    test_agent()
