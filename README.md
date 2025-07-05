# MuShare

An app to convert and share music links between Spotify and Apple Music.

Check it out: [mushare.link](https://mushare.link) 

## How It Works

1. **ISRC-Based Search**: The main method involves getting the track's International Standard Recording Code (ISRC) from the source platform. The ISRC is a universal identifier for a specific recording. It makes it easy to find the track on the target platform.

2. **Fallback to Text-Based search**: Sometimes there is a mismatch in ISRC for the same track on different platforms. There are other cases where a track may not have an ISRC. We don't want to return a failure in such scenarios. We fallback to using the song's title and artist name to search instead.

## Project Structure

This repo contains both the backend API and the UI.

-   `/api`: A **FastAPI** application that handles all the link conversion logic, communication with external music services, and caching.
-   `/ui`: A **Svelte** single-page app.
-   `/.github/workflows`: Render API goes to sleep if the app is inactive for 15min. Created a **GitHub Actions** workflow that queries the API every few min which helps avoid the API from sleeping. 

## Deployment
-   API on **Render**
-   UI on **Netlify**
