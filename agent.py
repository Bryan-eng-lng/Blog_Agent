import os
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from groq import RateLimitError
from tools import web_search

load_dotenv()

GROQ_KEYS = [v for k, v in sorted(os.environ.items()) if k.startswith("GROQ_KEY") and v]
CEREBRAS_KEY = os.getenv("CEREBRAS_API_KEY")
_key_index = 0


def _invoke(prompt: str, temperature: float) -> str:
    global _key_index

    # Try Cerebras first — faster and higher rate limits
    if CEREBRAS_KEY:
        for attempt in range(3):
            try:
                from langchain_cerebras import ChatCerebras
                llm = ChatCerebras(
                    model="llama-3.3-70b",
                    temperature=temperature
                )
                return llm.invoke(prompt).content
            except Exception as e:
                err = str(e).lower()
                if "rate" in err or "429" in err:
                    print(f"Cerebras rate limit, waiting 10s... (attempt {attempt+1})")
                    time.sleep(10)
                else:
                    print(f"Cerebras failed: {e}, falling back to Groq...")
                    break

    # Fall back to Groq with key rotation
    for _ in range(len(GROQ_KEYS) * 2):
        try:
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                api_key=GROQ_KEYS[_key_index]
            )
            return llm.invoke(prompt).content
        except RateLimitError:
            print(f"Rate limit on Groq key {_key_index + 1}, switching...")
            _key_index = (_key_index + 1) % len(GROQ_KEYS)
            time.sleep(2)

    raise Exception("All LLM providers are rate limited. Try again in a minute.")


CLICHES = [
    "you can't have your cake and eat it too",
    "wake up and smell the coffee",
    "at the end of the day",
    "journey not a destination",
    "journey, not a destination",
    "humans + machines",
    "unlock your potential",
    "unlock a world of",
    "are you ready to",
    "start living",
    "game changer",
    "game-changer",
    "revolutionize",
    "in today's world",
    "in today's fast-paced",
    "have you ever wondered",
    "the future is now",
    "think outside the box",
    "it is what it is",
    "ticking time bomb",
    "warm handshake",
    "as the saying goes",
    "one size fits all",
    "paradigm shift",
    "move the needle",
    "circle back",
    "deep dive",
    "it goes without saying",
    "needless to say",
    "a perfect storm",
    "perfect storm",
    "culinary revolution",
]

LENGTH_GUIDE = {
    "short": "600 to 800 words. 3 to 4 sections. Every sentence must earn its place. Dense, sharp, zero filler. Short does not mean shallow — pack maximum insight into minimum words.",
    "medium": "1000 to 1500 words. 5 to 6 sections. Each section goes one level deeper than the surface. At least 2 specific data points or named examples per section.",
    "long": "2000 to 2500 words. 7 to 8 sections. Full depth on every angle. Multiple named examples, data points, and at least 2 strong analogies throughout. Every section should feel like it could stand alone."
}


def fix_cliches(blog: str, topic: str) -> str:
    found = [c for c in CLICHES if c.lower() in blog.lower()]
    if not found:
        return blog
    cliche_list = "\n".join(f"- {c}" for c in found)
    prompt = f"""
You are a sharp editor. The blog below contains these clichés that must be replaced:

{cliche_list}

For each one, replace it with something specific, fresh, and relevant to the topic "{topic}".
Do not change anything else — only fix the clichés listed above.
Return the full blog with only those replacements made.

Blog:
{blog}
"""
    return _invoke(prompt, temperature=0.5)


def plan_blog(topic: str, audience: str) -> str:
    prompt = f"""
You are a blog strategist and content analyst.

Topic: {topic}
Target Audience: {audience}

Do two things in one response:

OUTLINE:
1. Title — specific, curiosity-driven, honest.
2. Opening hook — specific tension, surprising fact, or uncomfortable truth.
3. 4 to 6 section headings — each with a one-line description.
4. Core argument — the single most important takeaway.
5. Conclusion angle — challenge, reframe, call to action, or hard truth.
Recommended Length: one word — short / medium / long

COMPETITOR GAP:
In 2-3 sentences: what angle do most articles on this topic take, and what unique angle would make this blog stand out?
"""
    return _invoke(prompt, temperature=0.3)


