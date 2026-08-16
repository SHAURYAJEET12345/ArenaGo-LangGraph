# ArenaGo & TurfPro - Complete Platform

This repository contains the complete LangGraph-generated platform for ArenaGo, a turf booking system.

## Project Structure

- **`arenago-builder/`**: The Python LangGraph AI workflow used to generate this code.
- **`output/arena-go/`**: The Flutter mobile app for users.
- **`output/web-dashboard/`**: The Next.js 15 web dashboard for admins and turf owners.
- **`output/firebase/`**: The Firebase project containing Firestore security rules and Cloud Functions.

---

## 🚀 How to Run the Platform

Follow these steps to run each component locally. Ensure you have Flutter, Node.js (v22+), and the Firebase CLI installed on your system.

### 1. Database & Backend (Firebase)

The platform relies on Firebase Firestore and Cloud Functions. You need to deploy the rules and functions.

1. Install dependencies for Cloud Functions:
   ```bash
   cd output/firebase/functions
   npm install
   ```

2. Build the TypeScript functions:
   ```bash
   npm run build
   ```

3. Deploy to your Firebase project:
   ```bash
   # Make sure you are logged in to the Firebase CLI
   firebase login
   # Set your active project (replace 'your-project-id' with your actual Firebase project ID)
   firebase use your-project-id
   
   cd .. # Back to output/firebase
   firebase deploy --only functions,firestore:rules
   ```
   *Note: If you just want to test locally without deploying, you can use the Firebase Emulators: `cd functions && npm run serve`.*

### 2. Website (TurfPro Ground Control - Next.js)

The web dashboard is built with Next.js 15 App Router, React 19, and Tailwind CSS.

1. Navigate to the web directory:
   ```bash
   cd output/web-dashboard
   ```

2. Set up environment variables:
   Copy `.env.local.example` to `.env.local` and fill in your Firebase configuration keys.
   ```bash
   cp .env.local.example .env.local
   ```

3. Start the development server (uses Turbopack for faster loading):
   ```bash
   npm run dev
   ```

4. Open your browser and go to:
   **[http://localhost:3000](http://localhost:3000)**

### 3. Mobile App (ArenaGo - Flutter)

The mobile app is built with Flutter, Riverpod, go_router, and includes Razorpay for test payments.

1. Navigate to the Flutter directory:
   ```bash
   cd output/arena-go
   ```

2. Configure Firebase for Flutter:
   - Download the `google-services.json` file from your Firebase console.
   - Place it in `android/app/google-services.json`.
   - *(Optional for iOS: place `GoogleService-Info.plist` in `ios/Runner/`)*.

3. Install dependencies:
   ```bash
   flutter pub get
   ```

4. Run the app on an emulator or connected device:
   ```bash
   flutter run
   ```

---

## Technical Stack & Versions (Latest)

*   **Flutter**: ^3.27.0
*   **Next.js**: 15.5.x (App Router)
*   **React**: ^19.0.0
*   **Firebase SDK**: ^11.10.0 (Web), ^3.15.0 (Flutter Core)
*   **Firebase Functions**: Node.js 22, firebase-admin ^13.4.0
*   **Payments**: Razorpay Flutter (^1.3.9) in TEST MODE.

## Generating the Code Again

If you want the AI to regenerate the platform:
```bash
cd arenago-builder
# Ensure you have .env with GROQ_API_KEY and GEMINI_API_KEY
python main.py
```
