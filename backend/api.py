import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import AccessToken, ListRoomsRequest, LiveKitAPI, VideoGrants
from pydantic import BaseModel

load_dotenv()

# Get LiveKit API key and secret from environment variables
api_key = os.environ.get("LIVEKIT_API_KEY")
api_secret = os.environ.get("LIVEKIT_API_SECRET")
livekit_url = os.environ.get("LIVEKIT_URL")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RoomInfo(BaseModel):
    name: str
    num_participants: int
    creation_time: int
    metadata: str | None = None


@app.get("/api/rooms", response_model=list[RoomInfo])
async def list_active_rooms():
    """List all active customer service rooms"""
    if not api_key or not api_secret:
        raise HTTPException(
            status_code=500, detail="LiveKit API credentials not configured"
        )

    try:
        async with LiveKitAPI() as client:
            rooms = await client.room.list_rooms(ListRoomsRequest())

            # Filter for customer service rooms (inbound/outbound)
            cs_rooms = []
            for room in rooms.rooms:
                if (
                    room.name.startswith("inbound") or room.name.startswith("outbound")
                ) and room.num_participants > 0:
                    cs_rooms.append(
                        RoomInfo(
                            name=room.name,
                            num_participants=room.num_participants,
                            creation_time=room.creation_time,
                            metadata=room.metadata,
                        )
                    )

            return cs_rooms
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list rooms: {str(e)}"
        ) from e


@app.get("/api/join-token")
async def get_join_token(
    room_name: str = Query(...), participant_name: str = Query(...)
):
    """Get a token to join an existing customer service room"""
    if not api_key or not api_secret:
        raise HTTPException(
            status_code=500, detail="LiveKit API credentials not configured"
        )

    if not room_name or not participant_name:
        raise HTTPException(
            status_code=400, detail="Room name and participant name are required"
        )

    try:
        # Verify room exists and has participants
        async with LiveKitAPI() as client:
            rooms = await client.room.list_rooms(ListRoomsRequest())
            room_exists = any(
                r.name == room_name and r.num_participants > 0 for r in rooms.rooms
            )

            if not room_exists:
                raise HTTPException(
                    status_code=404, detail="Room not found or has no participants"
                )

        # Create token for joining existing room
        token = (
            AccessToken(api_key, api_secret)
            .with_identity(f"supervisor_{participant_name}")
            .with_name(participant_name)
            .with_grants(
                VideoGrants(
                    room=room_name,
                    room_join=True,
                    can_subscribe=True,
                    can_publish=True,
                    can_publish_data=True,
                )
            )
        )

        return {"token": token.to_jwt(), "url": livekit_url, "room_name": room_name}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate token: {str(e)}"
        ) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
