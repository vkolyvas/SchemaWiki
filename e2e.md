# WeddingWise.gr — End-to-End Element Audit

> Generated: 2026-04-24
> Scope: Full codebase scan — backend (all modules) + frontend (pages, components, lib)
> Validators: 3 independent scanner agents ran in parallel; findings cross-referenced

---

## Element Naming Conventions

| Prefix | Meaning |
|--------|---------|
| `[FE]` | Frontend element (React component / page / lib) |
| `[BE]` | Backend element (Express route / controller / service / model / repository / middleware / utils) |
| `[DB]` | Database schema / table |
| `[EXT]` | External service / third-party integration |

---

## Element Index

### Frontend (FE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| Home (page.js) | frontend/src/app/page.js | lucide-react, next/link | — | Side-effect: renders landing page with hero, planning tools, vendor CTAs | ACTIVE | Client component. Static marketing page with demo page links. |
| MyWeddingPage | frontend/src/app/my-wedding/page.js | weddingsAPI, checklistAPI, budgetAPI, guestsAPI, vendorsAPI, conversationsAPI, isAuthenticated, getCurrentUser | — | Side-effect: dashboard with stats, planning tools, budget tracker, guest list, saved vendors, messages, timeline | ACTIVE | Client component. Fetches multiple APIs in parallel. Vendor role redirects to /vendor/dashboard. Auto-creates wedding if none exists. |
| CalendarPage | frontend/src/app/my-wedding/calendar/page.js | weddingsAPI, checklistAPI, bookingRequestsAPI, isAuthenticated, getCurrentUser | — | Side-effect: calendar with tasks + vendor bookings, stats grid | ACTIVE | Client component. Vendor redirect check on mount. |
| BudgetPage | frontend/src/app/my-wedding/budget/page.js | weddingsAPI, budgetAPI, isAuthenticated, getCurrentUser | — | Side-effect: budget overview with expense tracking, category breakdown, Greek benchmarks | ACTIVE | Client component. sanitizeInput removes SQL injection chars. Vendor redirect. |
| ChecklistPage | frontend/src/app/my-wedding/checklist/page.js | weddingsAPI, checklistAPI, isAuthenticated, getCurrentUser | — | Side-effect: task CRUD, priority/date sorting, search, progress tracking | ACTIVE | Client component. loadDefaultChecklist generates 44 recommended tasks. Inline date picker per task. |
| GuestsPage | frontend/src/app/my-wedding/guests/page.js | weddingsAPI, guestsAPI, isAuthenticated, getCurrentUser | — | Side-effect: RSVP management, Excel import/export via xlsx library | ACTIVE | Client component. Uses xlsx for Excel. sanitizeValue prevents formula injection. |
| SeatingChartPage | frontend/src/app/my-wedding/seating-chart/page.js | seatingAPI, weddingsAPI, guestsAPI, isAuthenticated, getCurrentUser, apiFetch, BlueprintCanvas, TableAssignmentPanel | — | Side-effect: interactive seating chart editor with drag-drop, PDF/Excel export, blueprint upload | ACTIVE | Client component. Debounced save (1s). html2canvas for image export. Uses BlueprintCanvas + TableAssignmentPanel. |
| SecurityPage | frontend/src/app/my-wedding/security/page.js | isAuthenticated, getCurrentUser | — | Side-effect: active sessions management, device info, session revocation | ACTIVE | Client component. Direct fetch with credentials:include. 401 → redirect to signin. |
| AuthCallbackPage | frontend/src/app/auth/callback/page.js | authAPI, apiFetch | — | Side-effect: OAuth callback, stores user in localStorage, dispatches auth-change event, redirects by role | ACTIVE | Client component. Handles Google OAuth callback. Dispatches auth-change for Header update. |
| BillingPage | frontend/src/app/billing/page.js | billingAPI | — | Side-effect: subscription dashboard, transaction history, invoice download | ACTIVE | Client component. Uses SubscriptionStatus. handleManageSubscription opens Stripe portal. |
| MessagesPage | frontend/src/app/messages/page.js | conversationsAPI, isAuthenticated, getCurrentUser | — | Side-effect: conversations inbox with search, unread indicators, vendor avatars | ACTIVE | Client component. Normalizes vendor_id to string. Routes to /messages/[vendor_id]. |
| Header | frontend/src/components/Header.jsx | isAuthenticated, getCurrentUser, authAPI, notificationsAPI, notificationsStream | — | Side-effect: nav header with auth state, notifications dropdown, user menu, mobile responsive | ACTIVE | Client component. Subscribes to notificationsStream for unread count (SSE singleton). Dispatches auth-change on logout. |
| BlueprintCanvas | frontend/src/components/BlueprintCanvas.jsx | — | tables (array, req), guests (array, req), layoutElements (array, opt), blueprintUrl (string, opt), displaySettings (object, opt), onAddTable (fn, opt), onUpdateTable (fn, opt), onDeleteTable (fn, opt), onSelectTable (fn, opt) | Side-effect: interactive seating chart canvas with drag-drop tables, rotation handles, guest assignment | ACTIVE | Client component. Mouse + touch drag, rotation, keyboard delete. 10 table types, 32 layout element types. |
| TableAssignmentPanel | frontend/src/components/TableAssignmentPanel.jsx | — | table (object, req), guests (array, req), unassignedGuests (array, req), onAssignGuest (fn, req), onUnassignGuest (fn, req) | Side-effect: side panel for guest-to-table assignment | ACTIVE | Client component. Part of seating chart editor. |
| SubscriptionStatus | frontend/src/components/billing/SubscriptionStatus.js | billingAPI | subscription (object, req), onManage (fn, opt) | Side-effect: subscription status card with plan name, billing cycle, cancel option | ACTIVE | Client component. Shows free/paid tier. Handles cancelSubscription with confirmation. |
| notificationsStream | frontend/src/lib/notificationsStream.js | SSE_URL, EventSource | authRequired (boolean, opt) | Return: SSE connection singleton | ACTIVE | Singleton SSE connection shared across Header, BottomNav. Auth flag must be set before subscribe. |
| apiFetch | frontend/src/lib/api.js | fetchAPI, API_BASE, encryptPassword, uploadImageToStorage | path (string, req), options (object, opt) | Return: Promise<JSON>; 401 triggers auth flow; retry on 502/503/504 for GET | ACTIVE | Central API wrapper with retry logic, 401 debouncing, CSRF token handling. |
| authAPI | frontend/src/lib/api.js | fetchAPI, encryptPassword, localStorage | userData (object, req) | Return: register, login, logout, getMe, refreshToken, verifyEmail, resendVerification, deleteAccount, recoverAccount | ACTIVE | Passwords encrypted before sending. Tokens in HTTP-only cookies. |
| weddingsAPI | frontend/src/lib/api.js | fetchAPI | weddingData (object, req) | Return: getAll, getActive, getById, create, update, getStats, collaborators CRUD | ACTIVE | Central weddings API used by all my-wedding pages. |
| guestsAPI | frontend/src/lib/api.js | fetchAPI | weddingId (string\|number, req), guestData (object, req) | Return: getAll, getById, create, update, delete, bulkImport, getRsvpSummary, updateRsvp | ACTIVE | Used by guests page and seating chart. |
| budgetAPI | frontend/src/lib/api.js | fetchAPI | weddingId (string\|number, req) | Return: getBudget, saveBudget, expenses CRUD, getBenchmarks | ACTIVE | Used by budget page. |
| checklistAPI | frontend/src/lib/api.js | fetchAPI | weddingId (string\|number, req) | Return: getChecklist, generate, tasks CRUD, toggleTask | ACTIVE | Used by checklist page and my-wedding dashboard. |
| conversationsAPI | frontend/src/lib/api.js | fetchAPI | vendorId (string, req), content (string, req) | Return: startConversation, getConversations, getMessages, sendMessage, markAsRead, archive, delete | ACTIVE | Unified conversations API. Also provides backward-compatible messagesAPI wrapper. |
| billingAPI | frontend/src/lib/api.js | fetchAPI | planId (string, opt) | Return: getPlans, getSubscription, createSubscription, cancelSubscription, getPortalUrl, Stripe/PayPal ops, getTransactions, getInvoices | ACTIVE | Stripe + PayPal payment integrations. |
| seatingAPI | frontend/src/lib/api.js | fetchAPI | weddingId (string\|number, req) | Return: getSeating, saveLayout, table CRUD, assignGuest | ACTIVE | Used by seating chart page. |
| ContactRoute | frontend/src/app/api/contact/route.js | — | name (string, req), email (string, req), subject (string, req), message (string, req) | Return: POST handler — validates fields, logs submission, returns success JSON | ACTIVE | Server route. Currently logs only — no DB/email integration. Validates required fields + email format. |

---

