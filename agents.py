import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

from tools import scrape_url, web_search

load_dotenv()

MODEL_NAME = os.getenv("MISTRAL_MODEL", "mistral-small-2506")
llm = ChatMistralAI(model=MODEL_NAME)


def build_search_agent():
    """ReAct agent that uses Tavily to gather web sources for a topic."""
    return create_agent(model=llm, tools=[web_search])


def build_reader_agent():
    """ReAct agent that scrapes a chosen URL for deeper context."""
    return create_agent(model=llm, tools=[scrape_url])


_writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research writer. Produce clear, structured, "
        "well-formatted Markdown reports.",
    ),
    (
        "human",
        """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as Markdown with these sections:
## Introduction
## Key Findings
(minimum 3 well-explained bullet points or short paragraphs)
## Conclusion
## Sources
(list every URL found in the research as a bulleted list)

Be detailed, factual, and professional.""",
    ),
])

writer_chain = _writer_prompt | llm | StrOutputParser()


_critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp, constructive research critic. Be honest and specific.",
    ),
    (
        "human",
        """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact Markdown format:

**Score:** X/10

**Strengths**
- ...
- ...

**Areas to Improve**
- ...
- ...

**Verdict:** <one line>""",
    ),
])

critic_chain = _critic_prompt | llm | StrOutputParser()