def analyze_competitor_gap(topic: str) -> str:
    # Merged into plan_blog to save LLM calls
    return ""
    queries = [
        topic,
        f"{topic} surprising facts and lesser known insights",
        f"{topic} recent data statistics research 2024 2025",
        f"{topic} common misconceptions and expert perspectives"
    ]

    def fetch(q):
        result = web_search(q)
        return f"Query: {q}\n{result}"

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fetch, queries))

    return "\n\n".join(results)


def research(topic: str) -> str:
    queries = [
        topic,
        f"{topic} surprising facts and lesser known insights",
        f"{topic} recent data statistics research 2024 2025",
        f"{topic} common misconceptions and expert perspectives"
    ]

    def fetch(q):
        result = web_search(q)
        return f"Query: {q}\n{result}"

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fetch, queries))

    return "\n\n".join(results)


def extract_facts(topic: str, research_data: str) -> str:
    prompt = f"""
You are a research analyst. Extract only the most concrete, specific, and useful information.

Topic: {topic}

From the research below, extract:
- Specific statistics with their source
- Named tools, companies, or products that are relevant
- Real examples of what is actually happening right now
- Surprising or counterintuitive findings
- Direct quotes from named experts or studies
- Anything most people don't know about this topic

Ignore vague claims and marketing language.
Return a clean numbered list of concrete facts only.

Research Data:
{research_data}
"""
    return _invoke(prompt, temperature=0.3)


def write_blog(topic: str, audience: str, plan: str, research_data: str, memory: str, length: str = "medium", gap: str = "") -> str:
    time.sleep(3)
    facts = extract_facts(topic, research_data)
    length_instruction = LENGTH_GUIDE.get(length, LENGTH_GUIDE["medium"])
    gap_section = f"\nContent Gap (what existing articles miss — your blog must address this):\n{gap}\n" if gap else ""

    prompt = f"""
You are a writer who has contributed to The Atlantic, Wired, Harvard Business Review, and Vox. You write for humans, not algorithms.

Topic: {topic}
Target Audience: {audience}
Length: {length_instruction}

Blog Plan:
{plan}
{gap_section}
Verified Facts (use these — do not invent statistics):
{facts}

Past Context (from memory):
{memory}

Rules — non-negotiable:

Opening:
- First sentence must be specific. A stat, a contradiction, a scene, or an uncomfortable truth.
- No "In today's world..." or "Have you ever wondered..." ever.
- Talk directly to the reader's exact situation.

Body:
- Every section makes one distinct point. No filler sections.
- After every stat or fact, explain what it means for the reader.
- At least one strong analogy that makes something complex feel simple.
- Short paragraphs — 2 to 4 lines. White space matters.
- Plain text section headings. No hashtags, no bold markers, no emojis.
- Depth is non-negotiable at any length. Short does not mean shallow.
- Natural transitions — each section flows into the next.

Tone:
- Match tone to topic and audience.
- Direct. Cut anything that doesn't move the reader forward.
- No corporate speak: "leverage", "synergy", "revolutionize" — banned.
- Smart friend explaining something, not a content marketer.

Conclusion:
- One sharp, specific statement the reader hasn't heard before.
- No "In conclusion..." No recycling the intro.
- No clichés. No question endings. End with a statement that lands.

No hashtags or emojis. Blank line between sections.

Write the full blog now.
"""
    return _invoke(prompt, temperature=0.6)


