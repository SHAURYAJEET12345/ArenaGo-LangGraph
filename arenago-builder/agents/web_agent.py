import os
import time
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from prompts.web_prompts import WEB_SYSTEM_PROMPT


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
    "3.1_firebase_web": """
Generate web-dashboard/lib/auth-context.tsx for TurfPro Ground Control Next.js app.

Requirements:
- 'use client' directive
- AuthContext with: user (User | null), loading (boolean), isAdmin (boolean), isOwner (boolean), signOut()
- Read custom claims from ID token to determine isAdmin / isOwner
- useAuth() hook
- AuthProvider component
- onAuthStateChanged listener
- Auto redirect to /login if not authenticated (use useRouter)

Full TypeScript file. No markdown fences.
""",

    "3.2_globals_css": """
Generate web-dashboard/app/globals.css for TurfPro Ground Control.

Requirements:
- @import url for Inter font from Google Fonts
- CSS variables:
  --bg: #F7F9FB
  --sidebar: #1B4332
  --accent: #40916C
  --card: #FFFFFF
  --border: #E2E8F0
  --text: #191C1E
  --text-muted: #6B7280
  --danger: #DC2626
  --success: #16A34A
- Tailwind base/components/utilities directives
- Custom scrollbar styles (thin, #40916C thumb)
- Smooth transitions on all elements
- Base body styles with Inter font

Full CSS file. No markdown fences.
""",

    "3.3_login_page": """
Generate web-dashboard/app/login/page.tsx for TurfPro Ground Control.

Requirements:
- 'use client' directive  
- Split layout: left panel (dark green #1B4332) with branding, right panel with login form
- Left panel: TurfPro logo (emoji + text), tagline "Ground Control for Turf Owners"
- Right panel white: "Sign In" title, email + password inputs, "Login" button in #40916C
- Firebase Auth: signInWithEmailAndPassword
- On success: redirect to /admin if admin, /owner if owner (check custom claims)
- Show loading state, error messages
- "Forgot password?" link
- Full TypeScript. No markdown fences.
""",

    "3.4_admin_layout": """
Generate web-dashboard/app/admin/layout.tsx for TurfPro Ground Control admin section.

Requirements:
- Server component (no 'use client' needed)
- Sidebar navigation (#1B4332 background):
  - Logo: "TurfPro" with small pitch icon
  - Nav items with Heroicons: Dashboard, Turfs, Owners, Payments, Settings
  - Active item: #40916C background, white text
  - Bottom: User info + Sign Out
- Top navbar: Page title, notification bell, user avatar
- Main content area with padding
- Protected route: redirect to /login if not admin
- Responsive: sidebar collapsible on mobile
Full TypeScript. No markdown fences.
""",

    "3.5_admin_dashboard": """
Generate web-dashboard/app/admin/page.tsx for TurfPro Ground Control admin dashboard.

Requirements:
- 'use client' directive
- Stats cards row (4 cards):
  - Total Turfs (count from Firestore turfs collection)
  - Total Bookings (count from bookings collection)
  - Revenue This Month (sum of totalAdvancePaid where bookingStatus=confirmed, current month)
  - Active Owners (count of users with owner role)
- Each card: white bg, border, icon, number, label, small % change badge
- Recent Bookings table:
  - Columns: Booking ID, User, Turf, Date, Amount, Status, Payment Status
  - Last 10 bookings from Firestore
  - Status badges with colors
- Quick Actions section: "Add New Turf", "View All Bookings" buttons
- Use Firestore onSnapshot for real-time updates
Full TypeScript. No markdown fences.
""",

    "3.6_turfs_pages": """
Generate THREE Next.js pages for turf management:

FILE 1: web-dashboard/app/admin/turfs/page.tsx
- 'use client'
- Table of all turfs from Firestore
- Columns: Name, Address, Sport, Price/hr, Owner, Status (Active/Inactive), Actions
- Search bar to filter by name
- "Add New Turf" button -> /admin/turfs/new
- Edit / Toggle Active buttons per row
- Pagination (10 per page)

FILE 2: web-dashboard/app/admin/turfs/new/page.tsx
- 'use client'
- Form to create new turf:
  - Name, Address, Sport (select), Price per hour, Owner (select from owners list)
  - Photo URL fields (up to 3)
  - isActive toggle
- Submit -> Firestore turfs.add(...)
- Validation with inline errors

FILE 3: web-dashboard/app/admin/turfs/[id]/page.tsx
- 'use client'
- Edit existing turf (fetch by id from params)
- Same form as new, pre-filled
- Update + Delete buttons

Separate with FILE: comments. Full TypeScript. No markdown fences.
""",

    "3.7_owners_page": """
Generate web-dashboard/app/admin/owners/page.tsx for TurfPro Ground Control.

Requirements:
- 'use client'
- Table of all users where role = "owner"
- Columns: Name, Phone, Email, Turfs Count, Bookings Count, Joined Date, Actions
- "Add Owner" -> open modal form (name, phone, email, assign turfs)
- Firebase: create user + set custom claims owner=true
- Search and filter
- Suspend/Activate owner toggle
Full TypeScript. No markdown fences.
""",

    "3.8_payments_page": """
Generate web-dashboard/app/admin/payments/page.tsx for TurfPro Ground Control.

Requirements:
- 'use client'
- DISPLAY ONLY - no payment processing on web side
- Table of all bookings with payment info:
  Columns: Booking ID, User Phone, Turf Name, Sport, Date/Time, Total Amount,
           Advance Paid, Due at Venue, Payment Status, Booking Status, Payment ID, Actions
- paymentStatus badge: success=green pill, pending=yellow pill, failed=red pill
- bookingStatus badge: confirmed=blue, completed=grey, cancelled=red
- Filter by: date range, status, turf
- Export to CSV button
- Summary cards: Total Collected, Pending Amount, Failed Payments count
- Real-time Firestore listener
Full TypeScript. No markdown fences.
""",

    "3.9_owner_layout": """
Generate TWO files for owner section:

FILE 1: web-dashboard/app/owner/layout.tsx
- Sidebar for turf owners (#1B4332):
  - "TurfPro Owner" header
  - Nav: Dashboard, My Slots, Bookings, E-Bills
  - Protected: redirect to /login if not owner role
- Top bar with turf name

FILE 2: web-dashboard/app/owner/page.tsx
- 'use client'
- Owner dashboard:
  - Today's bookings count card
  - This week's revenue card
  - Upcoming bookings list (next 5)
  - Slot availability summary (booked vs available today)
  - Quick links to Slots and Bookings

Separate with FILE: comments. Full TypeScript. No markdown fences.
""",

    "3.10_owner_slots": """
Generate web-dashboard/app/owner/slots/page.tsx for TurfPro owner portal.

Requirements:
- 'use client'
- Weekly calendar grid view (Mon-Sun, time slots 6AM-10PM)
- Each cell shows: booked (green) or available (white/grey)
- Click available slot -> open modal to manually mark as unavailable (block slot)
- Click booked slot -> show booking details (user, sport, payment status)
- Date navigation: Previous week / Next week buttons
- Legend: Available, Booked, Blocked
- Fetch slots from Firestore for owner's turfId
Full TypeScript. No markdown fences.
""",

    "3.11_owner_bookings": """
Generate web-dashboard/app/owner/bookings/page.tsx for TurfPro owner portal.

Requirements:
- 'use client'
- Table of bookings for owner's turf(s) only
- Columns: Booking ID, User Phone, Sport, Date, Time Slots, Amount, Advance Paid, Status
- Status filter tabs: All, Upcoming, Completed, Cancelled
- "Mark as Completed" button for confirmed bookings
- Download booking details
- Real-time Firestore updates
Full TypeScript. No markdown fences.
""",

    "3.12_ebills": """
Generate web-dashboard/app/owner/ebills/page.tsx for TurfPro owner portal.

Requirements:
- 'use client'
- Table of e-bills from Firestore ebills collection (filtered by ownerId)
- Columns: Invoice ID, Booking ID, Turf Name, Date, Amount, Status, Actions
- "Generate E-Bill" button -> calls Firebase callable function generateEBill
- "Download PDF" button (open invoice in new tab as printable HTML)
- Invoice preview modal: show invoice details cleanly formatted
- Total revenue summary at top
Full TypeScript. No markdown fences.
""",
}


