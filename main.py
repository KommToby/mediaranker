import os
import sys
import argparse
import subprocess

def main():
    # An optional parameter to run the script to forcably update letterboxd data
    # Use this in case you have added more films since the last time it has been run
    parser = argparse.ArgumentParser(description='Process Letterboxd data')
    parser.add_argument('username', type=str, help='Letterboxd Username')
    parser.add_argument('--force', action='store_true', help='Force update users films')
    args = parser.parse_args()

    # Define letterboxd_username from passed in argument
    letterboxd_username = args.username

    if not letterboxd_username:
        parser.error("Letterboxd Username is required. Use 'python main.py <username>'")

    # Define the filename of films to check for
    filename = f"{letterboxd_username}_films.txt"

    # Depending if the filename exists, run media-sorter or scrape-letterboxd
    if not os.path.exists(filename) or args.force:
        print(f"Running film scraper for {letterboxd_username}")
        subprocess.run(['python', 'scrape-letterboxd.py', letterboxd_username])

    # We always end up running media-sorter-gui.py
    subprocess.run(['python', 'media_sorter_gui.py', letterboxd_username])

if __name__ == "__main__":
    main()