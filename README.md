# Blog Writer Agent

A research-first blog writing agent that produces deeply researched, publish-ready blog posts using a multi-step agentic pipeline.

Unlike a single LLM call, this agent plans, researches, extracts facts, analyzes competitors, writes, critiques, rewrites, removes clichés, scores, and generates SEO metadata — all automatically.

---

## Pipeline

1. Plan — generates a specific, audience-aware blog outline
2. Research — runs 4 parallel web searches using Tavily
3. Competitor Gap Analysis — finds what existing articles miss and writes to fill that gap
4. Memory Retrieval — pulls relevant past context from vector memory (Chroma)
5. Fact Extraction — strips raw research down to named sources, real stats, and concrete examples
6. Write Draft — writes a full blog using only verified facts
7. Critique and Rewrite — a senior editor pass that fixes weak hooks, filler, and poor conclusions
8. Cliché Detection — scans for 30+ known clichés and replaces them with topic-specific language
9. SEO Metadata — generates meta title, description, keywords, tags, and read time
10. Blog Score — scores the final blog across readability, hook strength, depth, SEO, and conclusion quality

---

## Tech Stack

- LLM: Groq (llama-3.3-70b-versatile) with automatic key rotation
- Search: Tavily API (advanced depth, parallel queries)
- Memory: Chroma vector store with OllamaEmbeddings
- Framework: LangChain + FastAPI

---

## Setup

1. Clone the repo and install dependencies

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the `blog_agent` folder

```
TAVILY_API_KEY=your_tavily_key
GROQ_KEY_1=your_first_groq_key
GROQ_KEY_2=your_second_groq_key
```

3. Start Ollama (required for memory embeddings)

```bash
ollama serve
ollama pull nomic-embed-text
```

4. Run the CLI

```bash
python main.py
```

Or start the API server

```bash
uvicorn api:app --reload
```

---

## API Usage

POST `/generate-blog`

```json
{
  "topic": "Why Most Diets Fail in the First 30 Days",
  "audience": "People aged 25-40 who keep falling off track",
  "length": "medium"
}
```

Length options: `short` (600-800 words), `medium` (1000-1500 words), `long` (2000-2500 words)

---

## What Makes It Different

Most AI blog tools make a single LLM call. This agent:

- Searches the web before writing — no hallucinated statistics
- Analyzes what competitors have already written and fills the gap
- Runs a dedicated fact extraction step so the writer only uses verified data
- Has a built-in editor that rewrites weak sections
- Detects and replaces clichés automatically
- Scores its own output so users know what they're publishing

---

## Project Structure

```
blog_agent/
├── agent.py       # Core pipeline — all LLM functions
├── tools.py       # Tavily web search
├── memory.py      # Chroma vector store
├── main.py        # CLI interface
├── api.py         # FastAPI endpoint
└── .env           # API keys (not committed)
```
