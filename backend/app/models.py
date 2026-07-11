"""
backend/app/models.py

Author: Hellodan

Tables: Player
        PlayerGameStats (shared per-game fields)
        PlayerBattingStats (1:1 with PlayerGameStats)
        PlayerPitchingStats (1:1 with PlayerGameStats)
        PlayerFieldingStats (1:1 with PlayerGameStats)
        PlayerSeasonBatting (cumulative batting per season, new row per player per day)
        PlayerSeasonPitching (cumulative pitching per season, new row per player per day)
        PlayerSeasonFielding (cumulative fielding per season, new row per player per day)
            per player per day rows makes it easier to get stats for specific time periods
"""
from datetime import date, datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


#Player 
class Player(SQLModel, table=True):
    __tablename__ = "player"  #type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    mlb_id: int = Field(unique=True, index=True)
    first_name: str
    last_name: str
    position: Optional[str] = None
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    birth_date: Optional[date] = None
    mlb_debut_date: Optional[date] = None
    height_inches: Optional[int] = None
    weight_lbs: Optional[int] = None
    throws_hand: Optional[str] = None
    bats_hand: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)

    game_stats: list["PlayerGameStats"] = Relationship(back_populates="player")
    season_batting: list["PlayerSeasonBatting"] = Relationship(back_populates="player")
    season_pitching: list["PlayerSeasonPitching"] = Relationship(back_populates="player")
    season_fielding: list["PlayerSeasonFielding"] = Relationship(back_populates="player")


