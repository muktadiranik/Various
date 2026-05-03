from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_async_db
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomOut, RoomList


router = APIRouter()


@router.post("/", response_model=RoomOut)
async def create_room(room_in: RoomCreate, db: AsyncSession = Depends(get_async_db)):
    db_room = Room(**room_in.model_dump())
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return db_room


@router.get("/", response_model=RoomList)
async def list_rooms(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Room).order_by(Room.id))
    rooms = result.scalars().all()
    return {"rooms": rooms}


@router.get("/{room_id}", response_model=RoomOut)
async def get_room(room_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "Room not found")
    return room


@router.delete("/{room_id}")
async def delete_room(room_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "Room not found")
    await db.delete(room)
    await db.commit()
    return {"message": "Room deleted"}


@router.patch("/{room_id}", response_model=RoomOut)
async def update_room(room_id: int, room_in: RoomCreate, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "Room not found")
    room.name = room_in.name
    await db.commit()
    await db.refresh(room)
    return room