def task_to_filename(task: str) -> str:
    mapping = {
        "3.1_firebase_web":   "web-dashboard/lib/auth-context.tsx",
        "3.2_globals_css":    "web-dashboard/app/globals.css",
        "3.3_login_page":     "web-dashboard/app/login/page.tsx",
        "3.4_admin_layout":   "web-dashboard/app/admin/layout.tsx",
        "3.5_admin_dashboard":"web-dashboard/app/admin/page.tsx",
        "3.6_turfs_pages":    "web-dashboard/app/admin/turfs/page.tsx",
        "3.7_owners_page":    "web-dashboard/app/admin/owners/page.tsx",
        "3.8_payments_page":  "web-dashboard/app/admin/payments/page.tsx",
        "3.9_owner_layout":   "web-dashboard/app/owner/layout.tsx",
        "3.10_owner_slots":   "web-dashboard/app/owner/slots/page.tsx",
        "3.11_owner_bookings":"web-dashboard/app/owner/bookings/page.tsx",
        "3.12_ebills":        "web-dashboard/app/owner/ebills/page.tsx",
    }
    return mapping.get(task, f"web-dashboard/app/unknown/{task}.tsx")


def invoke_with_fallback(task: str) -> str:
    prompt = TASK_PROMPTS.get(task, f"Generate Next.js TypeScript code for task: {task}")
    messages = [("system", WEB_SYSTEM_PROMPT), ("human", prompt)]

    for attempt, use_fallback in enumerate([False, True]):
        try:
            llm = get_llm(use_fallback=use_fallback)
            provider = "Gemini" if use_fallback else "Groq"
            print(f"   [LLM] Web Agent using {provider}...")
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            err = str(e)
            if "rate" in err.lower() or "429" in err:
                print(f"   [WARN]  Rate limit, waiting 15s...")
                time.sleep(15)
            elif attempt == 0:
                print(f"   [WARN]  Groq error: {err[:80]}. Falling back to Gemini...")
            else:
                print(f"   [ERROR] Both LLMs failed: {err[:80]}")
                return f"// ERROR generating {task}: {err}\n"
    return f"// Could not generate {task}\n"


def web_agent_node(state: AgentState) -> AgentState:
    task = state["current_task"]
    print(f"   [WEB] Web Agent processing: {task}")

    code = invoke_with_fallback(task)
    filename = task_to_filename(task)

    generated = dict(state.get("generated_files", {}))
    generated[filename] = code
    completed = list(state.get("completed_tasks", []))
    completed.append(task)

    print(f"   [OK] Web Agent done: {filename}")
    return {**state, "generated_files": generated, "completed_tasks": completed}


