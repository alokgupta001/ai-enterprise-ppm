"""
Base agent pattern — all specialized agents inherit from this.
Handles prompt templating and LLM invocation with graceful fallback.
"""
import os
import json
from abc import ABC, abstractmethod

OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY", "").strip())


class BaseAgent(ABC):
    """Abstract base for specialized PMO analysis agents."""

    def __init__(self, system_prompt: str, agent_name: str):
        self.system_prompt = system_prompt
        self.agent_name = agent_name

    def run(self, context: str, question: str) -> dict:
        """Execute the agent against a question with portfolio context."""
        if OPENAI_AVAILABLE:
            return self._run_llm(context, question)
        return self._run_fallback(context, question)

    def _run_llm(self, context: str, question: str) -> dict:
        """Run using LLM (OpenAI via LangChain)."""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                max_retries=2,
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "Project Portfolio Context:\n{context}\n\nQuestion: {question}"),
            ])

            chain = prompt | llm
            result = chain.invoke({"context": context, "question": question})
            return {"agent": self.agent_name, "response": result.content}
        except Exception as e:
            print(f"[{self.agent_name}] LLM call failed: {e}")
            return self._run_fallback(context, question)

    @abstractmethod
    def _run_fallback(self, context: str, question: str) -> dict:
        """Fallback analysis when LLM is unavailable."""
        pass
