from state import AgentState

ALL_TASKS = [
    # Phase 1: Firebase & Shared Setup
    "1.1_firebase_init",
    "1.2_types",
    "1.3_rules",
    "1.4_functions",
    "1.5_qa_firebase",
    # Phase 2: Flutter Mobile (ArenaGo)
    "2.1_theme",
    "2.2_router",
    "2.3_splash",
    "2.4_login",
    "2.5_otp",
    "2.6_models",
    "2.7_home",
    "2.8_turf_detail",
    "2.9_slot_widgets",
    "2.10_booking_summary",
    "2.11_payment",
    "2.12_booking_confirmed",
    "2.13_my_bookings",
    "2.14_profile",
    "2.15_shared",
    "2.16_qa_flutter",
    # Phase 3: Next.js Web (TurfPro Ground Control)
    "3.1_firebase_web",
    "3.2_globals_css",
    "3.3_login_page",
    "3.4_admin_layout",
    "3.5_admin_dashboard",
    "3.6_turfs_pages",
    "3.7_owners_page",
    "3.8_payments_page",
    "3.9_owner_layout",
    "3.10_owner_slots",
    "3.11_owner_bookings",
    "3.12_ebills",
    "3.13_qa_web",
    # Phase 4: File Writing
    "4.1_write_files",
]

PHASE_MAP = {
    "1": "firebase",
    "2": "flutter",
    "3": "web",
    "4": "write",
}

QA_TASKS = {"1.5_qa_firebase", "2.16_qa_flutter", "3.13_qa_web"}
WRITE_TASKS = {"4.1_write_files"}


def orchestrator_node(state: AgentState) -> AgentState:
    """
    Pops the next task from the queue, sets current_task, current_phase,
    and next_agent. When queue is empty, routes to END.
    """
    queue = list(state.get("task_queue", []))

    if not queue:
        print("\n[DONE] Orchestrator: All tasks complete! Routing to END.")
        return {**state, "next_agent": "end", "current_task": "done"}

    task = queue.pop(0)
    phase_prefix = task.split(".")[0]
    phase = PHASE_MAP.get(phase_prefix, "firebase")

    if task in QA_TASKS:
        next_agent = "qa_agent"
    elif task in WRITE_TASKS:
        next_agent = "file_writer"
    elif phase == "firebase":
        next_agent = "firebase_agent"
    elif phase == "flutter":
        next_agent = "flutter_agent"
    elif phase == "web":
        next_agent = "web_agent"
    else:
        next_agent = "file_writer"

    print(f"\n[TASK] Orchestrator → [{next_agent}] Task: {task}")

    return {
        **state,
        "task_queue": queue,
        "current_task": task,
        "current_phase": phase,
        "next_agent": next_agent,
    }

