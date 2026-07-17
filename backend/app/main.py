"""
backend/app/main.py
FastAPI app with DB initialization, scheduler startup, and manual pull endpoint.
"""
import os
from contextlib import asynccontextmanager
from datetime import date, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException

from app.database import init_db
from app.baseball_client import fetch_daily_data
from app.ingest import run_nightly_pull


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    init_db()

    scheduler = BackgroundScheduler(timezone=timezone.utc)
    scheduler.add_job(
        run_nightly_pull,
        trigger=CronTrigger(hour=8, timezone=timezone.utc), #in an ideal world no game will ever run this late but just in case i will put a guardrail in later
        id="nightly_pull",
        replace_existing=True,
        misfire_grace_time=3600
    )
    scheduler.start()
    app.state.scheduler = scheduler

    yield

    scheduler.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "OK"}


@app.post("/pull-now")
def pull_now():
    try:
        run_nightly_pull()
        return {"status": "started_or_completed"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/pull/{game_date}")
async def pull_date(game_date: str):
    data = await fetch_daily_data(date.fromisoformat(game_date))

    top_players = "None"
    top_hits = 0

    for boxscore in data["boxscores"]:
        for side in ["away", "home"]:
            players = boxscore["teams"][side].get("players", {})

            for _, player_data in players.items():
                name = player_data["person"]["fullName"]
                batting = player_data.get("stats", {}).get("batting", {})
                hits = batting.get("hits", 0)

                if hits > top_hits:
                    top_hits = hits
                    top_players = name
                elif hits == top_hits and hits > 0:
                    top_players = f"({top_players}, {name})"

    return {
        "games": len(data["game_pks"]),
        "boxscores_fetched": len(data["boxscores"]),
        "boxscores": data["boxscores"],
        "top-hitter": top_players,
        "top-hitter-hit-count": top_hits,
    }