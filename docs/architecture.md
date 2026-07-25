# FastAPI Auth – Architecture & Implementation Guide

## Purpose

This document describes the intended responsibilities of each module in the project. It serves as the implementation blueprint before functionality is added.

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
├── models/
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

* Database configuration
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

The `core` package contains reusable application utilities that are independent of FastAPI.

---

## `core/hashing.py`

Responsible for password hashing.

Should expose functions like:

* hash_password()
* verify_password()

Uses `pwdlib` with Argon2.

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
* Manage email templates
* Provide email sender abstraction

Should not depend on any specific email provider.

---

# Database

Contains database infrastructure and persistence-related components only.

---

## `database/session.py`

Responsible for SQLAlchemy database connectivity.

Responsibilities:

* Create async database engine
* Configure async session factory
* Provide database session infrastructure

Should not contain business logic.

---

## `database/base.py`

Defines the SQLAlchemy declarative base.

Responsibilities:

* Provide the Base class for all ORM models
* Expose SQLAlchemy metadata for migrations

No database queries.

---

## `database/repository.py`

Provides database operations for ORM models.

Examples:

* create_user()
* get_user_by_email()
* update_password()
* mark_email_verified()
* save_refresh_token()
* revoke_refresh_token()

Repositories may depend on:

* database sessions
* SQLAlchemy models

Repositories should contain database queries only.

Repositories should not contain:

* authentication logic
* HTTP concerns
* business workflows

---

## Database Sessions

Database sessions are managed through SQLAlchemy's async session factory.

Responsibilities:

* Manage database transactions
* Provide unit-of-work scope
* Ensure sessions are properly created and closed

Database sessions should be consumed by repositories/services through dependency providers.

Routers should never directly interact with database sessions.

---

# Models

Contains SQLAlchemy ORM models.

Each model has its own module.

Structure:

```
models/
├── __init__.py
├── user.py
├── refresh_token.py
└── verification_token.py
```


Examples:

* User
* RefreshToken
* VerificationToken

Models define:

* database columns
* relationships
* constraints
* indexes

Models should contain no:

* HTTP logic
* authentication workflows
* business rules

---

# Migrations

Database migrations are managed through Alembic.

Responsibilities:

* Track database schema changes
* Generate migrations from SQLAlchemy metadata
* Apply schema changes
* Roll back schema changes

Alembic should depend on database metadata but should not contain application logic.

---

# Schemas

Contains all Pydantic models.

Schemas are responsible for validation and serialization only.

They should not contain:

* database queries
* authentication workflows
* business logic

---

## `schemas/user.py`

User-related schemas.

Examples:

* UserCreate
* UserRead
* UserUpdate

---

## `schemas/auth.py`

Authentication schemas.

Examples:

* LoginRequest
* LoginResponse
* RefreshTokenRequest
* TokenPair

---

## `schemas/password.py`

Password-related schemas.

Examples:

* ForgotPasswordRequest
* ResetPasswordRequest
* ChangePasswordRequest

---

# Services

Business logic lives here.

Services orchestrate repositories and core utilities.

Services should contain:

* workflows
* business rules
* application decisions

Services should not contain:

* HTTP code
* direct database queries

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

* repositories
* hashing
* JWT utilities

---

## `services/password.py`

Password workflows.

Responsibilities:

* Change password
* Forgot password
* Reset password

Coordinates:

* repositories
* hashing
* email utilities
* token utilities

---

## `services/verification.py`

Email verification workflows.

Responsibilities:

* Generate verification email
* Validate verification token
* Mark user as verified

Coordinates:

* repositories
* email utilities
* token utilities

---

# Dependencies

FastAPI dependency providers.

Dependencies connect framework-specific functionality with application components.

---

## `dependencies/current_user.py`

Authentication dependencies.

Examples:

* get_current_user()
* get_current_active_user()
* get_current_verified_user()
* require_admin()

Responsibilities:

* Extract authentication information
* Validate tokens
* Retrieve users through services/repositories

Should not contain business workflows.

---

# Routers

HTTP layer only.

Routers should:

* Validate request bodies
* Call services
* Convert exceptions into HTTP responses
* Return API responses

Routers should never contain:

* SQLAlchemy code
* Password hashing
* JWT creation
* Business rules

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

Main application flow:

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

Shared Utilities:

```
Services
│
├── Hashing
├── JWT
├── Tokens
└── Email
```

Full dependency relationship:

```
Core Utilities
   |
   ▼
Routers ───────► Services ───────► Repositories ───────► Database
```


---

# Design Rules

## Routers

* No SQLAlchemy
* No password hashing
* No JWT creation
* No business rules

Only HTTP handling.

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

## Models

* Define database structure.
* Define relationships and constraints.
* No application workflows.

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
