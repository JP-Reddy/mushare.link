from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from app.cache import get_link_from_cache, set_link_in_cache, get_cache_stats
from app.settings import settings
from app.services import (
    normalize_url,
    extract_spotify_track_id, 
    get_track_details_from_spotify,
    extract_apple_music_info,
    get_track_details_from_apple_music,
    get_spotify_url,
    get_apple_music_url,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for converting music links between Spotify and Apple Music",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConvertRequest(BaseModel):
    source_url: HttpUrl

class ConvertResponse(BaseModel):
    source_url: HttpUrl
    converted_url: HttpUrl

@app.get("/")
def roooooot():
    return {"status": "yo mama so fat she can't convert links"}

@app.post("/api/v1/convert", response_model=ConvertResponse)
async def convert_link(request: ConvertRequest):
    print(f"request: {request}")
    source_url = str(request.source_url)
    
    # 1. Normalize URL and check cache
    normalized_source_url = normalize_url(source_url)
    cached_url = get_link_from_cache(normalized_source_url)
    if cached_url:
        return ConvertResponse(source_url=source_url, converted_url=cached_url)

    # 2. Get track details from the source URL
    source_details = None
    service_type = None

    if "spotify.com" in source_url:
        service_type = "spotify"
        track_id = extract_spotify_track_id(source_url)
        print(f"track_id: {track_id}")
        if not track_id:
            raise HTTPException(status_code=400, detail="Hmmm, invalid Spotify track URL")
        source_details = await get_track_details_from_spotify(track_id)
        
    elif "apple.com" in source_url or "music.apple.com" in source_url:
        service_type = "apple"
        apple_info = extract_apple_music_info(source_url)
        if not apple_info:
            raise HTTPException(status_code=400, detail="Hmm, invalid Apple Music URL")
        source_details = await get_track_details_from_apple_music(apple_info["id"], apple_info["storefront"])
    else:
        raise HTTPException(status_code=400, detail="Uh oh, invalid URL provided :(")

    if not source_details:
         raise HTTPException(status_code=404, detail="Oops, could not retrieve details for the provided link :(")

    # 3. Use details to get the converted link from the target service
    converted_url = None
    
    if service_type == "spotify":
        converted_url = await get_apple_music_url(
            isrc=source_details.get("isrc"),
            track_name=source_details["name"],
            artist_name=source_details["artist"]
        )
    elif service_type == "apple":
        converted_url = await get_spotify_url(
            isrc=source_details.get("isrc"),
            track_name=source_details["name"],
            artist_name=source_details["artist"]
        )

    if not converted_url:
        raise HTTPException(status_code=404, detail="Could not find a match")

    # 4. Cache and return the result
    set_link_in_cache(normalized_source_url, converted_url)

    return ConvertResponse(source_url=source_url, converted_url=converted_url)

@app.get("/api/v1/cache/stats")
def cache_stats():
    return get_cache_stats() 