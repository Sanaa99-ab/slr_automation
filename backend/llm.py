# llm.py
from openai import OpenAI
from typing import Optional
from config import config

client = OpenAI(
    base_url=config.OPENAI_BASE_URL,
    api_key=config.GITHUB_TOKEN
)

def generate_research_questions(topic: str) -> list[str]:
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert researcher helping to automate Systematic Literature Reviews."},
                {"role": "user", "content": f"Generate 3 concise research questions for a Systematic Literature Review on '{topic}'. Format each question as a single sentence starting with 'How', 'What', or 'To what extent', separated by newlines."}
            ],
            model=config.OPENAI_MODEL,
            temperature=1,
            max_tokens=4096,
            top_p=1
        )
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split("\n") if q.strip()]
        return questions[:3] if len(questions) >= 3 else questions + [f"Fallback: What is the impact of {topic} on outcomes?"] * (3 - len(questions))
    except Exception as e:
        return [
            f"Error: Could not generate questions ({str(e)})",
            f"Fallback: What is the impact of {topic} on X?",
            f"Fallback: How does {topic} influence Y?"
        ]

# def generate_search_queries(topic: str, questions: list[str]) -> list[str]:
#     try:
#         prompt = "Convert the following research questions into Boolean search queries suitable for academic databases:\n" + "\n".join(questions)
#         response = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": "You are an expert in crafting search queries for Systematic Literature Reviews."},
#                 {"role": "user", "content": f"{prompt}. Format each query as a single line, using AND/OR/NOT operators, separated by newlines."}
#             ],
#             model=config.OPENAI_MODEL,
#             temperature=0.5,  # More structured output
#             max_tokens=150,
#             top_p=1
#         )
#         queries_text = response.choices[0].message.content.strip()
#         queries = [q.strip() for q in queries_text.split("\n") if q.strip()]
#         return queries[:3] if len(queries) >= 3 else queries + [f"Fallback: {questions[0].split()[2:4]} AND impact"] * (3 - len(queries))
#     except Exception as e:
#         return [
#             f"Error: Could not generate queries ({str(e)})",
#             f"Fallback: {topic} AND research",
#             f"Fallback: {topic} AND outcomes"
        # ]
def generate_search_queries(topic: Optional[str], questions: list[str]) -> list[str]:
    try:
        prompt = "Convert the following research questions into Boolean search queries suitable for academic databases:\n" + "\n".join(questions)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in crafting search queries for Systematic Literature Reviews."},
                {"role": "user", "content": f"{prompt}. Format each query as a single line, using AND/OR/NOT operators, separated by newlines."}
            ],
            model=config.OPENAI_MODEL,
            temperature=0.5,
            max_tokens=150,
            top_p=1
        )
        queries_text = response.choices[0].message.content.strip()
        queries = [q.strip() for q in queries_text.split("\n") if q.strip()]
        if len(queries) >= 3:
            return queries[:3]
        else:
            # Use topic if available; otherwise use a default fallback
            fallback = f"Fallback: {(topic or 'research')} AND impact"
            return queries + [fallback] * (3 - len(queries))
    except Exception as e:
        return [
            f"Error: Could not generate queries ({str(e)})",
            f"Fallback: {(topic or 'research')} AND outcomes",
            f"Fallback: {(topic or 'research')} AND impact"
        ]

def propose_criteria(topic: str) -> list[str]:
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in Systematic Literature Reviews, specializing in crafting precise inclusion and exclusion criteria for scientific research."},
                {"role": "user", "content": f"For a Systematic Literature Review on '{topic}', propose 3 inclusion criteria and 2 exclusion criteria. Ensure criteria are specific, research-oriented, and relevant to academic studies. Format each as a single line starting with 'Include:' or 'Exclude:', separated by newlines."}
            ],
            model=config.OPENAI_MODEL,
            temperature=0.5,
            max_tokens=150,
            top_p=1
        )
        criteria_text = response.choices[0].message.content.strip()
        criteria = [c.strip() for c in criteria_text.split("\n") if c.strip()]
        includes = [c for c in criteria if c.startswith("Include:")][:3]
        excludes = [c for c in criteria if c.startswith("Exclude:")][:2]
        result = includes + excludes
        if len(result) < 5:
            result.extend(["Exclude: Studies lacking rigorous methodology"] * (5 - len(result)))
        return result
    except Exception as e:
        return [
            "Include: Papers in English",
            "Include: Published after 2015",
            "Include: Peer-reviewed studies",
            f"Exclude: Non-empirical articles",
            f"Error: Could not generate criteria ({str(e)})"
        ]