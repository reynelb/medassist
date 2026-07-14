# Implementation Documentation

This document maps the technical implementation of MedAssist to the dissertation's Implementation section. It covers all three sprints, architectural decisions, and references to the relevant source files.

---

## Sprint 1 — Project Setup, Authentication & Base Structure

### Goals
- Initialise frontend and backend projects
- Set up database schema and migrations
- Implement JWT authentication (register, login, invite flow)
- Build auth pages (Login, Register, Invite Register)
- Set up routing and role-based access control
- Deploy shared layout with sidebar navigation

### Frontend setup
The frontend was initialised using Vite with the React template:
```bash
npm create vite@latest frontend -- --template react
```
Dependencies added:
- `react-router-dom` — client-side routing
- `axios` — HTTP client
- `zustand` — lightweight state management
- `react-hook-form` — form handling
- `date-fns` — date formatting

### Backend setup
The backend uses FastAPI with async SQLAlchemy for non-blocking database access:
```bash
pip install fastapi uvicorn sqlalchemy[asyncio] alembic asyncpg passlib python-jose
```

### Database migrations
Alembic is configured for async PostgreSQL. To generate and apply migrations:
```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### Authentication architecture

**Registration flow:**
1. Patient submits `POST /api/v1/auth/register`
2. Password hashed with bcrypt via `passlib`
3. `users` row created with `role = patient`
4. Empty `patient_profiles` row created (FK to user)

**Invite flow:**
1. Doctor submits `POST /api/v1/auth/invite` with patient email
2. Backend generates `secrets.token_urlsafe(32)` token
3. Token stored in `invitations` table with 7-day expiry
4. Patient opens `/register/invite/:token`
5. Frontend validates token via `GET /api/v1/auth/invite/validate/:token`
6. On submit: `POST /api/v1/auth/register/invite/:token`
7. Patient profile automatically linked to inviting doctor (`assigned_doctor_id`)

**Login flow:**
1. `POST /api/v1/auth/login` — credentials checked, bcrypt verified
2. Returns `access_token` (60 min) and `refresh_token` (7 days)
3. `role` included in access token payload
4. Frontend stores tokens in `localStorage`
5. Axios interceptor attaches `Authorization: Bearer <token>` to every request
6. On 401, interceptor automatically calls `/auth/refresh` and retries

**Role-based route protection:**
- Frontend: `ProtectedRoute` wrapper checks `isAuthenticated` and `role` in Zustand store
- Backend: FastAPI `Depends(get_current_doctor)` / `Depends(get_current_patient)` on protected routes

### Key files — Sprint 1
| File | Purpose |
|---|---|
| `backend/app/models/__init__.py` | All SQLAlchemy models |
| `backend/app/core/security.py` | bcrypt + JWT creation/decoding |
| `backend/app/api/v1/deps.py` | JWT middleware + role guards |
| `backend/app/api/v1/endpoints/auth.py` | Auth endpoints |
| `backend/alembic/` | Migration scripts |
| `frontend/src/api/client.js` | Axios instance + auto-refresh interceptor |
| `frontend/src/store/authStore.js` | Zustand auth state |
| `frontend/src/pages/auth/LoginPage.jsx` | Login UI |
| `frontend/src/pages/auth/RegisterPage.jsx` | Self-registration UI |
| `frontend/src/pages/auth/InviteRegisterPage.jsx` | Invite-based registration UI |
| `frontend/src/App.jsx` | Router + ProtectedRoute |
| `frontend/src/components/common/Layout.jsx` | Sidebar nav shell |

---

## Sprint 2 — Video Calls, Audio Recording & Transcription

### Goals
- Integrate Daily.co for WebRTC video calls
- Record audio client-side during the call
- Upload audio to backend on call end
- Trigger Whisper transcription as a background task
- Display transcript to doctor

### Video call integration
Daily.co is used as the WebRTC provider. It offers a prebuilt iframe embed and a JavaScript SDK (`@daily-co/daily-js`).

**Doctor call room flow:**
1. Doctor clicks "Start Call" on appointment detail
2. Frontend calls `POST /api/v1/appointments/:id/start`
3. Backend creates a Daily.co room via Daily REST API and returns `room_id`
4. Frontend joins the room using Daily.co SDK
5. `MediaRecorder` captures audio from the call stream
6. On "End Call": `MediaRecorder` stops, audio blob collected
7. Frontend calls `POST /appointments/:id/end` then uploads audio blob to `POST /transcripts/calls/:id/recording`
8. User is redirected to `/doctor/appointments/:id/transcript`

**Patient call room flow:**
1. Patient sees "Join Call" button when appointment status is `in_progress`
2. Frontend calls `GET /api/v1/calls/:id/room` to get a join token
3. Patient joins the same Daily.co room
4. Simple controls only: mute, camera, leave

### Audio recording (client-side)
```javascript
// Capture audio from the call stream
const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
const chunks = []
recorder.ondataavailable = (e) => chunks.push(e.data)
recorder.onstop = () => {
  const blob = new Blob(chunks, { type: 'audio/webm' })
  callsApi.uploadRecording(appointmentId, blob)
}
recorder.start()
```

### Transcription pipeline (backend)
1. `POST /transcripts/calls/:id/recording` receives audio file
2. File saved to `LOCAL_STORAGE_PATH` (or S3 in production)
3. FastAPI `BackgroundTasks` triggers `process_audio()`
4. `process_audio()` calls OpenAI Whisper API:
   ```python
   response = await client.audio.transcriptions.create(
       model="whisper-1",
       file=audio_file,
       response_format="verbose_json"
   )
   ```
5. Raw transcript saved to `transcripts` table with `status = ready`
6. `generate_report_from_transcript()` is called automatically

**Frontend polling:**
```javascript
// Poll every 3 seconds until transcript is ready
transcriptsApi.poll(appointmentId, (transcript) => {
  setTranscript(transcript)
}, 3000)
```

### Key files — Sprint 2
| File | Purpose |
|---|---|
| `backend/app/api/v1/endpoints/transcripts.py` | Audio upload + Whisper background task |
| `backend/app/api/v1/endpoints/appointments.py` | start/end appointment, room creation |
| `frontend/src/pages/doctor/DoctorCallRoom.jsx` | WebRTC + MediaRecorder integration |
| `frontend/src/pages/patient/PatientCallRoom.jsx` | Patient-side call UI |
| `frontend/src/pages/doctor/DoctorTranscript.jsx` | Transcript display + polling |
| `frontend/src/hooks/usePolling.js` | Generic polling hook |
| `frontend/src/api/services.js` | `callsApi.uploadRecording`, `transcriptsApi.poll` |

---

## Sprint 3 — AI Report Generation, Report Editor & Evaluation

### Goals
- Send transcript to GPT-4o and extract structured medical report
- Render auto-filled, editable report form
- Allow doctor to review, edit, and confirm report
- Build patient appointment history view
- Conduct testing and evaluation

### Report generation (LLM)
After transcription completes, `generate_report_from_transcript()` sends the raw text to GPT-4o with a structured prompt:

```python
prompt = f"""
You are a medical assistant. Analyse this doctor-patient consultation transcript
and extract structured information.

Transcript:
{transcript_text}

Return ONLY valid JSON with this structure:
{{
  "chief_complaint": "...",
  "symptoms": ["...", "..."],
  "diagnosis": "...",
  "treatment_plan": "...",
  "medications": [{{"name": "...", "dose": "...", "frequency": "..."}}],
  "follow_up_date": null,
  "summary": "..."
}}
"""
```

The `ai_raw_output` field stores the full LLM response for audit purposes. The structured fields (chief_complaint, symptoms, etc.) are extracted and stored separately in the `reports` table.

**Ethical design decision:** The report is stored with `is_confirmed = False` and `status = draft` until the doctor explicitly reviews and confirms it. The AI never produces a confirmed report autonomously.

### Report editor (frontend)
The `DoctorReport` page polls `GET /reports/:id` until `status = draft`, then renders an editable form:
- Chief complaint — text field
- Symptoms — tag-style multi-input
- Diagnosis — text area
- Treatment plan — text area
- Medications — repeatable rows (name, dose, frequency, duration)
- Follow-up date — date picker
- Doctor notes — free text

Changes are sent via `PATCH /reports/:id` on save. The transcript is shown in a collapsible side panel for reference.

On confirmation, `POST /reports/:id/confirm` sets `is_confirmed = True`, `confirmed_at = now()`, `status = confirmed`.

### Key files — Sprint 3
| File | Purpose |
|---|---|
| `backend/app/api/v1/endpoints/transcripts.py` | `generate_report_from_transcript()` |
| `backend/app/api/v1/endpoints/reports.py` | GET/PATCH/confirm report endpoints |
| `frontend/src/pages/doctor/DoctorReport.jsx` | Editable report form |
| `frontend/src/pages/patient/PatientAppointments.jsx` | Patient appointment history |
| `frontend/src/components/common/StatusBadge.jsx` | Reusable status indicator |

---

## Non-functional implementation notes

### Security
- Passwords stored as bcrypt hashes (cost factor 12)
- JWTs signed with HS256; access tokens expire in 60 minutes
- Refresh tokens stored client-side in `localStorage` (acceptable for demo; production would use httpOnly cookies)
- Role enforcement at both route guard (frontend) and dependency injection (backend) levels
- UUIDs used as primary keys to prevent enumeration attacks
- Patient reports inaccessible to patient role at API level

### Responsiveness
The layout is designed desktop-first with a fixed 220px sidebar. For mobile, the sidebar collapses to a bottom navigation bar (implement via CSS media query on `Layout.jsx`).

### Error handling
- Backend returns RFC-standard error shapes: `{ "detail": "message" }`
- Axios interceptor catches 401s and attempts token refresh before re-throwing
- All pages display inline error states rather than crashing

### Background tasks
Whisper transcription and LLM report generation run as FastAPI `BackgroundTasks`. For a production deployment, migrate these to a Celery queue backed by Redis to handle longer audio files and retry failures.

---

## Adding a new page — checklist

1. Create `src/pages/{role}/PageName.jsx` importing `Layout`
2. Add the route to `src/App.jsx` inside the correct `ProtectedRoute`
3. Add a nav link in `src/components/common/Layout.jsx` if it needs sidebar access
4. Add the corresponding API call to `src/api/services.js`
5. Create the backend endpoint in `backend/app/api/v1/endpoints/`
6. Register it in `backend/app/api/v1/router.py`

---

## Running tests

```bash
# Backend (pytest)
cd backend
pip install pytest pytest-asyncio httpx
pytest

# Frontend (Vitest)
cd frontend
npm run test
```

Test files go in:
- `backend/tests/` — use `httpx.AsyncClient` with FastAPI `app`
- `frontend/src/__tests__/` — use Vitest + React Testing Library
