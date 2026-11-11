Blog Content Crew

A multi-agent content pipeline built with CrewAI and exposed as a REST API via FastAPI. Given a topic, three collaborating agents research it, draft a short blog post, and edit the result.

Architecture
Topic ──► Researcher ──► Writer ──► Editor ──► Final post
          (web search)   (context)  (context)
Agent	Responsibility	Tools
Researcher	Gathers five key findings on the topic, each with a cited source	SerperDevTool (falls back to WebsiteSearchTool)
Writer	Drafts a 300–400 word post (title, introduction, body, conclusion) from the researcher's output	None; relies on task context only
Editor (optional)	Reviews tone, grammar and structure and returns the final version	None

Agents run through Process.sequential with verbose=True, so each agent's reasoning is visible in the server logs. The editor can be disabled per request.

Project Structure
.
├── app/
│   ├── __init__.py
│   ├── crew.py          # Agents, tasks, crew and process definition
│   └── main.py          # FastAPI application and endpoints
├── .env.example         # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
Getting Started
Prerequisites
Python 3.10+
An OpenAI API key (CrewAI's default LLM provider)
(Optional) A free Serper API key for web search
Installation
bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in your keys
Configuration
Variable	Required	Description
OPENAI_API_KEY	Yes	API key for the LLM
MODEL	No	Overrides the default model
SERPER_API_KEY	No	Enables SerperDevTool; otherwise WebsiteSearchTool is used
Running the Server
bash
uvicorn app.main:app --reload

Interactive API docs are available at http://127.0.0.1:8000/docs.

API Reference
Method	Endpoint	Description
GET	/health	Liveness check
POST	/generate	Generates a post for a single topic
POST	/compare	Runs the crew on 2–5 topics and returns posts with word counts
POST	/compare-editor	Produces the same topic with and without the editor for side-by-side comparison
Examples

Generate a post:

bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "هوش مصنوعی در بورس تهران", "use_editor": true}'

Compare multiple topics:

bash
curl -X POST http://127.0.0.1:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"topics": ["topic1", "topic2"]}'

Compare output with and without the editor:

bash
curl -X POST http://127.0.0.1:8000/compare-editor \
  -H "Content-Type: application/json" \
  -d '{"topic": "هوش مصنوعی در بورس تهران"}'
Design Notes
Blocking execution. crew.kickoff() is synchronous, so each run is dispatched with asyncio.to_thread. This keeps the event loop responsive and allows /compare to run topics concurrently.
Crew per request. A fresh crew is built for every call, which avoids shared state between concurrent requests.
Search tool fallback. The tool is selected at runtime from the environment, so the service starts without a Serper key.
Reflection: The Role of the Editor Agent

Removing the editor typically leaves the content intact but lowers polish: inconsistent tone, minor grammar and spelling errors, repetitive or overlong sentences, and occasional drift outside the 300–400 word target. The writer must produce the content and police its linguistic quality in the same pass, whereas a dedicated editor has a single, distinct objective and acts as an independent second review. Separating generation from review is the core principle of multi-agent design in CrewAI, and it consistently improves output reliability.
