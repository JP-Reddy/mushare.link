import httpx
import re
import time
import jwt
from fastapi import HTTPException
from typing import Optional
from app.settings import settings
import os

def normalize_url(url: str) -> str:
    """Strip protocol, 'www.', query parameters, and trailing slashes. """

    url = re.sub(r"^(https?://)?(www\.)?", "", url)
    if url.endswith('/'):
        url = url[:-1]
    url = url.split('?')[0]
    return url

# Spotify API Functions

_spotify_token = None
_spotify_token_expires_at = 0

async def get_spotify_token():
    global _spotify_token, _spotify_token_expires_at

    current_time = int(time.time())
    
    # Refresh token if it's expiring in the next 60 seconds
    buffer = 60  

    if _spotify_token and current_time < (_spotify_token_expires_at - buffer):
        return _spotify_token

    auth_url = "https://accounts.spotify.com/api/token"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            auth_url,
            data={"grant_type": "client_credentials"},
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
        )
        response.raise_for_status()
        
        token_data = response.json()
        _spotify_token = token_data["access_token"]
        _spotify_token_expires_at = current_time + token_data["expires_in"]
        
        return _spotify_token

def extract_spotify_track_id(url: str) -> Optional[str]:
    match = re.search(r"spotify\.com/track/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None

async def get_track_details_from_spotify(track_id: str) -> Optional[dict]:
    token = await get_spotify_token()
    api_url = f"https://api.spotify.com/v1/tracks/{track_id}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 404:
            return None
        response.raise_for_status()
        
        data = response.json()
        isrc = data.get("external_ids", {}).get("isrc")
        name = data.get("name")
        artist = data.get("artists", [{}])[0].get("name")

        # Not all tracks might have an ISRC, so we need to proceed with text search if not present
        if not all([name, artist]):
            return None
            
        return {"isrc": isrc, "name": name, "artist": artist}

async def get_spotify_url(isrc: Optional[str], track_name: str, artist_name: str) -> Optional[str]:
    token = await get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    api_url = "https://api.spotify.com/v1/search"
    
    async with httpx.AsyncClient() as client:
        # 1. First search using ISRC
        if isrc:
            params = {"q": f"isrc:{isrc}", "type": "track", "limit": 1}
            response = await client.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            tracks = data.get("tracks", {}).get("items", [])
            if tracks:
                return tracks[0].get("external_urls", {}).get("spotify")

        # 2. Fallback to text search if ISRC is not present
        params = {"q": f"{track_name} {artist_name}", "type": "track", "limit": 1}
        response = await client.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        tracks = data.get("tracks", {}).get("items", [])
        if tracks:
            return tracks[0].get("external_urls", {}).get("spotify")
    
    return None

# Apple Music API Functions

_apple_music_token = None
_apple_music_token_expiry = 0

def get_apple_music_token():
    global _apple_music_token, _apple_music_token_expiry

    current_time = int(time.time())

    buffer = 60  

    if _apple_music_token and current_time < (_apple_music_token_expiry - buffer):
        return _apple_music_token

    # Create a new token
    team_id = settings.APPLE_MUSIC_TEAM_ID
    key_id = settings.APPLE_MUSIC_KEY_ID
    key_file_path = settings.APPLE_MUSIC_PRIVATE_KEY_PATH

    if not all([team_id, key_id, key_file_path]):
        raise HTTPException(status_code=500, detail="Apple Music credentials not fully configured")
        
    try:
        with open(key_file_path, 'r') as f:
            private_key = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Apple Music private key file not found at: {key_file_path}")

    # Token expires in 5 months (Apple's max is 6 months)
    expiry_duration = 15777000 - 3600 # 6 months in seconds, minus 1 hour buffer
    expiry_time = current_time + expiry_duration

    payload = {
        "iss": team_id,
        "iat": current_time,
        "exp": expiry_time
    }
    
    headers = { "kid": key_id }

    token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    
    _apple_music_token = token
    _apple_music_token_expiry = expiry_time
    
    return token

def extract_apple_music_info(url: str) -> Optional[dict]:
    """Extract storefront and song ID from Apple Music URL."""

    # album format music.apple.com/us/album/album-name/album-id?i=song-id
    match = re.search(r"music\.apple\.com/(\w+)/album/.+\?i=(\d+)", url)
    if match:
        return {"storefront": match.group(1), "id": match.group(2)}
    
    # song format music.apple.com/us/song/song-name/song-id
    match = re.search(r"music\.apple\.com/(\w+)/song/.+/(\d+)", url)
    if match:
        return {"storefront": match.group(1), "id": match.group(2)}
        
    return None

async def get_apple_music_url(isrc: Optional[str], track_name: str, artist_name: str, storefront: str = "us") -> Optional[str]:
    token = get_apple_music_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # 1. First search using ISRC
        if isrc:
            params = {"filter[isrc]": isrc}
            api_url = f"https://api.music.apple.com/v1/catalog/{storefront}/songs"
            response = await client.get(api_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    return data["data"][0].get("attributes", {}).get("url")

        # 2. Fallback to text search if ISRC is not present
        params = {"term": f"{track_name} {artist_name}", "types": "songs", "limit": 1}
        api_url = f"https://api.music.apple.com/v1/catalog/{storefront}/search"
        response = await client.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("results", {}).get("songs", {}).get("data"):
            return data["results"]["songs"]["data"][0].get("attributes", {}).get("url")
            
    return None

async def get_track_details_from_apple_music(song_id: str, storefront: str) -> Optional[dict]:
    token = get_apple_music_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    api_url = f"https://api.music.apple.com/v1/catalog/{storefront}/songs/{song_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        
        if response.status_code == 404:
            return None
        response.raise_for_status()

        data = response.json()
        if not data.get("data"):
            return None

        attributes = data["data"][0].get("attributes", {})
        isrc = attributes.get("isrc")
        name = attributes.get("name")
        artist = attributes.get("artistName")

        # Not all tracks have an ISRC
        if not all([name, artist]):
            return None

        return {"isrc": isrc, "name": name, "artist": artist}

async def get_isrc_from_apple_music(song_id: str, storefront: str) -> Optional[str]:
    token = get_apple_music_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    api_url = f"https://api.music.apple.com/v1/catalog/{storefront}/songs/{song_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        
        if response.status_code == 404:
            return None
        response.raise_for_status()

        data = response.json()
        if not data.get("data"):
            return None

        return data["data"][0].get("attributes", {}).get("isrc") 