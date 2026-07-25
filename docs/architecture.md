# FastAPI Auth – Architecture & Implementation Guide

## Purpose

This document describes the intended responsibility of each module in the project. It serves as the implementation blueprint before functionality is added.

The guiding principles are:

* Keep business logic separate from HTTP routing.
* Make the package reusable across FastAPI projects.
* Keep authentication concerns modular.
* Avoid circular dependencies.
* Keep database access isolated from business logic.

---

# Project Structure

```
fastapi_auth/
├── config.py
├── exceptions.py
├── core/
├── database/
├── dependencies/
├── routers/
├── schemas/
└── services/
```

---

# Root Package

## `config.py`

Contains application configuration.

Responsibilities:

* JWT configuration
* Password hashing configuration
* Token expiry settings
* Email verification settings
* Password reset settings
* Environment variable loading
* Pydantic Settings models

Should **not** contain business logic.

---

## `exceptions.py`

Defines package-specific exceptions.

Examples:

* InvalidCredentials
* UserAlreadyExists
* UserNotFound
* EmailNotVerified
* TokenExpired
* InvalidToken
* PasswordResetExpired

Routers should convert these exceptions into HTTP responses.

---

# Core

The `core` package contains reusable infrastructure that is independent of FastAPI.

---

## `core/hashing.py`

Responsible for password hashing.

Should expose functions like:

* hash_password()
* verify_password()

Uses `pwdlib` (Argon2).

No database access.

---

## `core/jwt.py`

Responsible for JWT creation and validation.

Responsibilities:

* create_access_token()
* create_refresh_token()
* decode_token()

Should know nothing about users or databases.

---

## `core/tokens.py`

Handles non-JWT security tokens.

Examples:

* Email verification tokens
* Password reset tokens
* One-time tokens

Should centralise token generation and validation.

---

## `core/email.py`

Provides email-related utilities.

Responsibilities:

* Generate verification links
* Generate password reset links
* Email templates
* Email sender abstraction

Should not depend on any specific email provider.

---

# Database

Contains persistence logic only.

---

## `database/models.py`

Defines SQLAlchemy models.

Examples:

* User
* RefreshToken
* EmailVerification
* PasswordReset

No HTTP logic.

---

## `database/repository.py`

Provides database operations.

Examples:

* create_user()
* get_user_by_email()
* update_password()
* mark_email_verified()
* save_refresh_token()
* revoke_refresh_token()

Should contain all SQLAlchemy queries.

No authentication logic.

---

# Schemas

Contains all Pydantic models.

---

## `schemas/user.py`

User models.

Examples:

* UserCreate
* UserRead
* UserUpdate

---

## `schemas/auth.py`

Authentication models.

Examples:

* LoginRequest
* LoginResponse
* RefreshTokenRequest
* TokenPair

---

## `schemas/password.py`

Password-related models.

Examples:

* ForgotPasswordRequest
* ResetPasswordRequest
* ChangePasswordRequest

Schemas should perform validation only.

No business logic.

---

# Services

Business logic lives here.

Services orchestrate repositories and core utilities.

---

## `services/auth.py`

Authentication workflows.

Responsibilities:

* Register user
* Authenticate user
* Issue tokens
* Refresh tokens
* Logout

Coordinates:

* repository
* hashing
* jwt

Should contain no HTTP code.

---

## `services/password.py`

Password workflows.

Responsibilities:

* Change password
* Forgot password
* Reset password

Coordinates:

* repository
* hashing
* email
* tokens

---

## `services/verification.py`

Email verification workflows.

Responsibilities:

* Generate verification email
* Validate verification token
* Mark user as verified

Coordinates:

* repository
* email
* tokens

---

# Dependencies

FastAPI dependency providers.

---

## `dependencies/current_user.py`

Authentication dependencies.

Examples:

* get_current_user()
* get_current_active_user()
* get_current_verified_user()
* require_admin()

Should decode tokens and retrieve users via services/repositories.

---

# Routers

HTTP layer only.

Routers should:

* validate request bodies
* call services
* convert exceptions into HTTP responses

Routers should never contain business logic.

---

## `routers/auth.py`

Endpoints:

* POST /register
* POST /login
* POST /refresh
* POST /logout

---

## `routers/password.py`

Endpoints:

* POST /forgot-password
* POST /reset-password
* POST /change-password

---

## `routers/verification.py`

Endpoints:

* POST /verify-email
* POST /resend-verification

---

# Dependency Flow

```
Routers
    │
    ▼
Services
    │
    ▼
Repositories
    │
    ▼
Database
```

Shared utilities:

```
Services
    │
    ├── Hashing
    ├── JWT
    ├── Tokens
    └── Email
```

---

# Design Rules

## Routers

* No SQLAlchemy
* No password hashing
* No JWT creation
* No business rules

Only HTTP.

---

## Services

* Business logic only.
* Coordinate repositories and utilities.
* Raise domain exceptions.

---

## Repositories

* Database queries only.
* No authentication logic.
* No HTTP concerns.

---

## Core

* Pure utility modules.
* Reusable.
* Framework-independent.

---

# Future Features

Planned additions include:

* Refresh token rotation
* Email verification
* Password reset
* Remember-me sessions
* Multi-device session management
* OAuth providers
* MFA/TOTP
* Role-based access control (RBAC)
* Permission-based authorisation
* Audit logging
* Token revocation
* Session blacklisting
* Pluggable email backends
* Pluggable storage backends

---

# Goal

The long-term objective is to provide a reusable authentication toolkit that can be installed into any FastAPI project with minimal configuration while keeping routing, business logic, persistence, and infrastructure cleanly separated.
