# ArenaGo LangGraph Multi-Agent App Builder

> **Automatically generates a full turf-booking platform using LangGraph AI agents.**

## What Gets Built

| Product | Tech | Description |
|---|---|---|
| 📱 **ArenaGo** | Flutter (Dart) | Mobile booking app, dark theme, Razorpay payments |
| 🖥️ **TurfPro Ground Control** | Next.js 14 + TypeScript | Admin + owner web dashboard |
| 🔥 **Firebase Backend** | Firestore + Functions | Rules, auth, cloud functions |

## Architecture

```
START → [Orchestrator] → routes tasks →

  Firebase Agent  →  firebase.ts, types.ts, rules, functions
  Flutter Agent   →  15 Dart files (screens, widgets, theme)
  Web Agent       →  12 Next.js pages (admin + owner portal)
  QA Agent        →  reviews & auto-fixes code
  File Writer     →  writes all files to output/

→ END
```

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Groq API key (free at https://console.groq.com)
- Optional: Google Gemini API key (fallback LLM)

### 2. Setup

```bash
cd arenago-builder
pip install langgraph langchain langchain-groq langchain-google-genai python-dotenv
```

Edit `.env`:
```
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_gemini_key_here
RAZORPAY_TEST_KEY=rzp_test_REPLACE_ME
```

### 3. Run the Builder

```bash
cd arenago-builder
python main.py
```

Watch 35 tasks complete in the terminal. All code goes to `output/`.

---

## Running the Generated Apps

### Flutter App (ArenaGo)
```bash
cd output/arena-go
flutter pub get
# Add google-services.json to android/app/
flutter run
```

### Next.js Dashboard (TurfPro Ground Control)
```bash
cd output/web-dashboard
npm install
# Copy .env.local.example to .env.local and fill Firebase config
npm run dev
# Open http://localhost:3000
```

### Firebase Deploy
```bash
cd output/firebase/functions
npm install
firebase deploy --only functions,firestore:rules
```

---

## Design System

### Flutter App (Dark Theme)
| Token | Value |
|---|---|
| Background | `#0D0D0D` |
| Surface | `#141414` |
| Card | `#1C1C1E` |
| Accent | `#39FF80` (Neon Green) |
| Font | Poppins |

### Web Dashboard (Light Theme)
| Token | Value |
|---|---|
| Background | `#F7F9FB` |
| Sidebar | `#1B4332` |
| Accent | `#40916C` |
| Font | Inter |

---

## Razorpay Test Mode

The payment screen uses Razorpay in **test mode** — no real money is charged.

**Test card:**
```
Card: 4111 1111 1111 1111
Expiry: Any future date
CVV: Any 3 digits
OTP: 1234
```

**Test UPI:**
```
success@razorpay  → always succeeds
failure@razorpay  → always fails (for error flow testing)
```

---

## LangGraph Agents

| Agent | Generates | LLM |
|---|---|---|
| Firebase Agent | `firebase.ts`, `types.ts`, `firestore.rules`, 4 Cloud Functions | Groq → Gemini |
| Flutter Agent | 15 Dart files (theme, router, 10 screens, widgets) | Groq → Gemini |
| Web Agent | 12 Next.js pages (admin dashboard, owner portal) | Groq → Gemini |
| QA Agent | Reviews all code, auto-fixes issues | Groq → Gemini |
| File Writer | Writes to disk | No LLM |

---

*ArenaGo + TurfPro Ground Control — Built with LangGraph multi-agent system*
