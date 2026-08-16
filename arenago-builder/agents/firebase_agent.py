import os
import time
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from prompts.firebase_prompts import FIREBASE_SYSTEM_PROMPT

def get_llm(use_fallback: bool = False):
    if use_fallback:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1,
        )
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )

TASK_PROMPTS = {
    "1.1_firebase_init": """
Generate two complete files for the ArenaGo / TurfPro Ground Control project:

FILE 1: web-dashboard/lib/firebase.ts
- Initialize Firebase app with config for project turf-booking-5717d
- Export: app, auth (getAuth), db (getFirestore), storage (getStorage)
- Use environment variables: process.env.NEXT_PUBLIC_FIREBASE_*
- Full TypeScript

FILE 2: web-dashboard/lib/auth-context.tsx
- React context for Firebase Auth state
- AuthProvider wraps the app
- useAuth() hook returns { user, loading, signOut }
- 'use client' directive
- Full TypeScript

Output BOTH files with clear FILE: comments separating them. No markdown fences.
""",

    "1.2_types": """
Generate web-dashboard/lib/types.ts with TypeScript interfaces for all data models:

interface User { uid: string; phone: string; displayName: string; fcmToken?: string; createdAt: Date; }
interface Turf { id: string; name: string; address: string; sport: string; pricePerHour: number; photos: string[]; ownerId: string; rating: number; isActive: boolean; }
interface Slot { id: string; turfId: string; date: string; startTime: string; endTime: string; isBooked: boolean; bookingId?: string; }
interface Booking {
  id: string; userId: string; turfId: string; turfName: string; turfAddress: string;
  turfPhotoUrl: string; sport: string; slots: Slot[]; bookingType: 'instant' | 'pre';
  totalAmount: number; totalAdvancePaid: number; totalDue: number;
  paymentStatus: 'pending' | 'success' | 'failed';
  bookingStatus: 'confirmed' | 'cancelled' | 'completed';
  paymentId?: string; cancellationReason?: string; createdAt: Date;
}
interface Review { id: string; userId: string; turfId: string; rating: number; comment: string; createdAt: Date; }

Export all interfaces. Full TypeScript. No markdown fences.
""",

    "1.3_rules": """
Generate firebase/firestore.rules for the ArenaGo turf booking app.

Collections: users, turfs, slots, bookings, reviews

Rules:
- users: authenticated users can read/write their own document only
- turfs: anyone can read active turfs; only admin (custom claim: admin=true) can write
- slots: authenticated users can read; slot owner/admin can update isBooked field
- bookings: authenticated user can create their own; user can read own; owner can read turfs they own; admin can read all
- reviews: authenticated users can create; users can read all; users can only update/delete their own

Output only the rules file content. No markdown fences.
""",

    "1.4_functions": """
Generate 4 Firebase Cloud Functions in TypeScript. Output as one file: firebase/functions/index.ts

Import: firebase-functions v2, firebase-admin, @google-cloud/firestore

Function 1 - onBookingCreate:
  Trigger: Firestore onCreate on bookings/{bookingId}
  Action: Send FCM notification to user (token from users/{userId}.fcmToken)
         and to turf owner (token from users/{ownerId}.fcmToken)
  Message: "Booking confirmed for {turfName} on {date}"

Function 2 - onBookingCancel:
  Trigger: Firestore onUpdate on bookings/{bookingId}
  Condition: bookingStatus changed to "cancelled"
  Action: Set all slots in booking.slots[] -> isBooked=false, bookingId=null
  No refund logic.

Function 3 - generateEBill:
  Trigger: HTTPS Callable
  Input: { bookingId: string }
  Action: Fetch booking doc, generate a simple JSON invoice object
         { invoiceId, bookingId, amount, date, turfName, status }
         Store in Firestore: ebills/{bookingId}
  Return: the invoice object

Function 4 - sendBookingReminder:
  Trigger: Cloud Scheduler - every day at 8:00 AM IST (schedule: "0 2 * * *" UTC)
  Action: Query bookings where date == today AND bookingStatus == "confirmed"
          Send FCM push: "Reminder: Your ArenaGo booking at {turfName} is today!"

Full TypeScript with proper types. Admin SDK initialized once at top. No markdown fences.
""",
}


def invoke_with_fallback(task: str) -> str:
    prompt = TASK_PROMPTS.get(task, f"Generate Firebase code for task: {task}. Output complete deployable code only.")
    messages = [("system", FIREBASE_SYSTEM_PROMPT), ("human", prompt)]

    for attempt, use_fallback in enumerate([False, True]):
        try:
            llm = get_llm(use_fallback=use_fallback)
            provider = "Gemini" if use_fallback else "Groq"
            print(f"   [LLM] Firebase Agent using {provider}...")
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            err = str(e)
            if "rate" in err.lower() or "429" in err:
                print(f"   [WARN]  Rate limit on {'Groq' if not use_fallback else 'Gemini'}, waiting 10s...")
                time.sleep(10)
            elif attempt == 0:
                print(f"   [WARN]  Groq error: {err[:80]}. Falling back to Gemini...")
            else:
                print(f"   [ERROR] Both LLMs failed: {err[:80]}")
                return f"// ERROR generating {task}: {err}\n"
    return f"// Could not generate {task}\n"


def firebase_agent_node(state: AgentState) -> AgentState:
    task = state["current_task"]
    print(f"   [FIREBASE] Firebase Agent processing: {task}")

    code = invoke_with_fallback(task)

    filename_map = {
        "1.1_firebase_init": "web-dashboard/lib/firebase.ts",
        "1.2_types":         "web-dashboard/lib/types.ts",
        "1.3_rules":         "firebase/firestore.rules",
        "1.4_functions":     "firebase/functions/index.ts",
    }
    filename = filename_map.get(task, f"firebase/{task}.ts")

    generated = dict(state.get("generated_files", {}))
    generated[filename] = code
    completed = list(state.get("completed_tasks", []))
    completed.append(task)

    print(f"   [OK] Firebase Agent done: {filename}")
    return {**state, "generated_files": generated, "completed_tasks": completed}



