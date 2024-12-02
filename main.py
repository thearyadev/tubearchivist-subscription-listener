import argparse

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="tubearchivist-subscription-listener",
        description="this script will delete all videos that are watched and older than a specified number of days",
    )

    parser.add_argument(
        "-a",
        "--min-watched-age",
        required=True,
        type=int,
        help="Min age in days from the watched date",
    )
    parser.add_argument(
        "-u", "--url", required=True, type=str, help="Tube archivist API url"
    )
    parser.add_argument(
        "-t", "--token", type=str, required=True, help="Tube archviist api token"
    )
    parser.add_argument("-e", "--endless", action="store_true")
    parser.add_argument("-s", "--sleep", type=int, required=False, default=10)
    args = parser.parse_args()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
