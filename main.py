import argparse
import time
import requests
import logging

import googleapiclient.discovery

CHANNEL_LIST_PATH = "/api/channel/"
DOWNLOADS_CHECK_PATH = "/api/download/%s"
VIDEOS_CHECK_PATH = "/api/video/%s"
ADD_TO_QUEUE_PATH = "/api/download/"


def collect_channels(url: str, token: str) -> list[str]:
    headers = {"Authorization": f"Token {token}"}
    channels = list()
    page = 1
    last_page_reached = True
    while last_page_reached:
        request = requests.get(f"{url}{CHANNEL_LIST_PATH}?page={page}", headers=headers)
        if request.status_code != 200:
            raise Exception(f"Request failed with status code {request.status_code}")

        if len(content := request.json()["data"]) != 0:
            channels.extend(content)
            page += 1
            continue

        last_page_reached = False

    return [c["channel_id"] for c in channels if c["channel_subscribed"]]


def get_latest_videos(
    channel_id: str, youtube_token: str, max_result: int
) -> list[str]:
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=youtube_token
    )

    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = request.execute()
    playlist_id: str = response["items"][0]["contentDetails"]["relatedPlaylists"][
        "uploads"
    ].replace("UU", "UULF")
    request = youtube.playlistItems().list(
        part="snippet,contentDetails", maxResults=max_result, playlistId=playlist_id
    )
    response = request.execute()
    return [item["snippet"]["resourceId"]["videoId"] for item in response["items"]]


def video_exists_locally(url: str, token: str, video_id: str) -> bool:
    headers = {"Authorization": f"Token {token}"}
    endpoints: list[str] = [
        DOWNLOADS_CHECK_PATH % video_id,
        VIDEOS_CHECK_PATH % video_id,
    ]

    for path in endpoints:
        full_url = f"{url}{path}"
        response = requests.get(full_url, headers=headers)
        if response.status_code == 403:
            raise Exception("Request failed. Token is invalid.")
        elif response.status_code == 200:
            # Video found in this endpoint
            return True
        elif response.status_code != 404:
            raise Exception(
                f"Request to {full_url} failed with status code {response.status_code}."
            )
        # If 404, continue to check the next endpoint

    # Video not found in any of the checked endpoints
    return False


def add_to_queue(url: str, token: str, video_id: str, autostart: bool):
    headers = {"Authorization": f"Token {token}"}
    request = requests.post(
        f"{url}{ADD_TO_QUEUE_PATH}?autostart={str(autostart).lower()}",
        headers=headers,
        json={
            "data": [
                {
                    "youtube_id": video_id,
                    "status": "pending",
                }
            ]
        },
    )
    if request.status_code != 200:
        raise Exception(f"Request failed with status code {request.status_code}")
    return


def scan(url: str, token: str, youtube_token: str, autostart: bool):
    logging.info(f"Scanning started for {url}")
    channels = collect_channels(url, token)
    logging.info(f"Found {len(channels)} channels")

    for channel in channels:
        logging.info(f"Querying youtube api for {channel}")
        try:
            videos = get_latest_videos(channel, youtube_token, max_result=3)
        except Exception as e:
            logging.error(f"Failed to query youtube api for {channel}")
            logging.error(e)
            continue
        logging.info(f"Found {len(videos)} videos")
        for video in videos:
            if video_exists_locally(url, token, video):
                logging.info(f"Video {video} already exists locally")
                continue
            logging.info(f"Adding {video} to queue")
            add_to_queue(url, token, video, autostart=autostart)


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        prog="tubearchivist-subscription-listener",
        description="this script will query the youtube api to get the latest videos from all channels you are subscribed to in your Tubearchvist instance. It will then add those videos to the queue. this script runs endlessly.\n\n WARNING: the youtube data api has a quota of 10000 units. Each run costs 2 units per channel. Each run will process every channel. Select an interval that does not exhaust your quota.\n\n Example: 100 channels * 2 * 50 times per day = 10000\n This is approximately twice per hour (or every 30 minutes) for 100 channels\n\nYou might want to request a quota increase on GCP.",
    )

    parser.add_argument(
        "-u", "--url", required=True, type=str, help="Tube archivist API url"
    )
    parser.add_argument(
        "-t", "--token", type=str, required=True, help="Tube archviist api token"
    )
    parser.add_argument(
        "-yt", "--youtube-token", type=str, required=True, help="Youtube API token"
    )

    parser.add_argument(
        "-r", "--repeat", type=int, default=60, help="number of refreshes per day"
    )
    parser.add_argument("-a", "--autostart", type=bool, help="autostart downloads")

    args = parser.parse_args()

    sleep_time = (
        24 * 60 * 60
    ) // args.repeat  # calculates the interval based on num repeats per day

    logging.info(f"Sleeping for {sleep_time} seconds. {args.repeat} scans per 24 hours")
    logging.info(f"Autostart: {args.autostart}")

    while True:
        scan(args.url, args.token, args.youtube_token, args.autostart)
        time.sleep(sleep_time)


if __name__ == "__main__":
    raise SystemExit(main())
