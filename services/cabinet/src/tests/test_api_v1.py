import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient  # type: ignore

from app_types import map

# https://stackoverflow.com/questions/61582142/test-pydantic-settings-in-fastapi

game_map: map.GameMap = [
    [
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
        {"type": map.CellType.SPAWN},
    ],
    [
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
    ],
    [
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
    ],
    [
        {"type": map.CellType.SPAWN},
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
        {"type": map.CellType.FIELD},
    ],
]

game_map_raw = [[{**cell, "type": cell["type"].value} for cell in row] for row in game_map]


@pytest.mark.asyncio
async def test_create_map(app: FastAPI, client: TestClient, mongo_client: AsyncMongoMockClient):
    response = client.post(
        app.url_path_for("create_map"), json={"map": game_map_raw}, headers={"X-User-Id": "1"}
    )
    assert response.status_code == 201
    responce_json = response.json()
    maps_collection = mongo_client["tests"]["maps"]

    saved_data = await maps_collection.find_one({"_id": ObjectId(responce_json["id"])})
    assert saved_data["map"] == game_map
    assert saved_data["meta"] == {
        "version": 1,
        "points_of_interest": {map.CellType.SPAWN: [[0, 3], [3, 0]]},
        "max_players": 2,
    }
