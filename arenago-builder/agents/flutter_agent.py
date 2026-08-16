import os
import time
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from prompts.flutter_prompts import FLUTTER_SYSTEM_PROMPT


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


def get_task_prompt(task: str, state: AgentState) -> str:
    rzp = state.get("razorpay_test_key", "rzp_test_REPLACE_ME")

    prompts = {
        "2.1_theme": """
Generate TWO complete Dart files for ArenaGo Flutter app:

FILE 1: arena-go/lib/app/theme/app_colors.dart
```dart
class AppColors {
  static const background = Color(0xFF0D0D0D);
  static const surface = Color(0xFF141414);
  static const card = Color(0xFF1C1C1E);
  static const accent = Color(0xFF39FF80);
  static const textPrimary = Color(0xFFFFFFFF);
  static const textSecondary = Color(0xFFA1A1AA);
  static const error = Color(0xFFFF4444);
  static const success = Color(0xFF39FF80);
}
```

FILE 2: arena-go/lib/app/theme/app_theme.dart
- ThemeData dark theme using AppColors
- Poppins font (google_fonts package)
- Custom TextTheme, AppBarTheme, ElevatedButtonTheme, CardTheme, InputDecorationTheme
- Export a static ThemeData get darkTheme

Separate files with FILE: comments. No markdown fences.
""",

        "2.2_router": """
Generate arena-go/lib/app/router.dart using go_router package.

Routes:
  /             -> SplashScreen
  /login        -> LoginScreen
  /otp          -> OtpScreen (extra: { phone: String, verificationId: String })
  /home         -> HomeScreen
  /turf/:id     -> TurfDetailScreen (param: id)
  /booking-summary -> BookingSummaryScreen (extra: { turfId, slots, totalAmount, totalAdvancePaid })
  /payment      -> PaymentScreen (extra: booking data map)
  /booking-confirmed -> BookingConfirmedScreen (extra: { bookingId: String })
  /my-bookings  -> MyBookingsScreen
  /profile      -> ProfileScreen

- Use GoRouter with redirect: if not logged in, go to /login (except /login and /otp)
- Use FirebaseAuth.instance.currentUser for auth check
- Export final goRouter = GoRouter(...)
Full Dart file. No markdown fences.
""",

        "2.3_splash": """
Generate arena-go/lib/features/auth/presentation/splash_screen.dart

SplashScreen:
- Black background (#0D0D0D)
- Centered column:
  - Custom paint or Icon for arena logo (use Icons.sports_soccer as placeholder)
  - "ArenaGo" text in bold Poppins, color #39FF80, fontSize 36
  - Small subtitle "Book your turf, own the game" in white, fontSize 14
- After 2.5 seconds:
  - If FirebaseAuth.instance.currentUser != null -> context.go('/home')
  - Else -> context.go('/login')
- Use initState + Future.delayed

Full Dart file. No markdown fences.
""",

        "2.4_login": """
Generate arena-go/lib/features/auth/presentation/login_screen.dart

LoginScreen:
- Dark background, Poppins font
- Logo + "ArenaGo" at top
- Title: "Welcome Back" subtitle: "Enter your phone number to continue"
- Phone number TextField with +91 prefix, number keyboard
- Gradient "Send OTP" ElevatedButton (background: #39FF80, text: black)
- Uses firebase_auth PhoneAuth: verifyPhoneNumber -> codeSent -> context.go('/otp', extra: {...})
- Show CircularProgressIndicator while loading
- Show SnackBar on error
- Handle all auth exceptions

Full Dart file, strict null safety. No markdown fences.
""",

        "2.5_otp": """
Generate arena-go/lib/features/auth/presentation/otp_screen.dart

OtpScreen:
- Receives { phone: String, verificationId: String } from GoRouterState.extra
- Show "Verify OTP" title, "Sent to +91XXXXXXXXXX" subtitle
- 6-digit OTP input (use individual TextField per digit or one TextField with maxLength:6)
- "Verify" button in #39FF80 accent
- On verify: PhoneAuthCredential -> signInWithCredential
  - Create/update Firestore users/{uid} doc
  - context.go('/home')
- "Resend OTP" text button with 30s countdown timer
- Show loading/error states

Full Dart file, strict null safety. No markdown fences.
""",

        "2.6_models": """
Generate TWO Dart files:

FILE 1: arena-go/lib/features/home/domain/turf_model.dart
```dart
class TurfModel {
  final String id, name, address, sport;
  final double pricePerHour, rating;
  final List<String> photos;
  final String ownerId;
  final bool isActive;
  
  TurfModel({required...});
  factory TurfModel.fromFirestore(DocumentSnapshot doc) {...}
  Map<String, dynamic> toMap() {...}
}
```

FILE 2: arena-go/lib/features/home/domain/slot_model.dart
```dart
class SlotModel {
  final String id, turfId, date, startTime, endTime;
  final bool isBooked;
  final String? bookingId;
  
  SlotModel({required...});
  factory SlotModel.fromFirestore(DocumentSnapshot doc) {...}
  Map<String, dynamic> toMap() {...}
}
```

Separate with FILE: comments. Full Dart code, strict null safety. No markdown fences.
""",

        "2.7_home": """
Generate TWO Dart files:

FILE 1: arena-go/lib/features/home/presentation/home_screen.dart
- Dark theme, Poppins font
- AppBar with "ArenaGo" logo + profile icon
- Search bar at top (TextField with search icon, grey fill)
- StreamBuilder reading turfs collection from Firestore (isActive==true)
- ListView of TurfCard widgets
- BottomNavigationBar: Home, My Bookings, Profile
- Riverpod consumer for auth state
- Sport filter chips: All, Cricket, Football, Badminton, Tennis

FILE 2: arena-go/lib/features/home/presentation/widgets/turf_card.dart
- Card with dark background (#1C1C1E)
- Image at top (CachedNetworkImage or Image.network)
- Turf name, address, sport chip, price per hour
- Star rating + "₹{pricePerHour}/hr" 
- Rounded corners, subtle green border accent
- onTap -> context.go('/turf/' + turf.id)

Separate with FILE: comments. Full Dart code, strict null safety. No markdown fences.
""",

        "2.8_turf_detail": """
Generate arena-go/lib/features/turf_detail/presentation/turf_detail_screen.dart

TurfDetailScreen:
- Receives turfId from GoRouterState.pathParameters
- Fetch turf from Firestore
- Hero image at top (network image, full width, 220px height)
- Back button overlay on image
- Turf name (bold, white, 24px), address, sport, rating stars
- "₹{price}/hr" prominently in #39FF80
- "Select Date" section: horizontal date picker row (next 7 days)
- "Available Slots" section: grid of time slots (SlotGrid widget)
  - Each slot: "10:00 - 11:00", green if available, grey if booked
  - Multi-select slots
- "Book Now" bottom button (sticky): opens BookingSummaryScreen
  - Passes: turfId, turfName, selectedSlots, totalAmount, advancePaid
- StreamBuilder for slots from Firestore

Full Dart file, strict null safety. No markdown fences.
""",

        "2.9_slot_widgets": """
Generate TWO Dart files:

FILE 1: arena-go/lib/features/turf_detail/presentation/widgets/date_picker_row.dart
- Horizontal scrollable row of date chips
- Each chip shows: day name (Mon), date (15), month (Aug)
- Selected date chip: #39FF80 background, black text
- Unselected: dark card (#1C1C1E), white text
- Callback: onDateSelected(String date) where date is "YYYY-MM-DD"
- Shows next 7 days

FILE 2: arena-go/lib/features/turf_detail/presentation/widgets/slot_grid.dart
- GridView.builder with 3 columns
- Each slot tile: time range text, colored based on isBooked
  - Available: border color #39FF80, dark bg, tappable
  - Booked: grey bg, grey text, disabled
  - Selected: #39FF80 bg, black text
- Supports multi-select (List<SlotModel> selectedSlots)
- Callback: onSlotToggled(SlotModel slot)

Separate with FILE: comments. Full Dart code. No markdown fences.
""",

        "2.10_booking_summary": """
Generate arena-go/lib/features/booking/presentation/booking_summary_screen.dart

BookingSummaryScreen:
- Receives from GoRouterState.extra: { turfId, turfName, turfAddress, sport, slots[], totalAmount, totalAdvancePaid, totalDue }
- Display booking summary card:
  - Turf name + address
  - Sport icon + name
  - Selected slots list with date and time
  - Price breakdown: Total ₹{totalAmount}, Advance ₹{totalAdvancePaid}, Due at venue ₹{totalDue}
- "Booking Type" toggle: Instant / Pre (updates totalAdvancePaid)
- Terms & conditions checkbox
- "Proceed to Payment" button (accent #39FF80):
  - Navigate to /payment with full booking data as extra
- Dark theme, clean card-based layout

Full Dart file, strict null safety. No markdown fences.
""",

        "2.11_payment": f"""
Generate arena-go/lib/features/booking/presentation/payment_screen.dart

This is PROTOTYPE - Razorpay TEST MODE only. Never real money.
Razorpay test key: {rzp}

PaymentScreen:
- Receives booking data from GoRouterState.extra (same as BookingSummaryScreen)
- Show "Payment" AppBar
- Payment summary card:
  - Turf name, slots, sport
  - "Advance to Pay: ₹{{totalAdvancePaid}}" in large #39FF80 text
  - "Remaining at venue: ₹{{totalDue}}"
- Payment method info row (Razorpay handles UI - just show "Secure Payment via Razorpay")
- "Pay ₹{{totalAdvancePaid}} Now" button in #39FF80

Razorpay Integration:
- import 'package:razorpay_flutter/razorpay_flutter.dart';
- Initialize Razorpay in initState:
  _razorpay = Razorpay();
  _razorpay.on(Razorpay.EVENT_PAYMENT_SUCCESS, _handlePaymentSuccess);
  _razorpay.on(Razorpay.EVENT_PAYMENT_ERROR, _handlePaymentError);
  _razorpay.on(Razorpay.EVENT_EXTERNAL_WALLET, _handleExternalWallet);
- On "Pay Now" button press:
  var options = {{
    'key': '{rzp}',
    'amount': totalAdvancePaid * 100,  // in paise
    'currency': 'INR',
    'name': 'ArenaGo',
    'description': slot details string,
    'prefill': {{'contact': userPhone, 'email': 'user@arenago.app'}},
    'theme': {{'color': '#39FF80'}},
  }};
  _razorpay.open(options);

- _handlePaymentSuccess(PaymentSuccessResponse response):
  1. Write to Firestore bookings collection:
     bookings.add({{
       'userId': FirebaseAuth.instance.currentUser!.uid,
       'turfId': turfId,
       'turfName': turfName,
       'turfAddress': turfAddress,
       'sport': sport,
       'slots': slots.map((s) => s.toMap()).toList(),
       'bookingType': bookingType,
       'totalAmount': totalAmount,
       'totalAdvancePaid': totalAdvancePaid,
       'totalDue': totalDue,
       'paymentStatus': 'success',
       'bookingStatus': 'confirmed',
       'paymentId': response.paymentId,
       'createdAt': FieldValue.serverTimestamp(),
     }})
  2. Update each slot: slots/{{slotId}}.isBooked = true, bookingId = newBookingId
  3. context.go('/booking-confirmed', extra: {{'bookingId': newBookingId}})

- _handlePaymentError: Show SnackBar "Payment failed: {{response.message}}"
- dispose(): _razorpay.clear()

Full Dart file, strict null safety. No markdown fences.
""",

        "2.12_booking_confirmed": """
Generate arena-go/lib/features/booking/presentation/booking_confirmed_screen.dart

BookingConfirmedScreen:
- Receives { bookingId: String } from GoRouterState.extra
- Fetch booking from Firestore using bookingId
- Show success animation (use AnimatedContainer with a checkmark, color #39FF80)
- "Booking Confirmed! 🎉" title in large white bold text
- Booking details card: turf name, sport, date & time, advance paid, booking ID
- "paymentId: pay_test_XXXXX" shown (confirms test mode worked)
- Two buttons:
  - "View My Bookings" -> context.go('/my-bookings')
  - "Back to Home" -> context.go('/home')
- Dark theme, confetti-like dots in background (use CustomPaint or simple colored circles)

Full Dart file, strict null safety. No markdown fences.
""",

        "2.13_my_bookings": """
Generate arena-go/lib/features/profile/presentation/my_bookings_screen.dart

MyBookingsScreen:
- StreamBuilder: Firestore bookings where userId == currentUser.uid, orderBy createdAt desc
- TabBar: Upcoming | Completed | Cancelled
- Each booking card:
  - Turf name + sport icon
  - Date & time slot
  - BookingStatus badge (confirmed=green, cancelled=red, completed=grey)
  - PaymentStatus badge (success=green, pending=orange, failed=red)
  - "View Details" -> show bottom sheet with full booking info
  - "Cancel Booking" button (only for upcoming confirmed bookings)
    - Show confirmation dialog
    - Update Firestore: bookingStatus = "cancelled", cancellationReason = "User cancelled"
- Empty state: illustration + "No bookings yet. Book your first turf!"
- Dark theme

Full Dart file, strict null safety. No markdown fences.
""",

        "2.14_profile": """
Generate arena-go/lib/features/profile/presentation/profile_screen.dart

ProfileScreen:
- Fetch user from Firestore users/{uid}
- Top section: CircleAvatar (gradient fill with initials), display name, phone number
- Menu items with arrow:
  - My Bookings
  - Notifications
  - Help & Support
  - About ArenaGo
  - Privacy Policy
- Sign Out button (red, at bottom) -> FirebaseAuth.signOut() -> context.go('/login')
- Version text at very bottom: "ArenaGo v1.0.0 • Test Mode"
- Dark theme, clean list tiles

Full Dart file, strict null safety. No markdown fences.
""",

        "2.15_shared": """
Generate TWO Dart files:

FILE 1: arena-go/lib/shared/widgets/custom_button.dart
- CustomButton StatelessWidget
- Parameters: label (String), onPressed (VoidCallback?), isLoading (bool), color (Color?), textColor (Color?)
- When isLoading: show CircularProgressIndicator (white) instead of label
- When disabled (onPressed==null): grey background
- Default: #39FF80 background, black text
- Rounded corners (BorderRadius 12), full width, height 52px

FILE 2: arena-go/lib/shared/widgets/loading_overlay.dart
- LoadingOverlay StatelessWidget
- Parameters: isLoading (bool), child (Widget)
- When isLoading: Stack with child + semi-transparent overlay + CircularProgressIndicator centered
- Color: Colors.black54 overlay, #39FF80 indicator

Separate with FILE: comments. Full Dart code. No markdown fences.
""",
    }
    return prompts.get(task, f"Generate Flutter Dart code for task {task}. Use ArenaGo dark theme (#0D0D0D bg, #39FF80 accent). Full code, no explanations.")


