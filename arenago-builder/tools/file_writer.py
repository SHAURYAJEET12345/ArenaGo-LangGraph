import os
from state import AgentState


def file_writer_node(state: AgentState) -> AgentState:
    """
    Writes all generated files from state['generated_files'] to disk.
    Creates all necessary directories.
    """
    task = state["current_task"]
    output_dir = state.get("output_dir", "output")
    generated = state.get("generated_files", {})

    print(f"\n   [FILES] File Writer: Writing {len(generated)} files to '{output_dir}/'...")

    written_count = 0
    errors = []

    for relative_path, content in generated.items():
        full_path = os.path.join(output_dir, relative_path)
        try:
            # Create parent directories
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Write the file
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            written_count += 1
            print(f"   [WRITE]  Written: {relative_path}")

        except Exception as e:
            error_msg = f"Failed to write {relative_path}: {e}"
            errors.append(error_msg)
            print(f"   [ERROR] {error_msg}")

    # Write scaffold files that aren't LLM-generated
    _write_scaffold_files(output_dir)

    print(f"\n   [OK] File Writer: {written_count}/{len(generated)} files written successfully.")
    if errors:
        print(f"   [WARN]  {len(errors)} errors occurred.")

    completed = list(state.get("completed_tasks", []))
    completed.append(task)

    return {**state, "completed_tasks": completed}


def _write_scaffold_files(output_dir: str):
    """Write non-LLM scaffold files: pubspec.yaml, package.json, firebase.json, etc."""

    scaffolds = {
        "arena-go/pubspec.yaml": _flutter_pubspec(),
        "arena-go/lib/main.dart": _flutter_main(),
        "web-dashboard/package.json": _web_package_json(),
        "web-dashboard/next.config.js": _next_config(),
        "web-dashboard/tailwind.config.js": _tailwind_config(),
        "web-dashboard/tsconfig.json": _tsconfig(),
        "web-dashboard/.env.local.example": _env_example(),
        "firebase/firebase.json": _firebase_json(),
        "firebase/functions/package.json": _functions_package_json(),
        "firebase/functions/tsconfig.json": _functions_tsconfig(),
    }

    for relative_path, content in scaffolds.items():
        full_path = os.path.join(output_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if not os.path.exists(full_path):  # Don't overwrite LLM-generated files
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"   [SCAFFOLD]  Scaffold: {relative_path}")


def _flutter_pubspec() -> str:
    return """name: arena_go
description: ArenaGo - Turf Booking App
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  # Firebase
  firebase_core: ^3.1.0
  firebase_auth: ^5.1.0
  cloud_firestore: ^5.1.0
  firebase_storage: ^12.1.0
  firebase_messaging: ^15.0.0
  # State Management & Navigation
  flutter_riverpod: ^2.5.1
  go_router: ^14.1.4
  # Payment
  razorpay_flutter: ^1.3.6
  # UI
  google_fonts: ^6.2.1
  cached_network_image: ^3.3.1
  # Utilities
  intl: ^0.19.0
  equatable: ^2.0.5

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

flutter:
  uses-material-design: true
"""


def _flutter_main() -> str:
    return """import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app/router.dart';
import 'app/theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(const ProviderScope(child: ArenaGoApp()));
}

class ArenaGoApp extends ConsumerWidget {
  const ArenaGoApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'ArenaGo',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routerConfig: goRouter,
    );
  }
}
"""


def _web_package_json() -> str:
    return """{
  "name": "turfpro-ground-control",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "firebase": "^10.12.3",
    "@heroicons/react": "^2.1.5",
    "typescript": "^5.5.3"
  },
  "devDependencies": {
    "@types/node": "^20.14.12",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.19",
    "eslint": "^8.57.0",
    "eslint-config-next": "14.2.5",
    "postcss": "^8.4.40",
    "tailwindcss": "^3.4.6"
  }
}
"""


def _next_config() -> str:
    return """/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['firebasestorage.googleapis.com', 'storage.googleapis.com'],
  },
};

module.exports = nextConfig;
"""


def _tailwind_config() -> str:
    return """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        sidebar: '#1B4332',
        accent: '#40916C',
        'accent-light': '#52B788',
        'bg-app': '#F7F9FB',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
"""


def _tsconfig() -> str:
    return """{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
"""


def _env_example() -> str:
    return """# Copy this to .env.local and fill in your Firebase config
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=turf-booking-5717d.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=turf-booking-5717d
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=turf-booking-5717d.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
"""


def _firebase_json() -> str:
    return """{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "functions": {
    "predeploy": ["npm --prefix functions run build"],
    "source": "functions",
    "runtime": "nodejs20"
  },
  "hosting": {
    "public": "public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"]
  }
}
"""


def _functions_package_json() -> str:
    return """{
  "name": "arenago-functions",
  "scripts": {
    "build": "tsc",
    "serve": "npm run build && firebase emulators:start --only functions",
    "deploy": "firebase deploy --only functions"
  },
  "main": "lib/index.js",
  "dependencies": {
    "firebase-admin": "^12.2.0",
    "firebase-functions": "^5.0.1"
  },
  "devDependencies": {
    "typescript": "^5.4.5"
  },
  "private": true
}
"""


def _functions_tsconfig() -> str:
    return """{
  "compilerOptions": {
    "module": "commonjs",
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "outDir": "lib",
    "sourceMap": true,
    "strict": true,
    "target": "es2017"
  },
  "compileOnSave": true,
  "include": ["src"]
}
"""

