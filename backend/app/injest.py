"""
backend/app/injests.py
Data injest script. Gets each box score, transforms, and then stores it
"""
from baseball_client import fetch_boxscore, get_schedule
from database import engine
from sqlmodel import Session
from datetime import date, timedelta
from models import Player, PlayerGameStats, PlayerBattingStats, PlayerPitchingStats, PlayerFieldingStats, PlayerSeasonBatting, PlayerSeasonPitching, PlayerSeasonFielding

def run_nightly_pull(game_date: date | None = None):
    """
    Pulls game information from provided datetime date. Defaults to pulling yesterday's games if no date is provided.
    """
    if game_date is None:
        game_date = date.today() - timedelta(days=1)

    game_pks = get_schedule(game_date)
    for pk in game_pks:
        raw_boxscores = fetch_boxscore(pk)
        players, game_stats, batting, pitching, fielding = _transform(raw)
        with Session(engine) as session:
            _store(session, players, game_stats, batting, pitching, fielding)
            session.commit()

def _transform(raw_boxscores: dict) -> tuple:
    # Map API dicts to SQLModel objects
    return
    

def _store(session, players, game_stats, batting, pitching, fielding):
    # session.add() in FK order
    return