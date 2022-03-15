from enum import Enum
from select import select

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from . import model
from .model import ResultUser, RoomInfo, RoomUser, SafeUser, join_room

app = FastAPI()

# Sample APIs


@app.get("/")
async def root():
    return {"message": "Hello World"}


# User APIs


class UserCreateRequest(BaseModel):
    user_name: str
    leader_card_id: int


class UserCreateResponse(BaseModel):
    user_token: str


class RoomCreateRequest(BaseModel):
    live_id: int
    select_difficulty: int


class RoomCreateResponse(BaseModel):
    room_id: int


class RoomListRequest(BaseModel):
    live_id: int


class RoomListResponse(BaseModel):
    room_info_list: list[RoomInfo]


class RoomJoinRequest(BaseModel):
    room_id: int
    select_difficulty: int


class RoomJoinResponse(BaseModel):
    join_room_result: int


class RoomWaitRequest(BaseModel):
    room_id: int


class RoomWaitResponse(BaseModel):
    status: int
    room_user_list: list[RoomUser]


class RoomStartRequest(BaseModel):
    room_id: int


class RoomEndRequest(BaseModel):
    room_id: int
    judge_count_list: list[int]
    score: int


class RoomResultRequest(BaseModel):
    room_id: int


class RoomResultResponse(BaseModel):
    result_user_list: list[ResultUser]


@app.post("/user/create", response_model=UserCreateResponse)
def user_create(req: UserCreateRequest):
    """新規ユーザー作成"""
    token = model.create_user(req.user_name, req.leader_card_id)
    return UserCreateResponse(user_token=token)


bearer = HTTPBearer()


def get_auth_token(cred: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    assert cred is not None
    if not cred.credentials:
        raise HTTPException(status_code=401, detail="invalid credential")
    return cred.credentials


@app.get("/user/me", response_model=SafeUser)
def user_me(token: str = Depends(get_auth_token)):
    user = model.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=404)
    # print(f"user_me({token=}, {user=})")
    return user


class Empty(BaseModel):
    pass


@app.post("/user/update", response_model=Empty)
def update(req: UserCreateRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    model.update_user(token, req.user_name, req.leader_card_id)
    return {}


@app.post("/room/create", response_model=RoomCreateResponse)
def room_create(req: RoomCreateRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    room_id = model.create_room(token, req.live_id, req.select_difficulty)
    return RoomCreateResponse(room_id=room_id)


@app.post("/room/list", response_model=RoomListResponse)
def room_list(req: RoomListRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    room_res = model.list_room(token, req.live_id)
    return RoomListResponse(room_info_list=room_res)


@app.post("/room/join", response_model=RoomJoinResponse)
def room_join(req: RoomJoinRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    room_res = model.join_room(token, req.room_id, req.select_difficulty)
    return RoomJoinResponse(join_room_result=room_res)


@app.post("/room/wait", response_model=RoomWaitResponse)
def room_wait(req: RoomWaitRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    room_res = model.wait_room(token, req.room_id)
    return RoomWaitResponse(join_room_result=room_res)


@app.post("/room/start", response_model=None)
def room_start(req: RoomStartRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    room_res = model.start_room(token, req.room_id)
    return room_res


@app.post("/room/end", response_model=None)
def room_end(req: RoomEndRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    room_res = model.end_room(token, req.room_id, req.judge_count_list, req.score)
    return room_res


@app.post("/room/result", response_model=RoomResultResponse)
def room_result(req: RoomResultRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    room_res = model.result_room(token, req.room_id)
    return room_res