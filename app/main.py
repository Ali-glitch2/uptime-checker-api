import time
from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Website Uptime Checker")


# The data a user must send when adding a website.
class Website(BaseModel):
    name: str
    url: str


# Our "database": a simple list kept in memory.
# It is emptied every time the server restarts.
websites = []
next_id = 1


def check_website(url):
    """Visit a URL and report if it is up and how fast it answered."""
    start_time = time.time()

    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.Timeout:
        return make_result(url, False, None, None, "Timed out after 5 seconds")
    except requests.exceptions.ConnectionError:
        return make_result(url, False, None, None, "Could not connect")
    except requests.exceptions.RequestException:
        return make_result(url, False, None, None, "Request failed")

    seconds = time.time() - start_time
    milliseconds = round(seconds * 1000)
    is_up = response.status_code < 400
    return make_result(url, is_up, response.status_code, milliseconds, None)


def make_result(url, is_up, status_code, response_time_ms, error):
    """Build one check result as a dictionary."""
    return {
        "url": url,
        "is_up": is_up,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "error": error,
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def find_website(website_id):
    """Find a website by its id, or send back a 404 error."""
    for website in websites:
        if website["id"] == website_id:
            return website
    raise HTTPException(status_code=404, detail="Website not found")


@app.get("/")
def home():
    return {"message": "Website Uptime Checker is running. Open /docs to try it."}


@app.get("/health")
def health():
    return {"status": "ok", "websites_saved": len(websites)}


@app.get("/check")
def check_one_url(url: str):
    """Check any URL once. Example: /check?url=https://google.com"""
    return check_website(url)


@app.post("/websites", status_code=201)
def add_website(website: Website):
    """Save a website so we can check it later."""
    global next_id

    if not (website.url.startswith("http://") or website.url.startswith("https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    for existing in websites:
        if existing["url"] == website.url:
            raise HTTPException(status_code=409, detail="This website is already saved")

    new_website = {"id": next_id, "name": website.name, "url": website.url}
    websites.append(new_website)
    next_id = next_id + 1
    return new_website


@app.get("/websites")
def list_websites():
    """Show every saved website."""
    return websites


@app.get("/websites/{website_id}")
def get_website(website_id: int):
    """Show one saved website."""
    return find_website(website_id)


@app.delete("/websites/{website_id}")
def delete_website(website_id: int):
    """Remove a saved website."""
    website = find_website(website_id)
    websites.remove(website)
    return {"message": f"Deleted {website['name']}"}


@app.get("/check-all")
def check_all_websites():
    """Check every saved website, one after another."""
    results = []
    up_count = 0

    for website in websites:
        result = check_website(website["url"])
        result["name"] = website["name"]
        results.append(result)
        if result["is_up"]:
            up_count = up_count + 1

    return {
        "total": len(results),
        "up": up_count,
        "down": len(results) - up_count,
        "results": results,
    }