### Backend — Auth Module (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| authenticate (middleware) | modules/auth/middleware/auth.middleware.js | jwt, role.service, authToken.repository | req, res, next (JWT_SECRET env) | Side-effect: attaches req.user, calls next() or 401/503 | ACTIVE | Extracts token from cookie or Bearer header, verifies JWT, checks is_deleted/status, validates tokenVersion via Redis+DB (503 if unavailable), touches session last_activity. |
| requireRole (middleware) | modules/auth/middleware/auth.middleware.js | role.service | allowedRoles (array, req) | Side-effect: returns 401/403/503 or calls next() | ACTIVE | Fast path: JWT claim check. Authoritative path: deriveRoleFromDB (fail-closed). |
| authSessionController | modules/auth/controllers/authSession.controller.js | authSessionService, cookie.util, AppError | req, res | Side-effect: HTTP response with user data or cookies | ACTIVE | login, logout, refresh, getActiveSessions, revokeSession handlers. Delegates to authSessionService. |
| authRegistrationController | modules/auth/controllers/authRegistration.controller.js | authRegistrationService, cookie.util | req, res | Side-effect: HTTP 201/200 with user+wedding data | ACTIVE | register, verifyEmail, resendVerification handlers. |
| authPasswordController | modules/auth/controllers/authPassword.controller.js | authPasswordService | req, res | Side-effect: HTTP JSON response | ACTIVE | forgotPassword, resetPassword handlers. |
| authProfileController | modules/auth/controllers/authProfile.controller.js | authProfileService | req, res | Side-effect: HTTP JSON with user profile | ACTIVE | me handler — pure read. |
| authOAuthController | modules/auth/controllers/authOAuth.controller.js | authTokenService, cookie.util | req, res (FRONTEND_URL env) | Side-effect: redirect to frontend callback with cookies set | ACTIVE | googleCallback — handles Google OAuth callback. |
| authSessionService | modules/auth/services/authSession.service.js | User, authTokenService, bcrypt, decryption, AppError | email (string, req, JWT_REFRESH_SECRET env), password (string, req), clientIp (string, opt), deviceMeta (object, opt) | Return: {user, accessToken, refreshToken, sessionId} | ACTIVE | login (5-attempt lockout / 15min), logout (revokes session), refresh (rotate), getActiveSessions, revokeSession. |
| authRegistrationService | modules/auth/services/authRegistration.service.js | User, Wedding, authTokenService, authVerificationService, email.service, bcrypt | first_name (string, req, FRONTEND_URL env), last_name (string, req), email (string, req), password (string, req), password_confirmation (string, req), wedding_date (string, opt), locale (string, opt), wedding_website (object, opt) | Return: {user, wedding, accessToken, refreshToken} | ACTIVE | register (creates user+wedding), verifyEmail, resendVerification. Email verification required. Wedding bootstrap if website data provided. |
| authPasswordService | modules/auth/services/authPassword.service.js | User, email.service, bcrypt, crypto | email (string, req), token (string, opt), newPassword (string, opt) | Return: success message string | ACTIVE | initiateReset (enumeration-safe — always same msg), resetPassword (validates token+password, invalidates sessions). |
| authProfileService | modules/auth/services/authProfile.service.js | User | userId (string, req) | Return: user profile object (no password) | ACTIVE | Pure read, no side effects. |
| authVerificationService | modules/auth/services/authVerification.service.js | User, crypto | userId (string, req), token (string, opt) | Return: verification token string or boolean | ACTIVE | generateToken (24h expiry), validateToken, markEmailVerified. |
| authTokenService | modules/auth/services/authToken.service.js | authTokenRepository, role.service, token.util, uuid, AppError | userId (string, req, JWT_SECRET, JWT_REFRESH_SECRET, JWT_REFRESH_EXPIRES_IN env), email (string, req), tokenVersion (number, opt), deviceMeta (object, opt), role (string, opt) | Return: {accessToken, refreshToken, sessionId} | ACTIVE | issueTokens, rotateRefreshToken (1-per-user, preserves sid), revokeToken, revokeAllTokens, getActiveSessions, revokeSessionBySid. parseDuration helper for Xd/Xh/Xm/Xs format. |
| roleService | modules/auth/services/role.service.js | database/connection, redis.client, AppError | userId (string, req, NODE_ENV env) | Return: role string ('user'\|'vendor') | ACTIVE | deriveRoleFromDB (Redis cache 2min+TTL jitter, fail-closed on DB error), isVendorUser, invalidateRoleCache, getTokenVersion (Redis 1min TTL), invalidateTokenVersionCache. Redis failures are non-fatal. |
| User model | modules/auth/models/user.model.js | database/connection, crypto | — | — | ACTIVE | create, findById, findByEmail, findByEmailIncludingDeleted, updateById (ALLOWED_UPDATE_COLUMNS whitelist), deleteById, findAll, findByWeddingId. Token/recovery/verification methods: save/has/deleteRefreshToken, getFailedLoginCount, clearFailedLoginAttempts, save/findVerificationToken, save/findPasswordResetToken, consumeRecoveryToken, incrementTokenVersion (updates Redis cache). |
| authTokenRepository | modules/auth/repositories/authToken.repository.js | database/connection, token.util | — | — | ACTIVE | saveRefreshToken (atomic delete-then-insert, 1-per-user), hasRefreshToken, deleteByHash, deleteAllForUser, cleanupExpired. Session methods: createSession, getActiveSessions, revokeSession, isSessionRevoked, getSessionBySid, deleteSession, revokeAllSessions, touchSession (throttled 5min), flagAccountSuspicious, deleteRevokedSessions. |
| generateAccessToken | modules/auth/utils/token.util.js | jsonwebtoken | userId (string, req, JWT_SECRET, JWT_EXPIRES_IN env), email (string, req), tokenVersion (number, opt), sessionId (string, opt), role (string, opt) | Return: JWT access token string | ACTIVE | Signs JWT with userId, email, tokenVersion, role, sid. |
| generateRefreshToken | modules/auth/utils/token.util.js | jsonwebtoken | userId (string, req, JWT_REFRESH_SECRET, JWT_REFRESH_EXPIRES_IN env), email (string, req), tokenVersion (number, opt), sessionId (string, opt), role (string, opt) | Return: JWT refresh token string | ACTIVE | Same fields as access token but with type:'refresh' and longer expiry. |
| setAuthCookies | modules/auth/utils/cookie.util.js | crypto | res (object, req, COOKIE_DOMAIN, NODE_ENV env), accessToken (string, req), refreshToken (string, req) | Side-effect: sets access_token, refresh_token, csrf_token cookies | ACTIVE | access_token is NOT httpOnly (for SSE auth). refresh_token is httpOnly. Cookie domain: .weddingwise.gr in prod, localhost if COOKIE_DOMAIN=localhost. |
| registerValidator | modules/auth/validators/auth.validator.js | express-validator | — | Return: validator chains for first_name, last_name, email (normalizeEmail), password, password_confirmation, wedding_date (opt, ISO8601, not past), locale (opt, en\|el) | ACTIVE | — |
| loginValidator | modules/auth/validators/auth.validator.js | express-validator | — | Return: validator chains for email (normalizeEmail), password, remember (opt boolean) | ACTIVE | — |
| refreshValidator | modules/auth/validators/auth.validator.js | express-validator | — | Return: validator chain for refresh_token required string | ACTIVE | — |
| uiConfigValidator | modules/auth/validators/auth.validator.js | express-validator | — | Return: validator chains for nested ui_config: theme (mode, primaryColor hex, fontSize), notifications (email/push/sms/...), language (en\|el), currency (3-letter ISO), timezone (IANA), dashboard (showBudget/showChecklist/showGuestCount booleans) | ACTIVE | — |
| configureGoogleStrategy | modules/auth/passport/google.passport.js | passport-google-oauth20, User, bcrypt | passport (object, req, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_CALLBACK_URL env) | Side-effect: configures Passport GoogleStrategy | ACTIVE | Reactivates soft-deleted accounts on OAuth login. Links google_id to existing accounts. Creates new user if not found. email_verified=true from Google. |
| test routes | modules/auth/routes/test.routes.js | bcrypt, jwt, User, Vendor | req (JWT_SECRET, JWT_REFRESH_SECRET, NODE_ENV, E2E_TEST_ENDPOINTS env) | Side-effect: HTTP response with test auth tokens | ACTIVE | POST /test/auth/login (bypasses decryptPassword), POST /test/auth/login-vendor (auto-creates vendor), POST /test/vendors/create. ONLY mounted if NODE_ENV=test or E2E_TEST_ENDPOINTS=true. |

---

### Backend — Billing Module (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| billingController | modules/billing/controllers/billing.controller.js | Subscription, Transaction, Invoice, StripeService, PayPalService, WebhookService, plans | req (CORS_ORIGIN env), res | Side-effect: HTTP JSON response | ACTIVE | getPlans, getSubscription, subscribe (Stripe checkout), cancelSubscription, getPortalUrl, createStripeIntent, createPayPalOrder, capturePayPalOrder, getTransactions, getInvoices, handleStripeWebhook, handlePayPalWebhook. |
| StripeService | modules/billing/services/stripe.service.js | stripe npm package | user (object, req, STRIPE_SECRET_KEY env), priceId (string, opt), successUrl (string, opt), cancelUrl (string, opt), amount (number, opt), currency (string, opt) | Return: Stripe customer/checkout/portal/subscription objects | ACTIVE | createOrGetCustomer, createCheckoutSession, createPortalSession, cancelSubscription, getSubscription, createPaymentIntent, constructWebhookEvent. Lazy-loaded stripe client. |
| PayPalService | modules/billing/services/paypal.service.js | @paypal/checkout-server-sdk | user (object, req, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE env), plan (object, req), orderId (string, opt), subscriptionId (string, opt), reason (string, opt) | Return: PayPal order/subscription/capture objects | ACTIVE | createOrder (EUR only), captureOrder, createSubscription (order+capture flow), getSubscription, cancelSubscription, verifyWebhookSignature (stub — always returns true). |
| WebhookService | modules/billing/services/webhook.service.js | StripeService, Subscription, Transaction, Invoice, database/connection, plans | payload (string\|object, req, STRIPE_WEBHOOK_SECRET env), signature (string, req) | Return: {received: true} or {received: true, skipped: true} | ACTIVE | handleStripeWebhook (idempotent via webhook_events table), handleSubscriptionUpdate, handleSubscriptionCanceled, handleInvoicePaid, handleInvoicePaymentFailed, handleCheckoutCompleted, mapStripeStatus, getPlanFromPriceId, updateUserSubscription. Plans: pro_monthly, pro_yearly, premium_monthly, premium_yearly. |
| Subscription model | modules/billing/models/subscription.model.js | database/connection, uuid | — | — | ACTIVE | create, findByUserId, findByStripeSubscriptionId, findByStripeCustomerId, update (allowed: stripe_subscription_id, stripe_customer_id, paypal_subscription_id, plan_id, status, billing_cycle, current_period_start, current_period_end, cancel_at_period_end), delete. |
| Transaction model | modules/billing/models/transaction.model.js | database/connection, uuid | — | — | ACTIVE | create, findById, findByExternalTransactionId, findByUserId (with limit/offset), update (status, metadata only). |
| Invoice model | modules/billing/models/invoice.model.js | database/connection, uuid | — | — | ACTIVE | create, findById, findByInvoiceNumber, findByStripeInvoiceId, findByUserId (with limit/offset), update (status, paid_at, invoice_url only), generateInvoiceNumber (INV-YYYY-NNNNN format). |
| billing.routes | modules/billing/routes/billing.routes.js | billingController, auth.middleware, csrf.middleware | — | — | ACTIVE | Public: GET /plans. Protected: GET /subscription, POST /subscribe (CSRF), POST /cancel (CSRF), GET /portal, POST /stripe/create-intent (CSRF), POST /paypal/create-order (CSRF), POST /paypal/capture (CSRF), GET /transactions, GET /invoices. Webhooks (no auth): POST /webhooks/stripe (raw body), POST /webhooks/paypal. |
| subscribeValidator | modules/billing/validators/billing.validator.js | express-validator | — | Return: validator chains for plan_id (pro_monthly\|pro_yearly\|premium_monthly\|premium_yearly), billing_cycle (monthly\|yearly, opt), payment_method (stripe\|paypal, opt) | ACTIVE | — |

