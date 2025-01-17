import requests
import json
import logging
import re
import os
import time
from hashlib import md5
import csv
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
from base64 import b64encode

# Configure logging with rotation
log_handler = RotatingFileHandler("asset_removal.log", maxBytes=5 * 1024 * 1024, backupCount=5)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[log_handler])

# Load configuration from config.ini
config = ConfigParser()
config.read("config.ini")

# API Configuration
API_URL = config.get("API", "URL")
USERNAME = config.get("API", "Username")
PASSWORD = config.get("API", "Password")
TOKEN = config.get("API", "Token", fallback=None)  # Optional 2FA token

# Generate Authorization Header
auth_header = b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
API_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Basic {auth_header}"
}
if TOKEN:
    API_HEADERS["Token"] = TOKEN

# File paths
ASSET_FILE = "assets.csv"  # CSV file containing computer names
PROCESSED_FILE = "processed_assets.log"  # Log of deleted assets


def create_backup(file_path):
    """Creates a timestamped backup copy of the given file."""
    timestamp = int(time.time())
    backup_file = f"backup_{timestamp}.csv"
    try:
        if os.path.exists(file_path):
            os.rename(file_path, backup_file)
            logging.info(f"Backup created: {backup_file}")
            return backup_file
        else:
            logging.error(f"File '{file_path}' not found for backup.")
            return None
    except Exception as e:
        logging.error(f"Error creating backup for {file_path}: {e}")
        return None


def validate_computer_name(name):
    """Validates computer names (e.g., checking for invalid characters)."""
    return bool(re.match(r"^[a-zA-Z0-9._-]+$", name)) # update regex as needed


def read_asset_file(file_path):
    """Reads the computer names from a CSV file."""
    computer_names = []
    try:
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    computer_names.append(row[0].strip())
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
    return computer_names


def write_processed_asset(computer_name):
    """Logs processed (deleted) computer names."""
    try:
        with open(PROCESSED_FILE, "a") as file:
            file.write(f"{computer_name},{time.ctime()}\n")
    except Exception as e:
        logging.error(f"Error writing to processed log: {e}")


def find_asset_by_computer_name(computer_name):
    """
    Searches for an asset in InsightVM by computer name.
    """
    try:
        params = {"name": computer_name}
        response = requests.get(f"{API_URL}/assets", headers=API_HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        for asset in data.get("resources", []):
            if asset.get("hostName") == computer_name:
                return asset

        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while searching for asset '{computer_name}': {e}")
        return None


def delete_asset_by_id(asset_id):
    """Deletes an asset by its ID."""
    try:
        response = requests.delete(f"{API_URL}/assets/{asset_id}", headers=API_HEADERS)
        if response.status_code == 204:
            logging.info(f"Asset with ID {asset_id} deleted successfully.")
            return True
        else:
            logging.error(f"Failed to delete asset {asset_id}. Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while deleting asset {asset_id}: {e}")
        return False


def send_summary_report(success_count, failure_count, failed_assets):
    """Outputs a summary of the script run."""
    logging.info("\nSummary of Script Execution:\n")
    logging.info(f"Assets Successfully Deleted: {success_count}")
    logging.info(f"Assets Failed to Delete: {failure_count}")
    if failed_assets:
        logging.info("Failed Assets:")
        for asset in failed_assets:
            logging.info(f"- {asset}")


def main():
    if not os.path.exists(ASSET_FILE):
        logging.error(f"Asset file {ASSET_FILE} not found.")
        return

    backup_file = create_backup(ASSET_FILE)
    if backup_file is None:
        logging.error("Backup could not be created. Aborting process.")
        return

    computer_names = read_asset_file(backup_file)
    success_count, failure_count = 0, 0
    failed_assets = []

    for computer_name in computer_names:
        logging.info(f"Processing computer: {computer_name}")

        if not validate_computer_name(computer_name):
            logging.warning(f"Invalid computer name skipped: {computer_name}")
            continue

        asset = find_asset_by_computer_name(computer_name)
        if not asset:
            logging.warning(f"Computer not found: {computer_name}")
            continue

        asset_id = asset.get("id")
        logging.info(f"Computer '{computer_name}' found with ID: {asset_id}")

        if delete_asset_by_id(asset_id):
            write_processed_asset(computer_name)
            success_count += 1
        else:
            failed_assets.append(computer_name)
            failure_count += 1

    send_summary_report(success_count, failure_count, failed_assets)


if __name__ == "__main__":
    main()
