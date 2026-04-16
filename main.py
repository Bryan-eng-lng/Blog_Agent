from agent import plan_blog, research, write_blog, critique_and_rewrite, generate_seo, fix_cliches, score_blog, analyze_competitor_gap, generate_extras
from memory import store_memory, retrieve_memory


def separator():
    print("\n" + "-" * 60 + "\n")


print("Blog Writer Agent")
print("Type 'exit' to stop.\n")

while True:

    topic = input("Enter blog topic: ").strip()

    if topic.lower() == "exit":
        break

    audience = input("Target audience (press Enter for 'general readers'): ").strip()
    if not audience:
        audience = "general readers"

    length = input("Blog length — short / medium / long (press Enter for 'medium'): ").strip().lower()
    if length not in ("short", "medium", "long"):
        length = "medium"

    separator()

    print("Step 1 — Planning the blog...")
    plan = plan_blog(topic, audience)
    print(plan)

    separator()

    print("Step 2 — Researching the topic...")
    research_data = research(topic)
    print("Research complete.")

    separator()

    print("Step 3 — Analyzing competitor gap...")
    gap = analyze_competitor_gap(topic)
    print(gap)

    separator()

    print("Step 4 — Retrieving memory...")
    memory = retrieve_memory(topic)
    if memory.strip():
        print("Relevant past context found.")
    else:
        print("No past context found.")

    separator()

    print(f"Step 5 — Writing {length} draft...")
    draft = write_blog(topic, audience, plan, research_data, memory, length=length, gap=gap)
    print(draft)

    separator()

    print("Step 6 — Critiquing and rewriting...")
    final_blog = critique_and_rewrite(draft, topic, audience)

    separator()

    print("Step 7 — Removing cliches...")
    final_blog = fix_cliches(final_blog, topic)
    print(final_blog)

    separator()

    print("Step 8 — Generating SEO metadata...")
    seo = generate_seo(topic, final_blog)
    for key, value in seo.items():
        print(f"{key}: {value}")

    separator()

    print("Step 9 — Generating TL;DR, pull quote, and key takeaway...")
    extras = generate_extras(final_blog, topic)
    print(f"TL;DR:")
    for bullet in extras["tldr"]:
        print(f"  - {bullet}")
    print(f"Pull Quote: {extras['pull_quote']}")
    print(f"Key Takeaway: {extras['key_takeaway']}")

    separator()

    print("Step 10 — Scoring the blog...")
    scores = score_blog(final_blog, topic, seo)
    for key, value in scores.items():
        print(f"{key}: {value}")

    separator()

    store_memory(topic)
    store_memory(final_blog)
    print("Blog saved to memory.")

    safe_topic = "".join(c if c.isalnum() or c in " _-" else "" for c in topic).strip().replace(" ", "_")
    filename = f"{safe_topic[:50]}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write(f"Target Audience: {audience}\n\n")
        f.write(f"Length: {length}\n\n")
        f.write(f"Read Time: {seo.get('Estimated Read Time', 'N/A')}\n\n")
        f.write("---\n\n")
        f.write("## TL;DR\n\n")
        for bullet in extras["tldr"]:
            f.write(f"- {bullet}\n")
        f.write("\n---\n\n")
        f.write(final_blog)
        f.write("\n\n---\n\n")
        f.write(f"> **{extras['pull_quote']}**\n\n")
        f.write("---\n\n")
        f.write(f"**Key Takeaway:** {extras['key_takeaway']}\n\n")
        f.write("---\n\n")
        f.write("## SEO Metadata\n\n")
        for key, value in seo.items():
            f.write(f"{key}: {value}\n")
        f.write("\n\n## Blog Score\n\n")
        for key, value in scores.items():
            f.write(f"{key}: {value}\n")

    print(f"Blog saved to: {filename}")

    separator()