def task_to_filename(task: str) -> str:
    mapping = {
        "2.1_theme":               "arena-go/lib/app/theme/app_colors.dart",
        "2.2_router":              "arena-go/lib/app/router.dart",
        "2.3_splash":              "arena-go/lib/features/auth/presentation/splash_screen.dart",
        "2.4_login":               "arena-go/lib/features/auth/presentation/login_screen.dart",
        "2.5_otp":                 "arena-go/lib/features/auth/presentation/otp_screen.dart",
        "2.6_models":              "arena-go/lib/features/home/domain/turf_model.dart",
        "2.7_home":                "arena-go/lib/features/home/presentation/home_screen.dart",
        "2.8_turf_detail":         "arena-go/lib/features/turf_detail/presentation/turf_detail_screen.dart",
        "2.9_slot_widgets":        "arena-go/lib/features/turf_detail/presentation/widgets/slot_grid.dart",
        "2.10_booking_summary":    "arena-go/lib/features/booking/presentation/booking_summary_screen.dart",
        "2.11_payment":            "arena-go/lib/features/booking/presentation/payment_screen.dart",
        "2.12_booking_confirmed":  "arena-go/lib/features/booking/presentation/booking_confirmed_screen.dart",
        "2.13_my_bookings":        "arena-go/lib/features/profile/presentation/my_bookings_screen.dart",
        "2.14_profile":            "arena-go/lib/features/profile/presentation/profile_screen.dart",
        "2.15_shared":             "arena-go/lib/shared/widgets/custom_button.dart",
    }
    return mapping.get(task, f"arena-go/lib/unknown/{task}.dart")


