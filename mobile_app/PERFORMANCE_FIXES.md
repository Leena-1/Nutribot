# Performance & Auth Flow Fixes

## Summary of changes

### 1. **Signup / Login flow**
- **Timeout**: Auth (signUp/signIn) now times out after **10 seconds**. On timeout, user sees a clear error and loading always stops.
- **Loading state**: `setState(() => _isLoading = false)` is always called in a **finally** block (and in the screen’s own try/catch/finally), so the spinner never gets stuck.
- **Navigation**: On success we use **`Navigator.pushAndRemoveUntil(..., (route) => false)`** so the stack is cleared and the user cannot go back to login/signup with the back button.
- **Double submit**: Buttons are disabled while `_isLoading` is true; loading is set at the start of the handler.
- **Success feedback**: A short success SnackBar is shown after navigating (e.g. “Account created! Welcome.” / “Welcome back!”).
- **Error handling**: All errors (including timeout and exceptions) are caught and shown in a SnackBar; no silent failures.

### 2. **Auth provider**
- **Timeout**: `AuthProvider.signUp()` and `signIn()` wrap the auth service call in **`.timeout(Duration(seconds: 10))`**. On timeout they return an error string instead of hanging.
- **Finally**: Both methods use **try/catch/finally**. In **finally** they always set `_isLoading = false` and call `notifyListeners()`, so the UI always leaves the loading state.
- **Debug logging**: `AppLogger` is used for: request start, success, timeout, errors, and “finished (loading=false)”.

### 3. **Navigation**
- After successful signup or login we **no longer** use `Navigator.pushReplacementNamed(context, '/home')`.
- We now use:
  ```dart
  Navigator.pushAndRemoveUntil(
    context,
    MaterialPageRoute<void>(builder: (_) => const HomeScreen()),
    (route) => false,
  );
  ```
- This clears the entire stack (splash, welcome, login/signup) and leaves only `HomeScreen`, so back does not return to auth screens.

### 4. **Performance**
- **Auth init**: `AuthProvider.initialize()` and `UsageProvider.loadUsage()` are started in **`WidgetsBinding.instance.addPostFrameCallback`** so the first frame paints immediately (e.g. splash) and auth/usage load in the background.
- **Heavy work**: Auth and API work remain async; no extra blocking work was added in the UI. Loading states are set/reset so the UI stays responsive.
- **Signup screen**: Removed `flutter_animate` from the signup screen to reduce rebuild cost; layout and behavior are unchanged.
- **Const / static**: Used `const` and `static` where it was easy (e.g. disease list, padding) to avoid unnecessary allocations.

### 5. **API layer**
- **Logging**: API calls use **`AppLogger.api`** and **`AppLogger.timing`** for:
  - Start of request (with attempt number)
  - Response status code
  - Response time in ms
  - Errors
- **Timeout / retry**: Existing 30s timeout and retry logic are unchanged; only logging was added.
- **Cache**: Cache hits are logged with `AppLogger.api('predict_food: cache hit')` for easier debugging.

### 6. **Debug logging**
- **`lib/utils/app_logger.dart`**:
  - `AppLogger.auth(message, [detail])` – auth flow
  - `AppLogger.api(message, [detail])` – API
  - `AppLogger.nav(message)` – navigation
  - `AppLogger.error(tag, error, [stack])` – errors
  - `AppLogger.timing(label, duration)` – timings
- Logs are printed only in **debug** builds (`kDebugMode`).

### 7. **UX**
- Signup/Login buttons are **disabled** while loading (`onPressed: _isLoading ? null : _handleSignup`).
- Loading indicator is a **small `CircularProgressIndicator`** (22x22) inside the button.
- Back button and “Sign In” / “Sign Up” links are disabled while loading to avoid double navigation.
- Error SnackBars use **`behavior: SnackBarBehavior.floating`** and a red background; success uses green.

---

## Files touched

| File | Changes |
|------|--------|
| `lib/utils/app_logger.dart` | **New** – central debug logging |
| `lib/providers/auth_provider.dart` | Timeout (10s), try/catch/finally, logging |
| `lib/screens/signup_screen.dart` | try/catch/finally, pushAndRemoveUntil, success toast, no animate |
| `lib/screens/login_screen.dart` | Same pattern as signup |
| `lib/services/api_service.dart` | AppLogger + timing in _retryRequest |
| `lib/main.dart` | Auth and usage init deferred to post-frame callback |

---

## How to verify

1. **Signup**
   - Fill form and tap Sign Up.
   - Loading shows, then either:
     - Success: navigate to Home, success SnackBar, back button does nothing.
     - Error: SnackBar with message, loading stops, can tap again.
   - In debug console you should see `[AUTH] SignUp: request start`, then either success + `[NAV] Signup: navigating to Home` or error.

2. **Timeout**
   - Simulate slow auth (e.g. turn off network before signup if using Firebase).
   - After 10 seconds you should see a timeout message and loading should stop.

3. **API**
   - Trigger a predict or chat request.
   - In debug console you should see `[API] ... start`, `[TIMING] ... ms`, and `[API] ... statusCode=...`.

---

## Optional next steps

- Reduce API timeout from 30s to 15s if you want faster failure on slow networks.
- Add analytics or crash reporting and send `AppLogger` output there in release.
- If Firebase is slow, consider moving to a fully local-only auth path and skip Firebase for development.