def critique_and_rewrite(blog: str, topic: str, audience: str) -> str:
    prompt = f"""
You are a senior editor from Wired and The Atlantic. Ruthless about quality.

Topic: {topic}
Target Audience: {audience}

Rewrite this blog as the final published version. Fix:
- Weak or generic opening — replace with something that grabs immediately
- Any stat dropped without explanation — add the "so what"
- Any cliché — cut it, replace with something specific
- Any filler section — make it earn its place or cut it
- Weak conclusion — one sharp, memorable final thought
- Choppy transitions — smooth them

Check:
- At least one strong analogy?
- Every paragraph moves the reader forward?
- Conclusion leaves the reader with something new?

Rules:
- No hashtags or emojis
- Plain text headings
- Short paragraphs, blank line between sections
- No clichés: "journey not a destination", "unlock potential", "game changer" — banned
- Write like a smart human, not a content farm

Return only the final blog. No commentary.

Original Blog:
{blog}
"""
    return _invoke(prompt, temperature=0.6)


def score_blog(blog: str, topic: str, seo: dict) -> dict:
    prompt = f"""
You are a professional blog quality analyst. Score objectively. Be honest, not generous.

Topic: {topic}

Blog:
{blog}

SEO Metadata:
{seo}

Score each from 1 to 10 with a one-line reason:

Readability: (short clear sentences? easy to follow?)
Hook Strength: (does the opening grab immediately with something specific?)
Content Depth: (real data, named examples, specific facts?)
SEO Strength: (focus keyword used naturally? meta title compelling?)
Conclusion Quality: (memorable and specific, not a cliché?)

Overall Score: (average of the 5, out of 10)
Verdict: (one sharp sentence — what it does well and what would push it higher)

Return each on its own line with label followed by colon. Nothing else.
"""
    raw = _invoke(prompt, temperature=0.0)
    scores = {}
    for line in raw.strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            scores[key.strip()] = value.strip()
    return scores


def generate_extras(blog: str, topic: str) -> dict:
    prompt = f"""
You are an editorial designer. Given this blog, generate three things:

1. TL;DR — exactly 3 bullet points summarizing the most important takeaways. Each bullet is one sharp sentence. No fluff.
2. Pull Quote — pick the single most powerful, quotable sentence from the blog. It should be something that makes a reader stop and think.
3. Key Takeaway — one bold, specific sentence that captures the core message of the entire blog. Not a summary — a conclusion that lands.

Topic: {topic}

Blog:
{blog}

Return in this exact format:
TL;DR:
- [bullet 1]
- [bullet 2]
- [bullet 3]
Pull Quote: [the sentence]
Key Takeaway: [the sentence]
"""
    raw = _invoke(prompt, temperature=0.3)
    extras = {"tldr": [], "pull_quote": "", "key_takeaway": ""}

    lines = raw.strip().split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("- "):
            extras["tldr"].append(line[2:].strip())
        elif line.lower().startswith("pull quote:"):
            extras["pull_quote"] = line.partition(":")[2].strip()
        elif line.lower().startswith("key takeaway:"):
            extras["key_takeaway"] = line.partition(":")[2].strip()

    return extras


def generate_seo(topic: str, blog: str) -> dict:
    word_count = len(blog.split())
    read_time = max(1, round(word_count / 200))

    prompt = f"""
You are an SEO specialist writing for both search engines and real humans.

Blog topic: "{topic}"

Generate in plain text (no hashtags, no emojis, no numbering):

Meta Title: (under 60 characters — specific and compelling, not just the topic name)
Meta Description: (under 160 characters — tell the reader exactly what value they get)
Focus Keyword: (single most searchable keyword phrase)
Secondary Keywords: (5 long-tail keyword phrases, comma separated)
Suggested Tags: (5 to 7 tags, comma separated)

Blog:
{blog}

Return each on its own line with label followed by colon. Nothing else.
"""
    raw = _invoke(prompt, temperature=0.3)
    seo = {}
    for line in raw.strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            seo[key.strip()] = value.strip().rstrip(":")
    seo["Estimated Read Time"] = f"{read_time} min read"
    return seo
