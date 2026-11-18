# Website Uptime Checker API

A simple REST API built with **FastAPI** that checks whether websites are up. Save a list of websites, check them all with one request, and see which ones are up, how fast they respond, and which ones are failing.

Inspired by uptime monitoring services such as UptimeRobot and Pingdom.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.165-009688?logo=fastapi&logoColor=white)

---

## Features

- Check any URL instantly: up/down, HTTP status code and response time
- Save, list, view and delete websites
- Check all saved websites with one request and get an up/down summary
- Clear errors for timeouts and sites that cannot be reached
- Input validation with Pydantic
- Proper HTTP status codes: `201`, `400`, `404`, `409`, `422`
- Interactive API docs at `/docs`

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health of the API and number of saved websites |
| GET | `/check?url=...` | Check any URL once (not saved) |
| POST | `/websites` | Save a website |
| GET | `/websites` | List all saved websites |
| GET | `/websites/{id}` | Get one saved website |
| DELETE | `/websites/{id}` | Delete a saved website |
| GET | `/check-all` | Check every saved website and return a summary |

### Example: `POST /websites`

Request body:
```json
{ "name": "GitHub", "url": "https://github.com" }
```

Response (`201 Created`):
```json
{ "id": 2, "name": "GitHub", "url": "https://github.com" }
```

### Example: `GET /check-all`

```json
{
  "total": 4,
  "up": 2,
  "down": 2,
  "results": [
    { "name": "Google", "url": "https://www.google.com", "is_up": true, "status_code": 200, "response_time_ms": 550, "error": null },
    { "name": "GitHub", "url": "https://github.com", "is_up": true, "status_code": 200, "response_time_ms": 546, "error": null },
    { "name": "Fake", "url": "https://fake-site-xyz-123.com", "is_up": false, "status_code": null, "response_time_ms": null, "error": "Could not connect" },
    { "name": "Missing page", "url": "https://github.com/no-such-page-xyz-123", "is_up": false, "status_code": 404, "response_time_ms": 507, "error": null }
  ]
}
```
*(`checked_at` timestamps omitted for brevity.)*

A website counts as **up** when it answers with a status code below `400`.

### Error responses

| Code | When |
|------|------|
| `400` | URL does not start with `http://` or `https://` |
| `404` | Website id does not exist |
| `409` | Website URL is already saved |
| `422` | Missing or wrongly typed fields in the request |

## Project structure

```
uptime-checker-api/
├── app/
│   ├── __init__.py     # Marks "app" as a Python package
│   └── main.py         # The whole API
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting started

### Prerequisites
- Python 3.10 or newer
- Internet access (to reach the websites being checked)

### Installation

```bash
git clone https://github.com/Ali-glitch2/uptime-checker-api.git
cd uptime-checker-api

python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** to try every endpoint in the browser.

## Usage with curl

```bash
# Check one URL
curl "http://127.0.0.1:8000/check?url=https://github.com"

# Save websites
curl -X POST http://127.0.0.1:8000/websites \
  -H "Content-Type: application/json" \
  -d '{"name": "GitHub", "url": "https://github.com"}'

# List saved websites
curl http://127.0.0.1:8000/websites

# Check all saved websites
curl http://127.0.0.1:8000/check-all

# Delete a website
curl -X DELETE http://127.0.0.1:8000/websites/1
```

**Windows PowerShell:**

```powershell
$body = @{ name = "GitHub"; url = "https://github.com" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/websites -ContentType "application/json" -Body $body
Invoke-RestMethod http://127.0.0.1:8000/check-all
```

## Limitations

- Websites are stored **in memory**, so they are lost when the server restarts.
- Websites are checked **one after another**, so checking many slow sites takes longer.

## Roadmap

- [ ] Store websites in a database
- [ ] Check websites concurrently with async requests
- [ ] Scheduled background checks
- [ ] Alerts when a website goes down
- [ ] Docker image

## Tech stack

- **[FastAPI](https://fastapi.tiangolo.com/)**: web framework
- **[Uvicorn](https://www.uvicorn.org/)**: ASGI server
- **[Requests](https://requests.readthedocs.io/)**: HTTP client used to check websites
- **[Pydantic](https://docs.pydantic.dev/)**: request validation

## What I learned

- Receiving JSON data with **POST** requests and a **Pydantic** model
- Building create / read / delete endpoints for a resource
- Path parameters (`/websites/{id}`) and query parameters (`/check?url=...`)
- Returning the right HTTP status codes and error messages with `HTTPException`
- Calling other websites from Python with `requests` and handling timeouts and connection errors

---

Built as **Day 2** of a 7-day FastAPI & backend challenge.