---

### Backend — Booking Requests (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| bookingRequestController | modules/bookingRequests/bookingRequest.controller.js | BookingRequest, Vendor, Booking, ChecklistTask, notifications, smsService, emailService, User, vendorProfileRepo | req, res | Side-effect: HTTP JSON response | ACTIVE | create (sends SMS+email to vendor + in-app notification), getByVendor, updateStatus (accept/decline — creates Booking+ChecklistTask on accept, notifies customer), getById, getByCustomer. findVendorByUserId helper with email fallback. |
| BookingRequest model | modules/bookingRequests/bookingRequest.model.js | database/connection, uuid | — | — | ACTIVE | create (expires_at = now+24h), getByVendor (with status filter, limit/offset), getById, updateStatus, checkExpired, expireOldRequests (batch), countByVendor, getByCustomer (joins vendors table). |
| bookingRequest.routes | modules/bookingRequests/bookingRequest.routes.js | bookingRequestController, auth.middleware | — | — | ACTIVE | All routes protected by authenticate. GET /vendor, GET /customer, GET /:id, PATCH /:id/status. |

---

### Backend — Budget Module (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| expenseController | modules/budget/controllers/expense.controller.js | Expense, sanitize.util | req, res | Side-effect: HTTP JSON response | ACTIVE | getBudget (summary + categories), getExpenses (with category_id, payment_status filters), createExpense (sanitizes text fields), updateExpense, deleteExpense, getCategories, getBenchmarks (hardcoded Greek wedding benchmarks, 8 categories). |
| Expense model | modules/budget/models/expense.model.js | database/connection, uuid | — | — | ACTIVE | create, findById, findByWeddingId (with category_id, payment_status filters), updateById (whitelist: description, amount, date, payment_status, payment_type, notes, receipt_url, vendor_name, category_name), deleteById, getBudgetSummary (total_spent, by_category, recent 5), getCategories, getBenchmarks (hardcoded Greek averages). |
| expense.routes | modules/budget/routes/expense.routes.js | expenseController, auth.middleware, verifyWedding.middleware, csrf.middleware | — | — | ACTIVE | All routes require authenticate + verifyWeddingOwnership. GET /, /categories, /benchmarks, /expenses (list). POST/PUT/DELETE /expenses require CSRF. |

---

### Backend — Checklist Module (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| taskController | modules/checklist/controllers/task.controller.js | Task | req, res | Side-effect: HTTP JSON response | ACTIVE | getTasks (with category, completed, priority filters), getSummary (total, completed, overdue, percentage), getByCategories, createTask, updateTask, toggleTask (sets completed_at timestamp), deleteTask, generateChecklist (44 default tasks, no due dates). |
| Task model | modules/checklist/models/task.model.js | database/connection, uuid | — | — | ACTIVE | create, findById, findByWeddingId (with category, completed, priority filters, priority-sorted), updateById (sets completed_at/NULL on completed toggle), deleteById, getSummary, getByCategories (12 predefined categories), generateDefault (44 tasks). |
| task.routes | modules/checklist/routes/task.routes.js | taskController, auth.middleware, verifyWedding.middleware, csrf.middleware | — | — | ACTIVE | All routes require authenticate + verifyWeddingOwnership. GET /, /summary, /categories, POST /generate (CSRF). POST/PUT/PATCH/DELETE /tasks require CSRF. |

---

### Backend — Guests Module (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| guestController | modules/guests/controllers/guest.controller.js | Guest, sanitize.util | req, res | Side-effect: HTTP JSON response | ACTIVE | getAll (search, group, rsvp_status, pagination + RSVP summary), getOne, create (first_name optional, last_name required), update, updateRsvp (confirmed\|pending\|declined), delete, getRsvpSummary, bulkImport (max 500, formula injection protection with sanitizeValue, side+rsvp validation). |
| Guest model | modules/guests/models/guest.model.js | database/connection, uuid | — | — | ACTIVE | create, findById, findByName (for duplicate check), findByWeddingId (with search, group_name, rsvp_status, limit/offset), updateById (ALLOWED_UPDATE_COLUMNS whitelist: first_name, last_name, email, phone, group_name, side, household_id, plus_one, plus_one_name, dietary_restrictions, rsvp_status, table_id, seat_number, notes), deleteById, getRsvpSummary (total/confirmed/pending/declined/not_sent), bulkCreate (duplicate skip + error handling). |
| guest.routes | modules/guests/routes/guest.routes.js | guestController, auth.middleware, verifyWedding.middleware, csrf.middleware | — | — | ACTIVE | All routes require authenticate + verifyWeddingOwnership. GET /, /summary, POST /import (CSRF), GET /:guestId, PATCH /:guestId/rsvp (CSRF), POST/PUT / require CSRF. |

---

### Backend — Seating Module (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| seatingController | modules/seating/controllers/seating.controller.js | Seating, Guest, database/connection | req, res | Side-effect: HTTP JSON response | ACTIVE | getSeatingData (tables + guests + elements), saveSeatingLayout (transaction with REPEATABLE READ, bulkUpsertWithClient + bulkUpdateGuestAssignmentsWithClient + bulkUpsertElementsWithClient), createTable, updateTable, deleteTable (unassigns guests first), assignGuest. |
| Seating model | modules/seating/models/seating.model.js | database/connection, uuid | — | — | ACTIVE | create, findById, findByWeddingId, updateById, deleteById, bulkUpsert (legacy N+1), bulkUpsertWithClient (STRICT mode, requires expectedUpdates Map, UNNEST bulk UPDATE with optimistic locking on save_version BIGINT, throws ConcurrentModificationError), getGuestsWithSeating, assignGuestToTable, bulkUpdateGuestAssignments, bulkUpdateGuestAssignmentsWithClient, findElementsByWeddingId, bulkUpsertElementsWithClient. |
| ConcurrentModificationError | modules/seating/models/seating.model.js | — | conflicts (array, req) | — | ACTIVE | Custom error class for optimistic locking conflicts. |
| ValidationError | modules/seating/models/seating.model.js | — | message (string, req) | — | ACTIVE | Custom error class for validation failures in seating operations. |
| seating.routes | modules/seating/routes/seating.routes.js | seatingController, auth.middleware, verifyWedding.middleware, csrf.middleware | — | — | ACTIVE | All routes require authenticate + verifyWeddingOwnership. GET /, POST /save (CSRF, validates full layout), POST /tables (CSRF), PUT /tables/:tableId (CSRF), DELETE /tables/:tableId (CSRF), PUT /guests/:guestId/assign (CSRF). |

---

### Backend — Messages & Conversations (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| messages/index.js | modules/messages/index.js | (deprecated) | — | — | DEPRECATED | Deprecated wrapper — routes to Conversations module. |
| messageController | modules/messages/controllers/message.controller.js | messages/models/message.model.js | req, res | Side-effect: HTTP JSON response | ACTIVE | sendMessage, getConversation, getInbox, markAsRead, getVendorMessages, sendVendorReply. Note: sendReplyValidator expects customer_id but sendVendorReply uses couple_email — MISMATCH. |
| messages model | modules/messages/models/message.model.js | database/connection | — | — | DEPRECATED | create, getByVendor, getInbox, markAsRead, getVendorMessages. Deprecated — superseded by conversations model. |
| sendMessageValidator | modules/messages/validators/message.validator.js | express-validator | — | Return: validator chains for attachments array, message content | ACTIVE | — |
| conversations/index.js | modules/conversations/index.js | express | — | Side-effect: Express router wrapper | ACTIVE | Router wrapper for conversations module. |
| conversations/routes | modules/conversations/routes/conversation.routes.js | express, conversationController | — | — | ACTIVE | requireVendor middleware applied. |
| conversationController | modules/conversations/controllers/conversation.controller.js | conversation.model | req, res | Side-effect: HTTP JSON response | ACTIVE | isPointerModelEnabled, startConversation, getConversations, getVendorConversations, getConversation, markAsRead, getMessages, sendMessage, deleteConversation, vendorDeleteConversation, getOrCreateForVendor. Heavy debug logging in getMessages. sendMessage has write-time invariant validation. DATA_INTEGRITY_VIOLATION thrown if conversation missing vendor binding. |
| conversationModel | modules/conversations/models/conversation.model.js | database/connection | — | — | ACTIVE | isPointerModelEnabled, createMessageWithFiltering, createWithBookingRequest, incrementLeadIfNew, getLeadStatus, create, getById, getUserConversations, getVendorConversations, updateStatus, findExisting, getByUserAndVendor, softDelete, vendorDelete. Dual pointer/legacy read tracking with cached feature detection. |

