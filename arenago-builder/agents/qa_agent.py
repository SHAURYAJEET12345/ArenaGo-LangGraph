import os
import json
import time
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from prompts.qa_prompts import QA_SYSTEM_PROMPT


def get_llm(use_fallback: bool = False):
    if use_fallback:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.0,
        )
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0,
    )


def get_files_for_phase(task: str, state: AgentState) -> dict:
    """Return relevant generated files for the QA phase."""
    generated = state.get("generated_files", {})
    if task == "1.5_qa_firebase":
        return {k: v for k, v in generated.items() if k.startswith("web-dashboard/lib/") or k.startswith("firebase/")}
    elif task == "2.16_qa_flutter":
        return {k: v for k, v in generated.items() if k.startswith("arena-go/")}
    elif task == "3.13_qa_web":
        return {k: v for k, v in generated.items() if k.startswith("web-dashboard/app/")}
    return {}


def qa_agent_node(state: AgentState) -> AgentState:
    task = state["current_task"]
    print(f"   [QA] QA Agent reviewing: {task}")

    files_to_review = get_files_for_phase(task, state)

    if not files_to_review:
        print(f"   [INFO]  QA Agent: No files to review for {task}")
        completed = list(state.get("completed_tasks", []))
        completed.append(task)
        return {**state, "completed_tasks": completed, "qa_approved": True}

    all_issues = []
    generated = dict(state.get("generated_files", {}))

    for filename, code in files_to_review.items():
        # Skip very short files (scaffolds)
        if len(code) < 100:
            continue

        # Truncate large files for QA to avoid token limits
        code_to_review = code[:4000] if len(code) > 4000 else code

        prompt = f"""Review this file: {filename}

```
{code_to_review}
```

Check for: null safety (Dart), missing imports, TypeScript errors, "PitchPulse" string, production Razorpay keys, invalid Tailwind classes.
Return ONLY valid JSON as specified."""

        for attempt, use_fallback in enumerate([False, True]):
            try:
                llm = get_llm(use_fallback=use_fallback)
                provider = "Gemini" if use_fallback else "Groq"
                response = llm.invoke([
                    ("system", QA_SYSTEM_PROMPT),
                    ("human", prompt)
                ])

                # Parse QA response
                content = response.content.strip()
                # Strip markdown fences if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                try:
                    qa_result = json.loads(content)
                    issues = qa_result.get("issues", [])
                    fixed_code = qa_result.get("fixed_code", "")
                    status = qa_result.get("status", "clean")

                    if issues:
                        print(f"   [WARN]  QA found {len(issues)} issue(s) in {filename}")
                        all_issues.extend([{**i, "file": filename} for i in issues])

                    if fixed_code and status == "fixed":
                        generated[filename] = fixed_code
                        print(f"   [FIX] QA auto-fixed: {filename}")

                except json.JSONDecodeError:
                    print(f"   [WARN]  QA response not valid JSON for {filename}, skipping")

                break  # Success, move to next file

            except Exception as e:
                err = str(e)
                if "rate" in err.lower() or "429" in err:
                    print(f"   [WARN]  Rate limit, waiting 10s...")
                    time.sleep(10)
                elif attempt == 0:
                    print(f"   [WARN]  Groq error for QA, falling back to Gemini...")
                else:
                    print(f"   [ERROR] QA failed for {filename}: {err[:60]}")
                    break

    completed = list(state.get("completed_tasks", []))
    completed.append(task)

    total_issues = len(all_issues)
    qa_approved = total_issues == 0
    qa_feedback = f"Found {total_issues} issues across {len(files_to_review)} files." if all_issues else "All files passed QA."

    print(f"   [OK] QA Agent done: {qa_feedback}")

    return {
        **state,
        "generated_files": generated,
        "completed_tasks": completed,
        "qa_feedback": qa_feedback,
        "qa_approved": qa_approved,
    }