def invoke_with_fallback(task: str, state: AgentState) -> str:
    prompt = get_task_prompt(task, state)
    messages = [("system", FLUTTER_SYSTEM_PROMPT), ("human", prompt)]

    for attempt, use_fallback in enumerate([False, True]):
        try:
            llm = get_llm(use_fallback=use_fallback)
            provider = "Gemini" if use_fallback else "Groq"
            print(f"   [LLM] Flutter Agent using {provider}...")
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            err = str(e)
            if "rate" in err.lower() or "429" in err:
                print(f"   [WARN]  Rate limit, waiting 15s...")
                time.sleep(15)
                if use_fallback:
                    return f"// RATE LIMITED - could not generate {task}\n"
            elif attempt == 0:
                print(f"   [WARN]  Groq error: {err[:80]}. Falling back to Gemini...")
            else:
                print(f"   [ERROR] Both LLMs failed: {err[:80]}")
                return f"// ERROR generating {task}: {err}\n"
    return f"// Could not generate {task}\n"


def flutter_agent_node(state: AgentState) -> AgentState:
    task = state["current_task"]
    print(f"   [FLUTTER] Flutter Agent processing: {task}")

    code = invoke_with_fallback(task, state)
    filename = task_to_filename(task)

    generated = dict(state.get("generated_files", {}))
    generated[filename] = code
    completed = list(state.get("completed_tasks", []))
    completed.append(task)

    print(f"   [OK] Flutter Agent done: {filename}")
    return {**state, "generated_files": generated, "completed_tasks": completed}


