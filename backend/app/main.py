"""
backend/app/main.py
FastAPI app with DB initialization and a manual data pull endpoint.
"""
import os
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI

from app.database import init_db
from app.baseball_client import fetch_daily_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/pull/{game_date}")
async def pull_date(game_date: str):
    """Manual test: GET /pull/2026-07-09"""
    data = await fetch_daily_data(date.fromisoformat(game_date))

    top_players = "None"
    top_hits = 0



    for boxscore in data["boxscores"]:
        for side in ["away","home"]:
            players = boxscore["teams"][side].get("players",{})

            for player_key, player_data in players.items():
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
