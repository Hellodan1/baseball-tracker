"""
Async MLB Stats API client using httpx.

Key endpoints used:
  - schedule:       GET /api/v1/schedule?sportId=1&date=YYYY-MM-DD
  - game_boxscore:  GET /api/v1/game/{gamePk}/boxscore
  - person_stats:   GET /api/v1/people/{personId}/stats/game/{gamePk}
  - person:         GET /api/v1/people/{personId}

No authentication required.

Game type filtering: only Regular Season ('R') games are pulled by default.
Add codes to VALID_GAME_TYPES to include postseason, etc.
  R=Regular, S=Spring Training, E=Exhibition, F=Wild Card,
  D=Division Series, L=League Championship, W=World Series, A=All-Star
"""
from __future__ import annotations

import asyncio
from datetime import date, datetime
from typing import Any, Optional

import httpx

BASE_URL = "https://statsapi.mlb.com/api/v1"
VALID_GAME_TYPES = {"R"}


class BaseballClient:
    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "BaseballClient":
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=httpx.Timeout(30.0),
            headers={"Accept": "application/json"},
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_schedule(
        self, game_date: date, sport_id: int = 1
    ) -> dict[str, Any]:
        """Fetch the schedule for a given date."""
        resp = await self._client.get(
            "/schedule",
            params={"sportId": sport_id, "date": game_date.isoformat()},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_game_boxscore(self, game_pk: int) -> dict[str, Any]:
        """Fetch the boxscore for a single game."""
        resp = await self._client.get(f"/game/{game_pk}/boxscore")
        resp.raise_for_status()
        return resp.json()

    async def get_player_game_stats(
        self, person_id: int, game_pk: int
    ) -> dict[str, Any]:
        """Fetch a player's stats for a specific game."""
        resp = await self._client.get(
            f"/people/{person_id}/stats/game/{game_pk}"
        )
        resp.raise_for_status()
        return resp.json()

    async def get_player_info(self, person_id: int) -> dict[str, Any]:
        """Fetch biographical info for a player."""
        resp = await self._client.get(f"/people/{person_id}")
        resp.raise_for_status()
        return resp.json()

    async def get_game_pks(
        self,
        game_date: date,
        game_types: Optional[set[str]] = None,
    ) -> list[int]:
        """Extract gamePks from a day's schedule, filtered by game type.

        Only returns games whose gameType is in the allowed set.
        Defaults to VALID_GAME_TYPES (regular season only).
        """
        allowed = game_types if game_types is not None else VALID_GAME_TYPES
        schedule = await self.get_schedule(game_date)
        games = schedule.get("dates", [{}])[0].get("games", [])
        return [
            game["gamePk"]
            for game in games
            if game.get("gameType") in allowed
        ]

    async def get_boxscores_concurrent(
        self, game_pks: list[int], max_concurrent: int = 5
    ) -> list[dict[str, Any]]:
        """Fetch boxscores for multiple games concurrently using a semaphore."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _fetch(gpk: int) -> dict[str, Any]:
            async with semaphore:
                return await self.get_game_boxscore(gpk)

        return await asyncio.gather(*[_fetch(pk) for pk in game_pks])


# ── Convenience function for a full daily pull ─────────────────────
async def fetch_daily_data(
    game_date: date,
    game_types: Optional[set[str]] = None,
) -> dict[str, Any]:
    """Run a complete one-day pull: schedule -> filtered gamePks -> boxscores.

    returns empty lists if no games match the filter.
    """
    async with BaseballClient() as client:
        game_pks = await client.get_game_pks(game_date, game_types)
        print(f"Found {len(game_pks)} games on {game_date}")

        boxscores = await client.get_boxscores_concurrent(game_pks)
        print(f"Fetched {len(boxscores)} boxscores")

        return {
            "date": game_date.isoformat(),
            "game_pks": game_pks,
            "boxscores": boxscores,
        }