---

### Backend — Notifications (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| NOTIFICATION_TYPES | modules/notifications/notification.service.js | — | — | Return: constant array of notification type strings | ACTIVE | new_message, booking_request, booking_confirmed, booking_rejected, booking_accepted, booking_declined, seating_update, budget_alert, checklist_reminder, vendor_reply |
| wrapVersionedPayload | modules/notifications/notification.service.js | — | {title, body, action, entityId} (object, req) | Return: {version:1, data:{title,body,action,entityId?}} | ACTIVE | Validates non-empty strings, throws on invalid. |
| createNotification | modules/notifications/notification.service.js | index.model, EventEmitter | userId, type, channels, title, body, action, entityId + legacy params | Return: {notificationId, deliveries[]}; emits notification.created events | ACTIVE | — |
| emitNotificationCreated | modules/notifications/notification.service.js | EventEmitter | {notificationId, userId, type, channel, deliveryId} | Side-effect: re-emits notification.created on EventEmitter | ACTIVE | — |
| getNotificationEventBus | modules/notifications/notification.service.js | EventEmitter | — | Return: EventEmitter singleton | ACTIVE | For other modules to subscribe to notification events. |
| notificationService (legacy) | modules/notifications/index.model.js | — | — | — | DEPRECATED | Legacy flat schema — superseded by new notifications + notification_deliveries schema. |
| getNotificationsByUser (legacy) | modules/notifications/index.model.js | database/connection | — | Return: notifications with LEFT JOIN conversations/vendors | DEPRECATED | Left-joined with conversations/vendors. |
| getUnreadCount (legacy) | modules/notifications/index.model.js | database/connection | — | Return: unread count using is_read=FALSE OR is_read IS NULL | DEPRECATED | Dual schema support. |
| markAsRead (legacy) | modules/notifications/index.model.js | database/connection | notificationId, userId | Return: boolean | DEPRECATED | Tries new schema first, falls back to legacy. |
| markAllAsRead (legacy) | modules/notifications/index.model.js | database/connection | userId | Side-effect: updates notifications | DEPRECATED | Legacy fallback. |
| createNotificationWithDeliveries | modules/notifications/index.model.js | database/connection | — | Return: {notification, deliveries[]} | ACTIVE | NEW schema — atomic transaction creates notification + delivery rows. |
| claimPendingDeliveries | modules/notifications/index.model.js | database/connection | channel, limit | Return: claimed rows | ACTIVE | Atomic UPDATE WHERE status='pending' AND claimed_at IS NULL — prevents duplicate claiming. |
| releaseStaleClaims | modules/notifications/index.model.js | database/connection | channel, staleMinutes=5 | Side-effect: releases old claims | ACTIVE | — |
| markDeliveryAsSent | modules/notifications/index.model.js | database/connection | deliveryId | Side-effect: sets status='sent', clears claimed_at | ACTIVE | — |
| markDeliveryAsFailed | modules/notifications/index.model.js | database/connection | deliveryId, errorMessage | Side-effect: sets status='failed', error message, clears claimed_at | ACTIVE | — |
| upsertDevice | modules/notifications/index.model.js | database/connection | {userId, platform, pushToken, sessionId} | Side-effect: ON CONFLICT (push_token) updates is_active/last_seen_at | ACTIVE | — |
| getDevicesByUserId | modules/notifications/index.model.js | database/connection | userId | Return: active devices (is_active=true) | ACTIVE | — |
| revokeDevicesBySession | modules/notifications/index.model.js | database/connection | sessionId | Return: count of revoked devices | ACTIVE | Logout invalidation. |
| notificationController | modules/notifications/controllers/notification.controller.js | index.model | req, res | Side-effect: HTTP JSON response | ACTIVE | getNotifications, getUnreadCount, markAsRead, markAllAsRead, deleteNotification. isPointerModelEnabled caches in module var — checks if conversation_reads table exists. |
| device.service | modules/notifications/device.service.js | index.model | — | — | ACTIVE | validatePlatform, registerDevice (validates userId/platform/pushToken non-empty), unregisterDevice, getActiveDevices. VALID_PLATFORMS = ['android','ios','web']. |
| push.service | modules/notifications/push.service.js | firebase-admin | — | — | ACTIVE | isFCMConfigured (checks FIREBASE_SERVICE_ACCOUNT_PATH + FIREBASE_PROJECT_ID), initializeFirebase (safe multiple calls, does NOT throw), sendToDevice (iOS returns permanent failure, handles NotRegistered), sendToUser (filters android/web only), sendBatch (chunks 20 devices per FCM limit), handleTokenInvalidation. iOS push NOT implemented — returns permanent failure. |
| sse.service | modules/notifications/sse.service.js | EventEmitter | — | — | ⚠️ CLUSTER_INCOMPATIBLE | connections Map (in-memory — incompatible with Node cluster mode), addConnection (sends immediate unread count on connect), removeConnection, sendToUser (SSE format), emitAuthError, sendUnreadCountToUser, pollAndEmit, startDispatcher (polls every 1000ms default), stopDispatcher, sendHeartbeatToAll (30s heartbeat), emitUnreadCount. **WARNING: module-level Map + EventEmitter incompatible with ENABLE_CLUSTER=true** |
| delivery.worker | modules/notifications/delivery.worker.js | index.model, push.service, EventEmitter | — | — | ACTIVE | processPushDelivery (validates payload, sends FCM, marks sent/failed, emits EventEmitter — safe when pushService null), processPendingDeliveries, startWorker (interval 5000ms), stopWorker. Workers auto-start at module load time. |
| notification.routes | modules/notifications/routes/notification.routes.js | notificationController | — | — | ACTIVE | GET /stream (inline JWT — enables auth_error SSE vs HTTP 401), OPTIONS /stream (CORS preflight handled by backend), POST /devices/register, POST /devices/unregister, GET /push/status, GET / (authenticated), GET /unread-count, PUT /read-all, PUT /:id/read, DELETE /:id. Module init starts SSE dispatcher (1000ms) and delivery worker (5000ms) at parse time. |

---

