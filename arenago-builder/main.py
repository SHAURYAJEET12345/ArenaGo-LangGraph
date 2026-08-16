# -*- coding: utf-8 -*-
"""
ArenaGo LangGraph Multi-Agent Builder
======================================
Entry point that wires everything together and runs the graph.

Usage:
  cd arenago-builder
  python main.py
"""

import os
import sys
import time
import io

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ── Validate required API keys ────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
RAZORPAY_TEST_KEY = os.getenv("RAZORPAY_TEST_KEY", "rzp_test_REPLACE_ME")

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not set in .env. Please add it and retry.")
    sys.exit(1)

print("API keys loaded.")
print(f"  Groq key: {GROQ_API_KEY[:12]}...")
print(f"  Gemini key: {'set' if GOOGLE_API_KEY else 'NOT SET (will use Groq only)'}")
print(f"  Razorpay key: {RAZORPAY_TEST_KEY[:15]}...")
sys.stdout.flush()

# ── Import graph AFTER env is loaded ─────────────────────────────
from graph import build_graph
from state import AgentState
from agents.orchestrator import ALL_TASKS

# ── Output directory ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "output")
OUTPUT_DIR = os.path.normpath(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"\nOutput directory: {OUTPUT_DIR}")
print(f"Total tasks: {len(ALL_TASKS)}")
print("=" * 60)
sys.stdout.flush()


def main():
    start_time = time.time()

    # ── Initial state ─────────────────────────────────────────────
    initial_state: AgentState = {
        "current_task":      "",
        "current_phase":     "",
        "task_queue":        ALL_TASKS.copy(),
        "completed_tasks":   [],
        "generated_files":   {},
        "qa_feedback":       None,
        "qa_approved":       False,
        "next_agent":        "orchestrator",
        "razorpay_test_key": RAZORPAY_TEST_KEY,
        "output_dir":        OUTPUT_DIR,
    }

    print("\nStarting LangGraph ArenaGo builder...\n")
    sys.stdout.flush()

    graph = build_graph()
    final_state = initial_state

    try:
        for event in graph.stream(initial_state, {"recursion_limit": 300}):
            for node_name, node_state in event.items():
                if node_name == "__end__":
                    final_state = node_state
                elif isinstance(node_state, dict):
                    final_state = node_state
                    completed = node_state.get("completed_tasks", [])
                    total = len(ALL_TASKS)
                    print(f"  [Progress] {len(completed)}/{total} tasks done", flush=True)
            sys.stdout.flush()

    except Exception as e:
        print(f"\nERROR during graph execution: {e}")
        import traceback
        traceback.print_exc()

    elapsed = time.time() - start_time
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("ArenaGo LangGraph Builder Complete!")
    print(f"Time taken: {mins}m {secs}s")
    completed = final_state.get("completed_tasks", [])
    generated = final_state.get("generated_files", {})
    print(f"Tasks completed: {len(completed)}/{len(ALL_TASKS)}")
    print(f"Files generated: {len(generated)}")
    print(f"QA feedback: {final_state.get('qa_feedback', 'N/A')}")
    print(f"\nAll files saved to: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("  1. cd ../output/arena-go && flutter pub get && flutter run")
    print("  2. cd ../output/web-dashboard && npm install && npm run dev")
    print("  3. cd ../output/firebase && firebase deploy --only functions,firestore:rules")
    print("=" * 60)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
