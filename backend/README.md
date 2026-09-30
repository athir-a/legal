# Verified Legal Research Assistant - Backend

Minimal Django + Django REST Framework backend for the **Verified Legal Research Assistant**.

## Requirements
- Python 3.10+
- Django >= 5.0, < 6.2
- djangorestframework >= 3.15, < 4.0

---

## 1. Setup & Installation

Navigate into the `backend/` directory:

```bash
cd backend
```

*(Optional but recommended)* Create and activate a virtual environment:

```bash
# Windows
py -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 2. Database Migrations

Apply the standard migrations:

```bash
python manage.py migrate
```
*(On Windows without `python` in PATH, use `py manage.py migrate`)*

---

## 3. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```
*(Or `py manage.py runserver`)*

The server will be available at `http://127.0.0.1:8000/`.

---

## 4. Run Tests

To execute the test suite:

```bash
python manage.py test
```
*(Or `py manage.py test`)*

---

## 5. API Specification

### Endpoint: `POST /api/ask/`

Submit a legal question for verified research.

#### Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
  "session_id": "abc123",
  "question": "What does Section 123 of BNS say?"
}
```

- `session_id` *(optional, string)*: Identifier for maintaining session context.
- `question` *(required, string)*: The legal inquiry. Must not be empty or whitespace-only.

#### Valid Response (HTTP 200 OK)
```json
{
  "answer": "This is a temporary mock answer.",
  "supported": true,
  "citations": []
}
```

#### Validation Error Response (HTTP 400 Bad Request)
Returned when `question` is missing, empty, or whitespace-only:
```json
{
  "question": [
    "question field is required."
  ]
}
```

---

## 6. Testing the Endpoint

### Using cURL
```bash
curl -X POST http://127.0.0.1:8000/api/ask/ \
     -H "Content-Type: application/json" \
     -d "{\"session_id\": \"abc123\", \"question\": \"What does Section 123 of BNS say?\"}"
```

### Using PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/ask/" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"session_id": "abc123", "question": "What does Section 123 of BNS say?"}' | ConvertTo-Json
```
