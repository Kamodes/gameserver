import json
from tkinter import INSERT
import uuid
from enum import Enum, IntEnum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import null, text
from sqlalchemy.exc import NoResultFound

from .db import engine


class InvalidToken(Exception):
    """指定されたtokenが不正だったときに投げる"""


class SafeUser(BaseModel):
    """token を含まないUser"""

    id: int
    name: str
    leader_card_id: int

    class Config:
        orm_mode = True


class RoomInfo(BaseModel):
    room_id: int
    live_id: int
    joined_user_count: int
    max_user_count: int


class RoomUser(BaseModel):
    user_id: int
    name: str
    leader_card_id: int
    select_difficulty: int
    is_me: bool
    is_host: bool


def create_user(name: str, leader_card_id: int) -> str:
    """Create new user and returns their token"""
    token = str(uuid.uuid4())
    # NOTE: tokenが衝突したらリトライする必要がある.
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `user` (name, token, leader_card_id) VALUES (:name, :token, :leader_card_id)"
            ),
            {"name": name, "token": token, "leader_card_id": leader_card_id},
        )
        # print(result)
    return token


def _get_user_by_token(conn, token: str) -> Optional[SafeUser]:
    result = conn.execute(
        text(
            "SELECT `id`, `name`, `leader_card_id` FROM `user` WHERE `token` = :token"
        ),
        dict(token=token),
    )
    try:
        row = result.one()
    except NoResultFound:
        return None
    return SafeUser.from_orm(row)


def get_user_by_token(token: str) -> Optional[SafeUser]:
    with engine.begin() as conn:
        return _get_user_by_token(conn, token)


def update_user(token: str, name: str, leader_card_id: int) -> None:
    # このコードを実装してもらう
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE `user` SET `name` = :name , `leader_card_id`=:leader_card_id WHERE `token`=:token"
            ),
            dict(name=name, leader_card_id=leader_card_id, token=token),
        )
    return None


def create_room(token: str, live_id: int, select_difficulty: int) -> int:
    with engine.begin() as conn:
        result = conn.execute(
                text(
                    "SELECT * FROM `user` WHERE token = :token"
                ),
                {"token": token},
            )
        row = result.first()
        user_id = row["id"]
        result = conn.execute(
            text(
                "INSERT INTO `room` (live_id, joined_user_count, max_user_count) VALUES (:live_id, :joined_user_count, :max_user_count)"
            ),
            {"live_id": live_id, "joined_user_count": 1, "max_user_count": 4},
        )
        res = conn.execute(
            text(
                "INSERT INTO `room_member` (id, room_id, select_difficulty, is_host) VALUES (:id, :room_id, :select_difficulty, :is_host)"
            ),
            {"id": user_id, "room_id": result.lastrowid, "select_difficulty": select_difficulty, "is_host": 1},
        )
        return result.lastrowid


def list_room(token: str, live_id: int) -> list[RoomInfo]:
    if live_id == 0:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    "SELECT * FROM `room`"
                )
            )
            row = result.fetchall()
        return row
    else:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    "SELECT * FROM `room` WHERE live_id = :live_id"
                ),
                {"live_id": live_id}
            )
            row = result.fetchall()
        return row


def join_room(token: str, room_id: int, select_difficulty: int) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "SELECT * FROM `room` WHERE room_id = :room_id"
            ),
            {"room_id": room_id},
        )
        row = result.first()
        if row is None:
            return 3
        limit = row["joined_user_count"]
        if limit == 4:
            return 2
        else:
            result = conn.execute(
                text(
                    "SELECT * FROM `user` WHERE token = :token"
                ),
                {"token": token},
            )
            row = result.first()
            user_id = row["id"]
            result = conn.execute(
                text(
                    "INSERT INTO `room_member` (id, room_id, select_difficulty, is_host) VALUES (:id, :room_id, :select_difficulty, :is_host)"
                ),
                {"id": user_id, "room_id": room_id, "select_difficulty": select_difficulty, "is_host": 2},
            )
            result = conn.execute(
                text(
                    "UPDATE `room` SET joined_user_count = :joined_user_count WHERE `room_id` = :room_id"
                ),
                {"joined_user_count": limit + 1, "room_id": room_id},
            )
            return 1
    return 4


def wait_room(token: str, room_id: int) -> int:
    with engine.begin() as conn:
        res = conn.execute(
            text(
                "(SELECT * FROM `room_member` WHERE room_id = :room_id) NATURAL JOIN (SELECT * FROM `user`) "
            ),
            {"room_id": room_id}
        )
        result = conn.execute(
            text(
                "SELECT * FROM `room` WHERE room_id = :room_id"
            ),
            {"room_id": room_id},
        )
        row = result.first()
        #解散したroomはmax_join_memberを-1にする
        #スタートできるroomはmax_join_memberを0にする
        status = 1
        if row["max_user_count"] == -1:
            status = 3
        elif row["max_user_count"] == 0:
            status = 2
        return 1
        


def start_room(token: str, room_id: int) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE `room` SET `max_user_count` = :max_user_count WHERE `room_id`=:room_id"
            ),
            {"room_id": room_id, "max_user_count": 0}
        )
    return None


def end_room(token: str, room_id: int, judge_count_list: list[int], score: int):
    with engine.begin() as conn:
        result = conn.execute(
                text(
                    "SELECT * FROM `user` WHERE token = :token"
                ),
                {"token": token},
            )
        row = result.first()
        user_id = row["id"]
        for judge_count in judge_count_list:
            res = conn.execute(
                text(
                    "INSERT INTO `judge` (`id`, `room_id`, `judge_count`) VALUES (:id, :room_id, :judge_count)"
                ),
                {"id": user_id, "room_id": room_id, "judge_count": judge_count},
            )
        res = conn.execute(
            text(
                    "UPDATE `room_member` SET score = :score WHERE `room_id` = :room_id AND `id` = :id"
                ),
                {"score": score, "room_id": room_id, "id": user_id},
        )
        return None