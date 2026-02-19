# Authentication & UI Upgrade Setup Guide

## 🎉 What's New

Your Nutribot app now includes:
- ✅ Modern Material 3 UI with animations
- ✅ Complete authentication system (Firebase + Local fallback)
- ✅ Free trial system (5 prompts each for chat & analysis)
- ✅ Feature access control
- ✅ User profile & subscription screens
- ✅ State management with Provider

---

## 📦 Installation

### 1. Install Dependencies

```bash
cd mobile_app
flutter pub get
```

### 2. Firebase Setup (Optional)

Firebase Auth is **optional**. The app works with local authentication if Firebase is not configured.

**To enable Firebase:**

1. Create a Firebase project at https://console.firebase.google.com
2. Add Android/iOS apps to your project
3. Download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
4. Place them in:
   - Android: `android/app/google-services.json`
   - iOS: `ios/Runner/GoogleService-Info.plist`
5. The app will automatically use Firebase Auth

**Without Firebase:**
- App uses secure local token storage
- All features work the same
- User data stored locally

---

## 🚀 Running the App

```bash
flutter run
```

**First Launch Flow:**
1. Splash Screen (2 seconds)
2. Welcome/Onboarding (3 pages)
3. Login Screen
4. Home Screen (after login)

---

## 🔐 Authentication Flow

### Sign Up
- Email + Password + Name
- Form validation
- Auto-login after signup
- Resets free trial usage

### Sign In
- Email + Password
- Session persistence
- Auto-redirect to home

### Logout
- Confirmation dialog
- Clears session
- Redirects to login

---

## 🎁 Free Trial System

### Guest Users (Not Logged In)
- ❌ Cannot use features
- Shows "Login Required" dialog

### Logged In Users
- ✅ 5 free chat prompts
- ✅ 5 free food analysis attempts
- ✅ Usage tracked locally
- ✅ Resets after signup/login

### After Limit Reached
- Shows "Free Trial Completed" dialog
- Prompts to sign up (if not already)
- Prompts to upgrade to premium

---

## 📱 Screen Structure

```
SplashScreen (2s)
  ↓
WelcomeScreen (onboarding)
  ↓
LoginScreen / SignupScreen
  ↓
HomeScreen
  ├── ScanScreen (Food Analysis)
  ├── ResultsScreen (History)
  ├── ChatScreen (AI Chat)
  └── ProfileScreen (User Profile)
```

---

## 🎨 UI Features

### Material 3 Design
- Modern color scheme
- Smooth animations
- Gradient backgrounds
- Glassmorphism effects

### Animations
- Page transitions
- Loading states
- Button interactions
- List animations

### Dark Mode
- Automatic system detection
- Full dark theme support

---

## 🔧 Configuration

### Backend URL
Edit `lib/services/api_service.dart`:
```dart
const String baseUrl = 'http://YOUR_IP:8000';
```

### Free Trial Limits
Edit `lib/services/usage_tracker_service.dart`:
```dart
static const int _freeLimit = 5; // Change this
```

---

## 📊 State Management

### AuthProvider
- Manages authentication state
- Handles login/signup/logout
- Provides user info

### UsageProvider
- Tracks free trial usage
- Updates UI in real-time
- Resets on login/signup

---

## 🛡️ Feature Access Control

### Protected Features
- Food Image Analysis (`ScanScreen`)
- AI Chat (`ChatScreen`)

### Access Logic
1. Check if user is authenticated
   - ❌ Not logged in → Show login dialog
   - ✅ Logged in → Continue
2. Check usage limit
   - ❌ Limit reached → Show upgrade dialog
   - ✅ Has remaining → Allow usage

---

## 🧪 Testing

### Test Authentication
1. Sign up with new email
2. Logout
3. Sign in with same credentials
4. Should work seamlessly

### Test Free Trial
1. Sign up/login
2. Use 5 chat prompts
3. Try 6th → Should show limit dialog
4. Use 5 food analyses
5. Try 6th → Should show limit dialog

### Test Access Control
1. Logout
2. Try to use chat/scan
3. Should show login dialog

---

## 🐛 Troubleshooting

### Firebase Not Working
- **Solution**: App automatically falls back to local auth
- Check console for Firebase errors
- Local auth works perfectly fine

### Usage Not Resetting
- **Solution**: Usage resets on login/signup
- Check `UsageProvider.resetUsage()` is called
- Verify SharedPreferences is working

### Navigation Issues
- **Solution**: Check route names match exactly
- Verify all screens are registered in `main.dart`
- Check navigation context is valid

---

## 📝 Code Structure

```
lib/
├── main.dart                    # App entry, routing, providers
├── models/
│   └── user_model.dart         # User data model
├── providers/
│   ├── auth_provider.dart      # Auth state management
│   └── usage_provider.dart      # Usage tracking
├── services/
│   ├── auth_service.dart       # Auth logic (Firebase + Local)
│   └── usage_tracker_service.dart # Usage storage
├── screens/
│   ├── splash_screen.dart      # Splash/loading
│   ├── welcome_screen.dart     # Onboarding
│   ├── login_screen.dart       # Login UI
│   ├── signup_screen.dart      # Signup UI
│   ├── home_screen.dart        # Main navigation
│   ├── scan_screen.dart        # Food analysis (updated)
│   ├── chat_screen.dart        # AI chat (updated)
│   ├── profile_screen.dart     # User profile
│   └── subscription_screen.dart # Premium upgrade
└── widgets/
    ├── auth_required_dialog.dart # Login prompt
    └── trial_limit_dialog.dart   # Limit reached prompt
```

---

## 🎯 Next Steps

1. **Customize UI**: Update colors, fonts in `main.dart`
2. **Add Features**: Extend profile screen, add settings
3. **Premium Integration**: Connect subscription to payment gateway
4. **Analytics**: Add Firebase Analytics (optional)
5. **Push Notifications**: Add FCM for engagement

---

## 📚 Dependencies Used

- `provider` - State management
- `firebase_core` - Firebase initialization
- `firebase_auth` - Authentication (optional)
- `google_fonts` - Beautiful typography
- `smooth_page_indicator` - Onboarding dots
- `flutter_animate` - Smooth animations
- `shared_preferences` - Local storage

---

**Status**: ✅ All features implemented and ready to use!

**Last Updated**: 2026-02-17
