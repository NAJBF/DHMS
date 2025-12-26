# API Documentation

## Authentication
Base URL: `/aau-dhms-api/auth/`

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| POST | `/login/` | Authenticate user and get JWT tokens. | AllowAny |
| POST | `/logout/` | Logout user and blacklist refresh token. | IsAuthenticated |
| POST | `/register/` | Register a new user account (Student/Staff). | AllowAny |
| POST | `/refresh/` | Refresh access token. | AllowAny |
| GET | `/me/` | Get current authenticated user details. | IsAuthenticated |

## Student Endpoints
Base URL: `/aau-dhms-api/students/`
**Permissions:** Authenticated users with role `student`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Get student dashboard stats (room, penalties, pending requests). |
| GET | `/room/` | Get assigned room details and roommates. |
| GET | `/maintenance/` | List my maintenance requests. |
| POST | `/maintenance/` | Submit a new maintenance request. |
| GET | `/laundry/` | List my laundry forms. |
| POST | `/laundry/` | Create a new laundry form. Returns `qr_link` for public access. |
| GET | `/penalties/` | List my assigned penalties. |

## Proctor Endpoints
Base URL: `/aau-dhms-api/proctors/`
**Permissions:** Authenticated users with role `proctor`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Get proctor dashboard stats for assigned dorm. |
| POST | `/assign-room/` | Assign a room to a student. |
| GET | `/maintenance/pending/` | List maintenance requests pending approval. |
| PUT | `/maintenance/{id}/approve/` | Approve a maintenance request. |
| PUT | `/maintenance/{id}/reject/` | Reject a maintenance request. |
| GET | `/laundry/pending/` | List laundry forms pending approval. |
| PUT | `/laundry/{id}/approve/` | Approve a laundry form. |
| PUT | `/laundry/{id}/reject/` | Reject a laundry form. |
| POST | `/penalties/` | Create a penalty for a student. |
| GET | `/students/` | List all students in the assigned dorm. |

## Staff Endpoints
Base URL: `/aau-dhms-api/staff/`
**Permissions:** Authenticated users with role `staff`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Get staff dashboard stats. |
| GET | `/maintenance/` | List available maintenance jobs (approved by proctor). |
| GET | `/maintenance/my-jobs/` | List jobs assigned to me. |
| PUT | `/maintenance/{id}/accept/` | Accept a maintenance job. |
| PUT | `/maintenance/{id}/start/` | Mark job as in progress. |
| PUT | `/maintenance/{id}/complete/` | Mark job as completed. |

## Security Endpoints
Base URL: `/aau-dhms-api/security/`
**Permissions:** Authenticated users with role `security`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Get security dashboard stats. |
| GET | `/laundry/pending/` | List laundry forms approved by proctor, pending verification. |
| PUT | `/laundry/{id}/verify/` | Verify laundry form items. |
| PUT | `/laundry/{id}/taken-out/` | Mark laundry as taken out. |
| POST | `/laundry/scan/` | Scan QR code to mark laundry taken out. |

## Dorm & Room Endpoints
Base URL: `/aau-dhms-api/`
**Permissions:** IsAuthenticated (Accessible to Students/Staff for browsing).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dorms/` | List all active dorms. |
| GET | `/dorms/{dorm_id}/rooms/` | List all rooms in a specific dorm. |
| GET | `/rooms/available/` | List all available rooms. |

## Public Endpoints (QR Code Workflow)
Base URL: `/aau-dhms-api/public/`
**Permissions:** AllowAny (No authentication required).

**Workflow:**
1. Student creates laundry form -> receives `qr_link`.
2. QR Code encodes this link.
3. Security/Staff scans QR code -> Visits text/link.
4. Link endpoint updates status to `taken_out`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/laundry/{form_code}/status/` | Check status of a laundry form via code. |
| GET | `/laundry/{form_code}/taken/` | **QR Scan Target**: Visits this link to mark laundry as taken out immediately. |
