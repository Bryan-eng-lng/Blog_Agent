"""
LangSmith Experiment Runner with Evaluators
Run: python langsmith_experiments.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"]    = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "Blog_Agent")

from langsmith import Client, evaluate
from langsmith.schemas import Run, Example
from graph import run_blog_pipeline

client = Client()
DATASET_NAME = "Blog Agent Test Suite"

# ── Target function ───────────────────────────────────────────────────────────
def run_agent(inputs: dict) -> dict:
    result = run_blog_pipeline(
        topic=inputs.get("topic", ""),
        audience=inputs.get("audience", "general readers"),
        length=inputs.get("length", "medium")
    )
    return {
        "final_blog":    result["final_blog"],
        "overall_score": result["scores"].get("Overall Score", "0"),
        "verdict":       result["scores"].get("Verdict", ""),
        "word_count":    len(result["final_blog"].split()),
    }

# ── Evaluators ────────────────────────────────────────────────────────────────

def eval_word_count(run: Run, example: Example) -> dict:
    """Blog must have at least 500 words"""
    output = run.outputs or {}
    word_count = output.get("word_count", 0)
    return {
        "key": "word_count_pass",
        "score": 1 if word_count >= 500 else 0,
        "comment": f"{word_count} words — {'PASS' if word_count >= 500 else 'FAIL (need 500+)'}"
    }

def eval_quality_score(run: Run, example: Example) -> dict:
    """Overall score must be >= 7.0"""
    output = run.outputs or {}
    try:
        score = float(str(output.get("overall_score", "0")).split()[0])
    except:
        score = 0.0
    return {
        "key": "quality_score_pass",
        "score": 1 if score >= 7.0 else 0,
        "comment": f"Score {score}/10 — {'PASS' if score >= 7.0 else 'FAIL (need 7.0+)'}"
    }

def eval_has_content(run: Run, example: Example) -> dict:
    """Blog must not be empty"""
    output = run.outputs or {}
    blog = output.get("final_blog", "")
    has_content = len(blog.strip()) > 100
    return {
        "key": "has_content",
        "score": 1 if has_content else 0,
        "comment": "Blog has content" if has_content else "FAIL — empty output"
    }

# ── Run experiment with evaluators ───────────────────────────────────────────
print(f"Running experiment with evaluators on: {DATASET_NAME}\n")

results = evaluate(
    run_agent,
    data=DATASET_NAME,
    evaluators=[eval_word_count, eval_quality_score, eval_has_content],
    experiment_prefix="Blog_Agent_v2_with_evals",
    description="Experiment with automated evaluators",
)

print("\n✅ Done! View at: https://smith.langchain.com → Datasets & Experiments")
