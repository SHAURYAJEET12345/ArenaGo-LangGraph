from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    # Current task being worked on
    current_task: str
    current_phase: str          # "firebase" | "flutter" | "web" | "qa" | "write"

    # Task tracking
    task_queue: List[str]       # All tasks remaining
    completed_tasks: List[str]  # Tasks done

    # Generated code storage (filename -> code content)
    generated_files: Dict[str, str]

    # QA feedback
    qa_feedback: Optional[str]
    qa_approved: bool

    # Routing
    next_agent: str             # which node to go to next

    # Config passed to agents
    razorpay_test_key: str      # embedded in payment_screen.dart

    # Final output
    output_dir: str             # where to write files
