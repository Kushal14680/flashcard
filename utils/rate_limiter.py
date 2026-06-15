import os
import json
import datetime
from typing import Tuple

USAGE_FILE = "exports/usage_log.json"

def check_and_update_rate_limit() -> Tuple[bool, str]:
    """
    Checks if generation is allowed based on:
    - Max 2 runs per 24 hours
    - Max 120 runs per 365 days
    
    If allowed, records the run and returns (True, "").
    If blocked, returns (False, error_message).
    """
    # Create parent folder if missing
    os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
    
    timestamps = []
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    timestamps = data
        except Exception:
            pass
            
    now = datetime.datetime.now()
    
    # Parse strings to datetime objects
    parsed_times = []
    for t in timestamps:
        try:
            parsed_times.append(datetime.datetime.fromisoformat(t))
        except Exception:
            pass
            
    # Filter out entries older than 365 days to prevent log bloat
    one_year_ago = now - datetime.timedelta(days=365)
    parsed_times = [t for t in parsed_times if t > one_year_ago]
    
    # 1. Check Daily Limit (last 24 hours)
    one_day_ago = now - datetime.timedelta(hours=24)
    daily_runs = [t for t in parsed_times if t > one_day_ago]
    if len(daily_runs) >= 2:
        # Get time when first run exits the 24h window
        next_available = daily_runs[0] + datetime.timedelta(hours=24)
        wait_time = next_available - now
        hours = wait_time.seconds // 3600
        minutes = (wait_time.seconds % 3600) // 60
        return False, (
            f"🚫 **Daily Limit Reached**: You are restricted to generating flashcards **2 times per day**.\n\n"
            f"Please wait **{hours}h {minutes}m** (until **{next_available.strftime('%I:%M %p')}**) to generate again."
        )
        
    # 2. Check Yearly Limit (last 365 days)
    if len(parsed_times) >= 120:
        next_available = parsed_times[0] + datetime.timedelta(days=365)
        return False, (
            f"🚫 **Yearly Limit Reached**: You have reached the yearly cap of **120 generations**.\n\n"
            f"Your next slot becomes available on **{next_available.strftime('%b %d, %Y')}**."
        )
        
    # Limit not exceeded: Log this run and save
    parsed_times.append(now)
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump([t.isoformat() for t in parsed_times], f, indent=2)
        
    return True, ""