### Backend — Vendors (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| vendorSearchController | modules/vendors/controllers/vendorSearch.controller.js | vendorSearchService | req, res | Side-effect: HTTP JSON response | ACTIVE | Vendors search with in-memory category cache. |
| vendorProfileController | modules/vendors/controllers/vendorProfile.controller.js | vendorProfileService, vendorProfileRepo | req, res | Side-effect: HTTP JSON response | ACTIVE | Largest controller — handles registration with password decryption/hashing, XSS sanitization, transactions. |
| vendorLeadController | modules/vendors/controllers/vendorLead.controller.js | vendorLeadService | req, res | Side-effect: HTTP JSON response | ACTIVE | — |
| vendorAvailabilityController | modules/vendors/controllers/vendorAvailability.controller.js | vendorAvailabilityService, vendorAvailabilityRepo | req, res | Side-effect: HTTP JSON response | ACTIVE | — |
| vendorSavedController | modules/vendors/controllers/vendorSaved.controller.js | vendorSavedService | req, res | Side-effect: HTTP JSON response | ACTIVE | — |
| vendorReviewController | modules/vendors/controllers/vendorReview.controller.js | vendorReviewService | req, res | Side-effect: HTTP JSON response | ACTIVE | — |
| vendorAnalyticsController | modules/vendors/controllers/vendorAnalytics.controller.js | vendorAnalyticsService | req, res | Side-effect: HTTP JSON response | ACTIVE | — |
| vendorSearchService | modules/vendors/services/vendorSearch.service.js | vendorSearchRepo | — | Return: search results with in-memory category cache | ACTIVE | In-memory category cache. |
| vendorProfileService | modules/vendors/services/vendorProfile.service.js | vendorProfileRepo, User, decryption | — | Side-effect: vendor registration with password decryption/hashing, XSS sanitization | ACTIVE | Largest service — handles password decryption for migrated vendors, XSS sanitization, transactions. |
| vendorLeadService | modules/vendors/services/vendorLead.service.js | vendorLeadRepo | — | Side-effect: lead management | ACTIVE | — |
| vendorAvailabilityService | modules/vendors/services/vendorAvailability.service.js | vendorAvailabilityRepo | — | Return: availability data | ACTIVE | ⚠️ Potential SQL injection in unblockDates — constructs SQL string directly from dates array. |
| vendorSavedService | modules/vendors/services/vendorSaved.service.js | vendorSavedRepo | — | Return: saved vendors list | ACTIVE | — |
| vendorReviewService | modules/vendors/services/vendorReview.service.js | vendorReviewRepo | — | Return: reviews | ACTIVE | — |
| vendorAnalyticsService | modules/vendors/services/vendorAnalytics.service.js | vendorAnalyticsRepo | — | Return: analytics data | ACTIVE | — |
| vendorProfileRepo | modules/vendors/repositories/vendorProfile.repository.js | database/connection | — | — | ACTIVE | ⚠️ Dual-write phase for Migration 0006 — relational vs JSONB columns. pointerModelEnabled() feature detection. |
| vendorSearchRepo | modules/vendors/repositories/vendorSearch.repository.js | database/connection | — | Return: search results | ACTIVE | — |
| vendorLeadRepo | modules/vendors/repositories/vendorLead.repository.js | database/connection | — | Return: leads | ACTIVE | — |
| vendorAvailabilityRepo | modules/vendors/repositories/vendorAvailability.repository.js | database/connection | — | Return: availability | ACTIVE | ⚠️ unblockDates constructs SQL string directly from dates array — potential SQL injection. |
| vendorSavedRepo | modules/vendors/repositories/vendorSaved.repository.js | database/connection | — | Return: saved vendors | ACTIVE | — |
| vendorReviewRepo | modules/vendors/repositories/vendorReview.repository.js | database/connection | — | Return: reviews | ACTIVE | — |
| vendorAnalyticsRepo | modules/vendors/repositories/vendorAnalytics.repository.js | database/connection | — | Return: analytics | ACTIVE | — |
| vendorReportRepo | modules/vendors/repositories/vendorReport.repository.js | database/connection | — | Return: reports | ACTIVE | — |
| vendor model | modules/vendors/models/vendor.model.js | database/connection | — | — | ACTIVE | — |
| vendor.routes | modules/vendors/routes/vendor.routes.js | vendor controllers, auth.middleware | — | — | ACTIVE | All vendor routes. |
| vendor validators (10) | modules/vendors/validators/vendor.validator.js | express-validator | — | Return: validator chains | ACTIVE | ⚠️ vendorContactValidator exported but NOT mounted in any route. |
| vendor contracts (7) | modules/vendors/contracts/*.contract.js | — | — | — | ACTIVE | Pure documentation schemas — no runtime effect. |

---

### Backend — Weddings & Website (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| weddingIdValidator | modules/weddings/validators/wedding.validator.js | express-validator | id (param, string, req) | Return: validator chain for UUID format | ACTIVE | — |
| createWeddingValidator | modules/weddings/validators/wedding.validator.js | express-validator | body (object, req) | Return: validator chains for name (req), date (req, ISO8601), partner_name, partner_email, timezone, locale (en\|el), currency (3 chars), budget_total (float min:0), venue, planning_style | ACTIVE | — |
| updateWeddingValidator | modules/weddings/validators/wedding.validator.js | express-validator | body (object, req) | Return: validator chains — extends createWeddingValidator + status field | ACTIVE | — |
| validate (wedding routes) | modules/weddings/routes/wedding.routes.js | express-validator | validations (array, req) | Side-effect: returns 422 with errors or calls next() | ACTIVE | Wrapper middleware — runs all validations in parallel. |
| weddingController | modules/weddings/controllers/wedding.controller.js | wedding.model, jsonb-version | req, res | Side-effect: HTTP JSON response | ACTIVE | getAll (maps output with unwrapVersioned), getActive (404 with NO_ACTIVE_WEDDING code), getOne (IDOR check — 403 on mismatch), create, update (wrapVersioned for website_data), delete (IDOR check), setActive (no IDOR — model does ownership check), getStats (overview + days_until_wedding, weeks_until_wedding, budget_remaining, budget_percentage_used, checklist percentage). |
| Wedding model | modules/weddings/models/wedding.model.js | database/connection, uuid | — | — | ACTIVE | create (generates slug from name+date), getActiveWedding (via users JOIN, not direct), setActiveWedding (transaction verifies ownership + updates users.active_wedding_id + users.wedding_id), findById, findByUserId, findBySlug, updateById (dynamic SET, skips undefined, updates updated_at), deleteById (reassigns user's active_wedding_id first), reactivateWedding (for account recovery, no transaction), getWithStats (3 separate DB queries for guests/budget/checklist). |
| website.routes | modules/website/routes/website.routes.js | express | — | — | ACTIVE | deepMergeWebsiteData (recursive merge, skips null/undefined), generateSlug (first-last-YYYY-MM-DD). |
| websiteDataValidator | modules/website/validators/website.validator.js | express-validator | body.website_data (object, opt) | Return: validator chains for brideName, groomName, ceremonyTime HH:MM, receptionTime HH:MM, venue{name,address,mapUrl with Google Maps + maps.app.goo.gl pattern}, church{name,address,mapUrl}, registry{name,links[]}, ourStory, heroImage, couplePhoto1, couplePhoto2, showSeatingChart, seatingChartUrl. Rejects javascript: scheme. | ACTIVE | — |
| websiteDataInvariantValidator | modules/website/validators/website.validator.js | express-validator | body.website_data (object, opt) | Return: invariant — showSeatingChart=true requires seatingChartUrl | ACTIVE | — |
| websiteTemplateValidator | modules/website/validators/website.validator.js | express-validator | body.website_template (string, opt) | Return: validator restricting to classic\|modern\|beach\|rustic | ACTIVE | — |

---

### Backend — Scheduling (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| schedulingController | modules/scheduling/controllers/scheduling.controller.js | venue.model, resource.model, booking.model, availability.model, vendor.model | req, res | Side-effect: HTTP JSON response | ACTIVE | createVenue (vendor auth required), getVenues (no auth — public vendor browsing), getVenueById (no auth), updateVenue (ownership check), deleteVenue (ownership check), createResource, getResources (no auth), getResourceById (no auth), updateResource (⚠️ no ownership check — potential auth issue), deleteResource (⚠️ no ownership check), createBooking (checks conflict, defaults status='pending'), getBookings (⚠️ no auth — any authenticated user can query all bookings), getBookingById (⚠️ no auth, no ownership), updateBooking (⚠️ no ownership check), updateBookingStatus (no ownership check), deleteBooking (no ownership), setAvailability (replaces all existing — not transactional), getAvailability (no auth), checkAvailability (⚠️ available=true if bookings.length===0 — incomplete logic, doesn't check actual time overlap with availability windows). |
| venue model | modules/scheduling/models/venue.model.js | database/connection, uuid | data (object, req) | Return: created venue row | ACTIVE | create (vendor_id, name required; images as JSON.stringify), findById, findByVendorId, findAll (dynamic WHERE, city ILIKE partial match), updateById (COALESCE for partial updates), deleteById. |
| resource model | modules/scheduling/models/resource.model.js | database/connection, uuid | data (object, req) | Return: created resource row | ACTIVE | create (vendor_id, venue_id, name, resource_type, capacity, is_active), findById, findByVendorId (LEFT JOIN venues), findByVenueId, findAll (dynamic WHERE, LEFT JOIN venues), updateById (COALESCE), deleteById, createDefaultForVendor (auto-creates by category mapping). |
| booking model | modules/scheduling/models/booking.model.js | database/connection, uuid | data (object, req) | Return: created booking row with joins | ACTIVE | create (resource_id, vendor_id, wedding_id, customer fields, guest_count, datetimes, status default 'pending'), findById (LEFT JOIN resources+vendors), findByResourceId, findByVendorId (OR condition: r.vendor_id OR b.vendor_id), findByWeddingId, findAll (dynamic WHERE with LIMIT), updateById (COALESCE — cannot update status via this method), updateStatus (direct UPDATE), deleteById, checkConflict (checks overlaps excluding cancelled bookings). |
| availability model | modules/scheduling/models/availability.model.js | database/connection, uuid | data (object, req) | Return: created availability row | ACTIVE | create (resource_id, day_of_week, start_time, end_time, is_available default true), findById, findByResourceId, findByDayOfWeek (WHERE is_available=true), findAll, setBulkAvailability (⚠️ DELETE existing + loop insert — NOT a transaction; partial failure leaves inconsistent state), updateById (COALESCE), deleteById, deleteByResourceId, isTimeSlotAvailable (converts date to day-of-week, checks start>=avail.start AND end<=avail.end). |
| booking routes | modules/scheduling/routes/scheduling.routes.js | schedulingController, auth.middleware | — | — | ACTIVE | All scheduling routes require authenticate. |
| createBookingValidator | modules/scheduling/validators/booking.validator.js | express-validator | body (object, req) | Return: validator chains for resource_id (req, UUID), wedding_id (opt, UUID), vendor_id (opt, UUID), customer_name, customer_email, event_description, guest_count (min:1), start_datetime (ISO8601, req), end_datetime (ISO8601, req), status (pending/confirmed/cancelled/completed), notes, metadata | ACTIVE | Note: param named bookingId in validator but routes use :id — potential mismatch. |
| updateBookingValidator | modules/scheduling/validators/booking.validator.js | express-validator | body (object, req) | Return: validator chains for bookingId param + optional body fields | ACTIVE | — |
| bookingMetadataValidator | modules/scheduling/validators/booking.validator.js | express-validator | body.metadata (object, opt) | Return: validator for {version:1, data:{eventType, guestExpectations, specialRequests, depositAmount, depositPaid, paymentNotes}} | ACTIVE | Stored as {version:1, data:{...}} wrapper. version must be 1. |

---

### Backend — Contact (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| sendContactEmail | modules/contact/controllers/contact.controller.js | email.service, escapeHtml | req.body: {name, email, subject, message} (all req) | Side-effect: sends HTML email to admin + confirmation to user; returns 200 or 400/500 | ACTIVE | Public endpoint. Validates required fields + email regex. Reads CONTACT_EMAIL env. escapeHtml() for all user input in HTML. Confirmation email failure caught/logged but doesn't fail request. |
| escapeHtml (contact) | modules/contact/controllers/contact.controller.js | — | str (any, req) | Return: HTML-escaped string; null/undefined → '' | ACTIVE | ⚠️ Duplicates escapeHtml in email.service.js — consider consolidating. |
| contact.routes | modules/contact/routes/contact.routes.js | express, contactController | — | Side-effect: POST / mapped to sendContactEmail | ACTIVE | Single public route — no authentication required. |

---

### Backend — Shared Infrastructure (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| redis client | shared/cache/redis.client.js | ioredis | host (REDIS_HOST env), port (REDIS_PORT env), password (REDIS_PASSWORD env), maxRetriesPerRequest, commandTimeout | Side-effect: ioredis client instance; emits 'error'/'connect' events | ACTIVE | Graceful degradation: retries 3x then stops, auth falls back to DB. Command timeout 100ms fails fast. |
| connect (redis) | shared/cache/redis.client.js | redis | — | Return: Promise — resolves on connect, logs warning on failure (doesn't throw) | ACTIVE | — |
| initDatabase | shared/database/connection.js | pg.Pool | retries (num, opt), delayMs (num, opt) | Return: boolean true on success; throws after retries exhausted | ACTIVE | Exponential backoff. Reads DATABASE_URL, SSL_ENABLED, DB_POOL_MIN, DB_POOL_MAX from env. |
| query | shared/database/connection.js | pool | text (string, req), params (array, opt) | Return: pool.query result object | ACTIVE | Throws 'Database not initialized' if pool is null. |
| getClient | shared/database/connection.js | pool | — | Return: Pool client from pool.connect() | ACTIVE | Throws if pool is null. |
| close (db) | shared/database/connection.js | pool | — | Side-effect: pool.end() + console.log | ACTIVE | Safe to call even if pool is already null. |
| usePostgres | shared/database/connection.js | — | — | Return: boolean true — flag indicating PostgreSQL is active | ACTIVE | Used to check which DB driver is active. |
| createTables | shared/database/init.js | node-pg-migrate, pg.Pool | — | Side-effect: runs all pending node-pg-migrate migrations | ACTIVE | Reads DATABASE_URL from env. |
| runMigrations | shared/database/init.js | createTables | — | Side-effect: calls createTables() | ACTIVE | CLI entrypoint wrapper. |
| initDatabase (init.js) | shared/database/init.js | — | — | No-op stub | DEPRECATED | Do not use. Connection pool is in connection.js. |
| csrfProtection | shared/middleware/csrf.middleware.js | — | req, res, next | Side-effect: 403 CSRF_TOKEN_MISSING/INVALID on mismatch; calls next() on success | ACTIVE | Skips GET/HEAD/OPTIONS. Compares X-CSRF-Token header vs csrf_token cookie. |
| errorHandler | shared/middleware/error.middleware.js | — | err, req, res, _next | Side-effect: returns JSON {success:false, error:{code, message}}; stack trace in dev | ACTIVE | Handles ValidationError, JsonWebTokenError, TokenExpiredError, 429 specifically. |
| notFoundHandler | shared/middleware/error.middleware.js | — | req, res | Side-effect: returns 404 JSON with NOT_FOUND code and route path | ACTIVE | Catches all unmatched routes. |
| asyncHandler | shared/middleware/error.middleware.js | — | fn (function, req) | Return: wrapped async function — Promise.resolve(fn(...)).catch(next) | ACTIVE | Used to wrap async route handlers so they don't need try/catch. |
| queryCount | shared/middleware/query-counter.js | — | — | Side-effect: shared object {value:number} — incremented on each DB query | ACTIVE | Module-level singleton shared across all requests. |
| wrapQuery | shared/middleware/query-counter.js | Pool.prototype.query | originalQuery (function, req) | Return: function that increments queryCount.value when active before calling originalQuery | ACTIVE | Patches Pool.prototype.query to add counting layer. |
| activateQueryCounting | shared/middleware/query-counter.js | wrapQuery, Pool.prototype.query | — | Side-effect: patches Pool.prototype.query; idempotent | ACTIVE | Only activates once (isActive flag). |
| deactivateQueryCounting | shared/middleware/query-counter.js | Pool.prototype.query | — | Side-effect: restores original Pool.prototype.query | ACTIVE | Only restores if isActive is true. |
| queryCounterMiddleware | shared/middleware/query-counter.js | — | req, res, next | Side-effect: resets queryCount.value=0; attaches to req object | ACTIVE | Express middleware — resets count at start of each request. |
| attachQueryCounter | shared/middleware/query-counter.js | activateQueryCounting, queryCounterMiddleware | app (object, req) | Side-effect: calls activateQueryCounting() then app.use(queryCounterMiddleware) | ACTIVE | Call once after app=express() and before routes. |
| loginLimiter | shared/middleware/rateLimit.middleware.js | express-rate-limit | — | Side-effect: express-rate-limit — 5 attempts/IP/15min (or 1000 if SKIP_RATE_LIMIT=true) | ACTIVE | skipSuccessfulRequests=true. |
| registerLimiter | shared/middleware/rateLimit.middleware.js | express-rate-limit | — | Side-effect: express-rate-limit — 3 attempts/IP/hour | ACTIVE | skipSuccessfulRequests=true. SKIP_RATE_LIMIT applies. |
| passwordResetLimiter | shared/middleware/rateLimit.middleware.js | express-rate-limit | — | Side-effect: express-rate-limit — 3 attempts/email/hour (keys on lowercased email if provided, else IP) | ACTIVE | skipSuccessfulRequests=true. Does NOT respect SKIP_RATE_LIMIT. |
| refreshLimiter | shared/middleware/rateLimit.middleware.js | express-rate-limit | — | Side-effect: express-rate-limit — 10 attempts/IP/15min | ACTIVE | Prevents refresh token grinding. skipSuccessfulRequests=true. SKIP_RATE_LIMIT applies. |
| generalLimiter | shared/middleware/rateLimit.middleware.js | express-rate-limit | — | Side-effect: express-rate-limit — 100 requests/min/IP | ACTIVE | SKIP_RATE_LIMIT applies. |
| reportLimiter | shared/middleware/rateLimit.middleware.js | express-rate-limit | — | Side-effect: express-rate-limit — 1 report/user/24h (keys by user ID if auth, else IP) | ACTIVE | ⚠️ SKIP_RATE_LIMIT does NOT apply — always active. |
| blockCredentialsInQueryParams | shared/middleware/security.middleware.js | — | req, res, next | Side-effect: 400 if sensitive params in req.query; calls next() if clean | ACTIVE | Blocks: email, password, pwd, secret, token, api_key, apikey, access_token, refresh_token. Case-insensitive. |
| verifyWeddingOwnership | shared/middleware/verifyWedding.middleware.js | Wedding.findById | req, res, next | Side-effect: 404 if wedding not found, 403 if user doesn't own, attaches req.wedding on success | ACTIVE | IDOR protection. Reads userId from req.user.userId (not req.user.id). |
| AppError | shared/utils/AppError.js | — | code (string, req), message (string, req), status (number, opt) | Return: new AppError instance with .code and .status | ACTIVE | Centralized error class — all services throw AppError, never raw Error. |
| VendorErrors | shared/utils/AppError.js | — | — | Return: object with vendor-specific error codes | ACTIVE | VENDOR_NOT_FOUND, INVALID_CATEGORY, INVALID_LOCATION, LEAD_CREATION_FAILED, REVIEW_NOT_FOUND, BLOCKED_DATE_CONFLICT, VENDOR_NOT_AVAILABLE. |
| init (decryption) | shared/utils/decryption.js | — | — | Side-effect: loads ENCRYPTION_PRIVATE_KEY env, handles base64 DER → PEM conversion | ACTIVE | Handles base64-encoded DER (no PEM headers) used when passed via base64 build arg. Logs warning if key not set. |
| decryptPassword | shared/utils/decryption.js | crypto | encryptedPassword (string, req) | Return: decrypted UTF-8 string, null on failure, original if <=50 chars (not encrypted) | ACTIVE | RSA-OAEP with SHA-256. Returns original if length <=50 (not encrypted). |
| isEncryptionEnabled | shared/utils/decryption.js | — | — | Return: boolean — true if privateKey is loaded | ACTIVE | Check before attempting decryption. |
| getClientIp | shared/utils/logger.js | — | req (object, opt) | Return: client IP string — tries x-forwarded-for, x-real-ip, connection.remoteAddress, req.ip | ACTIVE | Returns 'unknown' if req is null/undefined. |
| getUserAgent | shared/utils/logger.js | — | req (object, opt) | Return: user agent string or 'unknown' | ACTIVE | — |
| logSecurityEvent | shared/utils/logger.js | — | level (INFO/WARN/ALERT, req), event (string, req), req (opt), data (opt) | Side-effect: structured JSON log to console with timestamp, level, event, ip, userAgent, method, path, ...data | ACTIVE | ALERT→console.error, WARN→console.warn, INFO→console.log. |
| logFailedLogin | shared/utils/logger.js | logSecurityEvent | req (object, req), email (string, req), reason (string, req) | Side-effect: logs WARN FAILED_LOGIN with partially masked email ($1***$3) | ACTIVE | Email partially masked to avoid PII in logs. |
| logSuccessfulLogin | shared/utils/logger.js | logSecurityEvent | req, userId | Side-effect: logs INFO SUCCESSFUL_LOGIN with userId | ACTIVE | — |
| logAccountLockout | shared/utils/logger.js | logSecurityEvent | req, email, lockoutMinutes | Side-effect: logs ALERT ACCOUNT_LOCKOUT with masked email | ACTIVE | — |
| logSuspiciousPayload | shared/utils/logger.js | logSecurityEvent | req, details | Side-effect: logs ALERT SUSPICIOUS_PAYLOAD with details | ACTIVE | Used for potential injection attempt detection. |
| logTokenRefresh | shared/utils/logger.js | logSecurityEvent | req, userId, success (boolean) | Side-effect: logs INFO TOKEN_REFRESH with userId and success | ACTIVE | — |
| logLogout | shared/utils/logger.js | logSecurityEvent | req, userId | Side-effect: logs INFO LOGOUT with userId | ACTIVE | — |
| logRegistration | shared/utils/logger.js | logSecurityEvent | req, email, userId | Side-effect: logs INFO REGISTRATION with masked email + userId | ACTIVE | — |
| logAccountRecoveryRequest | shared/utils/logger.js | logSecurityEvent | req, email, userExists (boolean) | Side-effect: logs INFO ACCOUNT_RECOVERY_REQUEST with masked email + userExists flag | ACTIVE | — |
| logAccountRecoverySuccess | shared/utils/logger.js | logSecurityEvent | req, userId | Side-effect: logs INFO ACCOUNT_RECOVERY_SUCCESS with userId | ACTIVE | — |
| logAccountRecoveryFailed | shared/utils/logger.js | logSecurityEvent | req, reason, email (opt) | Side-effect: logs WARN ACCOUNT_RECOVERY_FAILED with reason + optionally masked email | ACTIVE | — |
| logTokenReuseAttempt | shared/utils/logger.js | logSecurityEvent | req, email (opt) | Side-effect: logs ALERT TOKEN_REUSE_ATTEMPT with optional masked email | ACTIVE | Detects potential token replay attacks. |
| sanitizeXss | shared/utils/sanitize.util.js | xss library | str (string, req) | Return: sanitized string with dangerous HTML stripped | ACTIVE | whiteList:{}, stripIgnoreTag:true, stripIgnoreTagBody:['script','style']. Returns non-string as-is. |
| sanitizeString | shared/utils/sanitize.util.js | — | value (string, req) | Return: string with control chars (0x00-0x1F, 0x7F) stripped + trimmed; non-string → '' | ACTIVE | Use for: names, emails, phone numbers. |
| sanitizeName | shared/utils/sanitize.util.js | sanitizeString, sanitizeXss | name (string, req) | Return: sanitized name — chains sanitizeString then sanitizeXss | ACTIVE | Use for guest names, owner names. |
| sanitizeText | shared/utils/sanitize.util.js | sanitizeXss | text (string, req) | Return: full XSS sanitization on text; non-string → '' | ACTIVE | Use for descriptions, notes. |
| sanitizeEmail | shared/utils/sanitize.util.js | sanitizeString | email (string, req) | Return: sanitized email (strip control chars, lowercased); non-string → '' | ACTIVE | Basic sanitization only — does not validate format. |

---

### Backend — Services (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| sendNewMessageNotification | services/email.service.js | nodemailer, transporter | to (string, req), vendorName (string, req), userName (string, req), message (string, req), _conversationId (string, opt) | Side-effect: sends HTML email to vendor; logs success/error; graceful — does not throw | ACTIVE | Reads MAILRELAY_HOST/PORT/USER/PASS, FRONTEND_URL env. Truncates message at 150 chars. |
| sendVendorReplyNotification | services/email.service.js | nodemailer, transporter | to (string, req), userName (string, req), vendorName (string, req), message (string, req), _conversationId (string, opt) | Side-effect: sends HTML email reply to user; graceful failure | ACTIVE | Reads FRONTEND_URL env. Truncates message at 150 chars. |
| sendEmail | services/email.service.js | nodemailer, transporter | to (string, req), subject (string, req), html (string, req) | Side-effect: sends general HTML email; throws on failure | ACTIVE | Throws — caller handles. Reads FROM_NAME, FROM_EMAIL env. |
| sendVerificationEmail | services/email.service.js | nodemailer, transporter | to (string, req), firstName (string, req), verificationUrl (string, req) | Side-effect: sends email verification HTML with verify button; throws on failure | ACTIVE | Throws — propagates error so caller knows. Link expires in 24h. |
| sendPasswordResetEmail | services/email.service.js | nodemailer, transporter | to (string, req), firstName (string, opt), resetToken (string, req) | Side-effect: sends password reset HTML with reset button; logs errors but does not throw | ACTIVE | Graceful failure — catches and logs. Reads FRONTEND_URL env. |
| sendAccountRecoveryEmail | services/email.service.js | nodemailer, transporter | to (string, req), recoveryToken (string, req) | Side-effect: sends account recovery email with recovery link; throws if transporter not configured | ACTIVE | Throws 'Email transporter not configured'. Reads FRONTEND_URL env. Link expires in 1h. |
| sendVendorReportEmail | services/email.service.js | nodemailer, transporter | vendorId, vendorName, vendorEmail (opt), reporterId, reporterName, reporterEmail, reason, details (opt) | Side-effect: sends vendor report HTML to admin; logs errors but does not throw | ACTIVE | Graceful failure. All dynamic content escaped via escapeHtml(). Reads ADMIN_EMAILS, FRONTEND_URL env. |
| escapeHtml (email) | services/email.service.js | — | str (string, opt) | Return: HTML-escaped string (&amp; &lt; &gt; &quot; &#39;) | ACTIVE | Prevents XSS in email HTML. Handles null/undefined as empty string. |
| sendBookingRequestNotification | services/email.service.js | nodemailer, transporter | to (string, req), vendorName (string, req), customerName (string, req), eventDate (string, req), message (string, opt), _bookingRequestId (string, opt) | Side-effect: sends booking request HTML to vendor; logs errors but does not throw | ACTIVE | Graceful failure. Reads FRONTEND_URL env. Truncates message at 150 chars. |
| sendSMS | services/sms.service.js | axios, TEXTBEE_API_URL | to (string, req), message (string, req) | Return: response.data on success; undefined if not configured; throws on API error | ACTIVE | TextBee integration — removes + prefix. Reads TEXTBEE_API_KEY, TEXTBEE_DEVICE_ID env. No-op if env vars missing or axios unavailable. |
| sendUrgentNotification | services/sms.service.js | sendSMS | to (string, req), message (string, req) | Return: delegates to sendSMS() | ACTIVE | Alias/wrapper for urgent SMS use cases. |
| r2Client | services/storage.service.js | @aws-sdk/client-s3, @aws-sdk/s3-request-presigner | — | Side-effect: S3Client instance for R2 (Cloudflare) with 'auto' region, v4 signatures | ACTIVE | Reads R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY env. Region 'auto' for Cloudflare R2. |
| hashUserId | services/storage.service.js | crypto | userId (string, req) | Return: SHA-256 truncated to 12 hex chars; 'anonymous' if userId falsy | ACTIVE | Prevents enumeration attacks — one-way, non-reversible. |
| generateObjectKey | services/storage.service.js | uuid, hashUserId, KEY_PREFIXES | userId (string, req), userRole (string, req), type (string, req), fileName (string, req) | Return: object key string: rolePrefix/hashedUser/typePrefix/timestamp-uuid.ext | ACTIVE | rolePrefix: vendors/ for vendor role, users/ otherwise. |
| getPublicUrl | services/storage.service.js | — | key (string, req) | Return: CDN_URL/key URL string | ACTIVE | CDN_URL from R2_CDN_URL env or fallback to cdn.weddingwise.gr. |
| generateSignedUploadUrl | services/storage.service.js | PutObjectCommand, getSignedUrl, r2Client | key (string, req), contentType (string, opt), expiresIn (number, opt) | Return: presigned PUT URL (default 3600s) | ACTIVE | Browser uploads directly to R2. Sets CacheControl public,max-age=2592000. |
| uploadFile | services/storage.service.js | PutObjectCommand, r2Client | fileData (object, req), key (string, req), options (object, opt) | Return: key string on success | ACTIVE | Sends PutObjectCommand to R2. Sets CacheControl public,max-age=2592000,immutable. |
| deleteFile | services/storage.service.js | DeleteObjectCommand, r2Client | key (string, req) | Return: true on success | ACTIVE | Sends DeleteObjectCommand to R2. |
| updateDeletionLog | services/accountDeletion.service.js | query | logId (number, req), status (string, req), metadataDelta (object, opt) | Side-effect: UPDATE deletion_logs — NEVER throws | ACTIVE | Deletion flow must continue even if logging fails. |
| extractKeyFromUrl | services/accountDeletion.service.js | — | url (string, req) | Return: extracted storage key string, or null if skip/empty/unknown format | ACTIVE | Handles: CDN URLs (replaces CDN_URL prefix), legacy OCI URLs (skipped), raw keys, unknown formats. Skips objectstorage/oraclecloud.com URLs. |
| extractStorageKeys | services/accountDeletion.service.js | query, extractKeyFromUrl, deleteFile | userId (string, req) | Return: array of unique non-empty storage key strings | ACTIVE | Scans: users.avatar_url, weddings.website_data (heroImage,gallery,...), expenses.receipt_url, vendors (logo_url,gallery_images), venues.images, messages.attachments, message_attachments.file_url, invoices.invoice_url. Per-table try/catch. Deduplicates via Set. |
| softDeleteUser | services/accountDeletion.service.js | query | userId (string, req) | Side-effect: DELETE refresh_tokens then UPDATE users SET is_deleted=TRUE, deleted_at=NOW(), status='deleted' | ACTIVE | BEGIN/COMMIT/ROLLBACK transaction. Sets is_deleted flag — reversible via recoverUser(). |
| recoverUser | services/accountDeletion.service.js | query | userId (string, req) | Return: updated user row; throws 'User not found or not deleted' | ACTIVE | Resets is_deleted=FALSE, deleted_at=NULL, status='active', updated_at=NOW(). Only works on already-deleted users. |
| hardDeleteUser | services/accountDeletion.service.js | query, extractStorageKeys, deleteFile, updateDeletionLog | userId (string, req) | Side-effect: R2-first deletion (batches of 5), then DB transaction deleting from all tables | ACTIVE | Idempotent (checks existence first). BATCH_SIZE controlled by R2_DELETE_BATCH env (default 5). NoSuchKey/404 treated as success. DB delete only after R2 completes. Uses deletion_logs table to track progress. |
| filterMessage | services/messageFilter.js | — | content (string, req) | Return: {filtered: string, wasFiltered: boolean} — contact info replaced by [blocked] | ACTIVE | Blocks: Greek phone numbers (+30 or 69X), spaced phone obfuscation, domains (.gr/.com/.net/.eu/.org), Google Maps links, Greek keywords (telephone, website, email, viber, whatsapp, telegram, etc.), obfuscation tricks. |
| filterDescription | services/messageFilter.js | filterMessage | description (string, req) | Return: {filtered, wasFiltered} — delegates to filterMessage | ACTIVE | Wrapper for filtering vendor profile descriptions. |

---

### Backend — Utils (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| wrapVersioned | utils/jsonb-version.js | — | data (any, req), version (number, opt, default 1) | Return: {version:number, data:any} version wrapper | ACTIVE | CURRENT_VERSION=1. All JSONB fields must use {version:1, data:{}} pattern. |
| unwrapVersioned | utils/jsonb-version.js | — | versioned (any, req), defaultValue (any, opt) | Return: versioned.data if versioned has .version+.data; otherwise versioned as-is (legacy compat); returns defaultValue if null/undefined | ACTIVE | Handles legacy unversioned data gracefully — returns as-is. |
| isVersioned | utils/jsonb-version.js | — | data (any, req) | Return: boolean — true if data is object with 'version' and 'data' properties | ACTIVE | Returns false for null, non-objects, or objects missing either field. |
| migrateToVersioned | utils/jsonb-version.js | wrapVersioned, isVersioned | data (any, req) | Return: {version:CURRENT_VERSION, data:data.data} if already versioned, or {version:CURRENT_VERSION, data} if legacy | ACTIVE | Idempotent migration — safe to call multiple times. |
| validateVersioned | utils/jsonb-version.js | — | data (any, req) | Return: validated versioned object; throws if null/undefined, not object, missing fields, or version != CURRENT_VERSION | ACTIVE | CURRENT_VERSION=1, throws if version != 1. Used at API boundary. |
| validateWebsiteData | utils/validate-website-data.js | — | data (object, req) | Return: {valid:boolean} if null/undefined; or {valid:true} or {valid:false, errors:[{field,message}]} | ACTIVE | Validates: brideName/groomName <=100 chars, ourStory <=5000 chars, ceremonyTime/receptionTime HH:MM, church/venue/registry objects, mapUrl valid Google Maps (embed or maps.app.goo.gl), no javascript:, registry.links array, showSeatingChart boolean. Unknown fields rejected (strict). |
| validateOrThrow | utils/validate-website-data.js | validateWebsiteData | data (object, req) | Side-effect: throws Error with code='VALIDATION_ERROR' and details array if invalid | ACTIVE | Convenience wrapper for controllers that want to throw. |

---

### Backend — Entry Point (BE)

| Element Name | File Path | Links/Dependencies | Inputs | Outputs | Validity Status | Notes |
|---|---|---|---|---|---|---|
| createApp | index.js | express, helmet, pino-http, express-rate-limit, cookie-parser, crypto, https, fs, path, database/connection, decryption, redis.client, auth/*, shared/middleware/*, modules/* | — (reads process.env: NODE_ENV, PORT, ENABLE_CLUSTER, REDIS_PASSWORD, CORS_ORIGIN, SKIP_RATE_LIMIT, LOG_LEVEL, HTTPS_ENABLED, CERT_PATH, KEY_PATH, E2E_TEST_ENDPOINTS) | Return: {app: Express app, startServer: async function} | ACTIVE | Main app factory. Initializes DB, Redis, decryption, Passport. Sets up helmet (CSP disabled — managed by nginx), rate limiting (100/min general, 10/min auth, 30/min refresh — all skippable via SKIP_RATE_LIMIT), body parsing (1mb limit), logging. HTTPS optional. Runs cleanupExpired, cleanupOldEmailTokens, deleteStaleSessions on startup and every 4h. Health check at /health. All 17 route modules mounted. |
| startServer | index.js (inner function) | database/connection, decryption, redis.client, authTokenRepository | — | Side-effect: server listening on PORT or HTTPS_PORT; connects DB, init decryption, connect Redis (non-blocking); schedules token cleanup every 4h with 5min initial delay | ACTIVE | Falls back to HTTP if HTTPS cert loading fails. Exits process on error. |

---

## Critical Findings Summary

### 🔴 Security Issues

| ID | Element | File | Issue |
|----|---------|------|-------|
| SEC-01 | vendorAvailabilityRepo.unblockDates | modules/vendors/repositories/vendorAvailability.repository.js | **SQL Injection**: Constructs SQL string directly from dates array — unsafe interpolation |
| SEC-02 | vendorContactValidator | modules/vendors/validators/vendor.validator.js | **Exported but never mounted**: validator exists but no route uses it — dead code, potential confusion |
| SEC-03 | getBookings | modules/scheduling/controllers/scheduling.controller.js | **No auth check**: Any authenticated user can query ALL bookings across all vendors/wedding |
| SEC-04 | updateResource / deleteResource | modules/scheduling/controllers/scheduling.controller.js | **No ownership check**: Resource update/delete has no authorization — any authenticated user can modify any resource |
| SEC-05 | checkAvailability | modules/scheduling/controllers/scheduling.controller.js | **Incomplete availability check**: available=true if bookings.length===0 — does NOT check actual time overlap with availability windows |

### 🟡 Cluster Mode Incompatibility

| ID | Element | File | Issue |
|----|---------|------|-------|
| CLU-01 | SSE connections Map | modules/notifications/sse.service.js | **In-memory Map** of userId → Set of SSE connections. With ENABLE_CLUSTER=true, each worker process has its own Map — connections are lost when load balancer routes to different worker |
| CLU-02 | EventEmitter (notification.service.js) | modules/notifications/notification.service.js | Module-level EventEmitter singleton shared across requests — not replicated across cluster workers |
| CLU-03 | SSE dispatcher | modules/notifications/sse.service.js | pollAndEmit dispatcher uses setInterval on a single process — with cluster, multiple processes may run duplicate dispatchers |

### 🟠 Data Consistency Issues

| ID | Element | File | Issue |
|----|---------|------|-------|
| DAT-01 | setBulkAvailability | modules/scheduling/models/availability.model.js | DELETE + loop INSERT is **not transactional** — if insert fails partway, partial state results with no rollback |
| DAT-02 | sendReplyValidator / sendVendorReply | modules/messages/controllers/message.controller.js | **Parameter mismatch**: validator expects customer_id but controller uses couple_email |
| DAT-03 | Dual schema (notifications) | modules/notifications/*.js | **Legacy + new schema dual code paths** throughout — legacy schema is DEPRECATED but still active; getUnreadCount uses different NULL-handling logic than markAsReadNew |
| DAT-04 | Dual write phase (vendors) | modules/vendors/repositories/vendorProfile.repository.js | Migration 0006 dual-write: pointerModelEnabled() feature detection switches between relational and JSONB columns — incomplete migration state |
| DAT-05 | Conversation missing vendor binding | modules/conversations/controllers/conversation.controller.js | DATA_INTEGRITY_VIOLATION thrown if conversation missing vendor_id — indicates possibility of orphaned conversations in DB |

### 🟢 Deprecated Elements (pending removal)

| Element | File | Status |
|---------|------|--------|
| messages module (entire) | modules/messages/* | **Deprecated** — routes to conversations module |
| initDatabase (init.js) | shared/database/init.js | **Deprecated stub** — pool management moved to connection.js |
| Notification legacy schema | modules/notifications/index.model.js | **Deprecated** — new schema uses notifications + notification_deliveries tables |

---

## Data Flow Summary

```
Frontend (Browser)
    │
    ├── authAPI → POST /api/v1/auth/register|login|refresh
    ├── weddingsAPI → GET/POST/PUT/DELETE /api/v1/weddings/*
    ├── guestsAPI → GET/POST/PUT/PATCH/DELETE /api/v1/weddings/:id/guests/*
    ├── budgetAPI → GET/POST/PUT/DELETE /api/v1/weddings/:id/budget/*
    ├── checklistAPI → GET/POST/PUT/PATCH/DELETE /api/v1/weddings/:id/checklist/*
    ├── seatingAPI → GET/POST/PUT/DELETE /api/v1/weddings/:id/seating/*
    ├── conversationsAPI → /api/v1/conversations/*
    ├── billingAPI → /api/v1/billing/*
    ├── notificationsStream (SSE) → GET /api/v1/notifications/stream
    │
    ▼
Backend (Express)
    │
    ├── authenticate middleware (JWT verification + Redis tokenVersion check)
    ├── verifyWeddingOwnership middleware (IDOR check via Wedding.findById)
    ├── csrf middleware (for mutating requests)
    │
    ▼
Database Layer (PostgreSQL)
    ├── Users / Weddings / Guests / Expenses / Tasks / Vendors / Bookings
    ├── Notifications (new schema) + NotificationDeliveries
    ├── Conversations + Messages (legacy messages deprecated → conversations)
    │
    ▼
Cache Layer (Redis)
    ├── Role cache (2min TTL + jitter)
    ├── Token version cache (1min TTL)
    ├── Rate limiting counters
    │
    ▼
External Services
    ├── Email (nodemailer → MailRelay)
    ├── SMS (TextBee)
    ├── Push (Firebase FCM) — iOS NOT implemented
    ├── Storage (Cloudflare R2 via AWS SDK)
    ├── Payments (Stripe + PayPal)
    └── OAuth (Google via Passport)
```

---

*Report generated by WeddingWise.gr Code Audit Team (2026-04-24)*