#PlayerGameStats (shared per-game fields) 
class PlayerGameStats(SQLModel, table=True):
    __tablename__ = "player_game_stats"  #type: ignore
    __table_args__ = (
        UniqueConstraint("player_id", "game_pk", name="uq_player_game"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    game_pk: int = Field(index=True)
    game_date: date = Field(index=True)
    season: int = Field(index=True)
    team_id: Optional[int] = None
    opponent_team_id: Optional[int] = None
    home_away: Optional[str] = None
    game_type: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)

    player: Optional[Player] = Relationship(back_populates="game_stats")
    batting: Optional["PlayerBattingStats"] = Relationship(
        back_populates="game_stat", sa_relationship_kwargs={"uselist": False}
    )
    pitching: Optional["PlayerPitchingStats"] = Relationship(
        back_populates="game_stat", sa_relationship_kwargs={"uselist": False}
    )
    fielding: Optional["PlayerFieldingStats"] = Relationship(
        back_populates="game_stat", sa_relationship_kwargs={"uselist": False}
    )


#PlayerBattingStats (1:1 with PlayerGameStats) 
class PlayerBattingStats(SQLModel, table=True):
    __tablename__ = "player_batting_stats"  #type: ignore
    __table_args__ = (
        UniqueConstraint("game_stat_id", name="uq_batting_game_stat"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    game_stat_id: int = Field(foreign_key="player_game_stats.id", unique=True, index=True)

    games_played: Optional[int] = None
    at_bats: Optional[int] = None
    runs: Optional[int] = None
    hits: Optional[int] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    home_runs: Optional[int] = None
    rbi: Optional[int] = None
    walks: Optional[int] = None
    intentional_walks: Optional[int] = None
    strikeouts: Optional[int] = None
    stolen_bases: Optional[int] = None
    caught_stealing: Optional[int] = None
    hit_by_pitch: Optional[int] = None
    grounded_into_double_play: Optional[int] = None
    grounded_into_triple_play: Optional[int] = None
    left_on_base: Optional[int] = None
    total_bases: Optional[int] = None
    sac_bunts: Optional[int] = None
    sac_flies: Optional[int] = None
    catchers_interference: Optional[int] = None
    pickoffs: Optional[int] = None
    air_outs: Optional[int] = None
    fly_outs: Optional[int] = None
    ground_outs: Optional[int] = None
    line_outs: Optional[int] = None
    pop_outs: Optional[int] = None
    plate_appearances: Optional[int] = None
    created_at: datetime = Field(default_factory=utc_now)

    game_stat: Optional[PlayerGameStats] = Relationship(back_populates="batting")


#PlayerPitchingStats (1:1 with PlayerGameStats) 
class PlayerPitchingStats(SQLModel, table=True):
    __tablename__ = "player_pitching_stats"  #type: ignore
    __table_args__ = (
        UniqueConstraint("game_stat_id", name="uq_pitching_game_stat"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    game_stat_id: int = Field(foreign_key="player_game_stats.id", unique=True, index=True)

    games_played: Optional[int] = None
    games_started: Optional[int] = None
    games_pitched: Optional[int] = None
    games_finished: Optional[int] = None
    complete_games: Optional[int] = None
    shutouts: Optional[int] = None
    innings_pitched: Optional[float] = None
    earned_runs: Optional[int] = None
    runs: Optional[int] = None
    hits: Optional[int] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    home_runs: Optional[int] = None
    walks_allowed: Optional[int] = None
    intentional_walks_allowed: Optional[int] = None
    strikeouts_pitching: Optional[int] = None
    hit_batsmen: Optional[int] = None
    hit_by_pitch: Optional[int] = None  #may duplicate hit_batsmen
    stolen_bases_allowed: Optional[int] = None
    caught_stealing: Optional[int] = None
    wild_pitches: Optional[int] = None
    balks: Optional[int] = None
    pickoffs: Optional[int] = None
    passed_balls: Optional[int] = None
    sac_bunts_allowed: Optional[int] = None
    sac_flies_allowed: Optional[int] = None
    catchers_interference: Optional[int] = None
    rbi_allowed: Optional[int] = None
    at_bats_against: Optional[int] = None
    batters_faced: Optional[int] = None
    outs: Optional[int] = None
    pitches_thrown: Optional[int] = None
    number_of_pitches: Optional[int] = None  #may duplicate pitches_thrown
    strikes_thrown: Optional[int] = None
    balls_thrown: Optional[int] = None
    inherited_runners: Optional[int] = None
    inherited_runners_scored: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    saves: Optional[int] = None
    blown_saves: Optional[int] = None
    holds: Optional[int] = None
    save_opportunities: Optional[int] = None
    air_outs: Optional[int] = None
    fly_outs: Optional[int] = None
    ground_outs: Optional[int] = None
    line_outs: Optional[int] = None
    pop_outs: Optional[int] = None
    created_at: datetime = Field(default_factory=utc_now)
    

    game_stat: Optional[PlayerGameStats] = Relationship(back_populates="pitching")


#PlayerFieldingStats (1:1 with PlayerGameStats) 
class PlayerFieldingStats(SQLModel, table=True):
    __tablename__ = "player_fielding_stats"  #type: ignore
    __table_args__ = (
        UniqueConstraint("game_stat_id", name="uq_fielding_game_stat"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    game_stat_id: int = Field(foreign_key="player_game_stats.id", unique=True, index=True)

    games_started: Optional[int] = None
    assists: Optional[int] = None
    put_outs: Optional[int] = None
    errors: Optional[int] = None
    chances: Optional[int] = None
    caught_stealing: Optional[int] = None  #catcher only
    stolen_bases: Optional[int] = None  #catcher only (stolen against)
    passed_balls: Optional[int] = None  #catcher only
    pickoffs: Optional[int] = None
    created_at: datetime = Field(default_factory=utc_now)

    game_stat: Optional[PlayerGameStats] = Relationship(back_populates="fielding")


#PlayerSeasonBatting (cumulative batting per season+date) 
class PlayerSeasonBatting(SQLModel, table=True):
    __tablename__ = "player_season_batting"  #type: ignore
    __table_args__ = (
        UniqueConstraint("player_id", "season", "stat_date", name="uq_player_season_batting_date"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    season: int = Field(index=True)
    stat_date: date = Field(index=True)
    team_id: Optional[int] = None

    games_played: Optional[int] = None
    at_bats: Optional[int] = None
    runs: Optional[int] = None
    hits: Optional[int] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    home_runs: Optional[int] = None
    rbi: Optional[int] = None
    walks: Optional[int] = None
    intentional_walks: Optional[int] = None
    strikeouts: Optional[int] = None
    stolen_bases: Optional[int] = None
    caught_stealing: Optional[int] = None
    hit_by_pitch: Optional[int] = None
    grounded_into_double_play: Optional[int] = None
    grounded_into_triple_play: Optional[int] = None
    left_on_base: Optional[int] = None
    total_bases: Optional[int] = None
    sac_bunts: Optional[int] = None
    sac_flies: Optional[int] = None
    catchers_interference: Optional[int] = None
    pickoffs: Optional[int] = None
    air_outs: Optional[int] = None
    fly_outs: Optional[int] = None
    ground_outs: Optional[int] = None
    line_outs: Optional[int] = None
    pop_outs: Optional[int] = None
    plate_appearances: Optional[int] = None

    #Rate stats
    avg: Optional[float] = None
    obp: Optional[float] = None
    slg: Optional[float] = None
    ops: Optional[float] = None
    created_at: datetime = Field(default_factory=utc_now)

    player: Optional[Player] = Relationship(back_populates="season_batting")


#PlayerSeasonPitching (cumulative pitching per season+date) 
class PlayerSeasonPitching(SQLModel, table=True):
    __tablename__ = "player_season_pitching"  #type: ignore
    __table_args__ = (
        UniqueConstraint("player_id", "season", "stat_date", name="uq_player_season_pitching_date"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    season: int = Field(index=True)
    stat_date: date = Field(index=True)
    team_id: Optional[int] = None

    games_played: Optional[int] = None
    games_started: Optional[int] = None
    games_pitched: Optional[int] = None
    games_finished: Optional[int] = None
    complete_games: Optional[int] = None
    shutouts: Optional[int] = None
    innings_pitched: Optional[float] = None
    earned_runs: Optional[int] = None
    runs: Optional[int] = None
    hits: Optional[int] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    home_runs: Optional[int] = None
    walks_allowed: Optional[int] = None
    intentional_walks_allowed: Optional[int] = None
    strikeouts_pitching: Optional[int] = None
    hit_batsmen: Optional[int] = None
    hit_by_pitch: Optional[int] = None  #may duplicate hit_batsmen
    stolen_bases_allowed: Optional[int] = None
    caught_stealing: Optional[int] = None
    wild_pitches: Optional[int] = None
    balks: Optional[int] = None
    pickoffs: Optional[int] = None
    passed_balls: Optional[int] = None
    sac_bunts_allowed: Optional[int] = None
    sac_flies_allowed: Optional[int] = None
    catchers_interference: Optional[int] = None
    rbi_allowed: Optional[int] = None
    at_bats_against: Optional[int] = None
    batters_faced: Optional[int] = None
    outs: Optional[int] = None
    pitches_thrown: Optional[int] = None
    number_of_pitches: Optional[int] = None  #may duplicate pitches_thrown
    strikes_thrown: Optional[int] = None
    balls_thrown: Optional[int] = None
    inherited_runners: Optional[int] = None
    inherited_runners_scored: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    saves: Optional[int] = None
    blown_saves: Optional[int] = None
    holds: Optional[int] = None
    save_opportunities: Optional[int] = None
    air_outs: Optional[int] = None
    fly_outs: Optional[int] = None
    ground_outs: Optional[int] = None
    line_outs: Optional[int] = None
    pop_outs: Optional[int] = None

    #Rate stats
    era: Optional[float] = None
    whip: Optional[float] = None
    created_at: datetime = Field(default_factory=utc_now)
    home_runs_per_9: Optional[str] = None  #"0.50"
    strike_percentage: Optional[str] = None  #".650"
    stolen_base_percentage: Optional[str] = None  #".---"

    player: Optional[Player] = Relationship(back_populates="season_pitching")


#PlayerSeasonFielding (cumulative fielding per season+date) 
class PlayerSeasonFielding(SQLModel, table=True):
    __tablename__ = "player_season_fielding"  #type: ignore
    __table_args__ = (
        UniqueConstraint("player_id", "season", "stat_date", name="uq_player_season_fielding_date"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    season: int = Field(index=True)
    stat_date: date = Field(index=True)
    team_id: Optional[int] = None

    games_started: Optional[int] = None
    assists: Optional[int] = None
    put_outs: Optional[int] = None
    errors: Optional[int] = None
    chances: Optional[int] = None
    caught_stealing: Optional[int] = None  #catcher only
    stolen_bases: Optional[int] = None  #catcher only (stolen against)
    passed_balls: Optional[int] = None  #catcher only
    pickoffs: Optional[int] = None
    created_at: datetime = Field(default_factory=utc_now)

    #Rate stats
    fielding_percentage: Optional[str] = None  #".987"
    stolen_base_percentage: Optional[str] = None  #".---"
    caught_stealing_percentage: Optional[str] = None  #".---"

    player: Optional[Player] = Relationship(back_populates="season_fielding")
