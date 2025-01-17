# rapid7-vm-asset-removal

 Remove assets from rapid7 insight vm.

## Overview

This script automates the process of removing computers (assets) from **Rapid7 InsightVM (On-Premises)** using its API.

## Disclaimers

- **Use at Your Own Risk**: This script is provided "as-is" with no guarantees or warranties of any kind.
- **No Liability**: The author is not responsible for any damages, data loss, or misconfigurations caused by using this script.
- **InsightVM On-Prem Only**: This script is for Rapid7 InsightVM's on-premises deployment. It is not compatible with cloud-based versions which, uses the v4 API.
- **Basic Authentication Required**: The script requires valid InsightVM credentials.

## Features

- **Backup Support**: Automatically creates a timestamped backup of the input file (`assets.csv`) before processing.
- **Input File Parsing**: Reads a list of computer names from a CSV file.
- **Validation**: Validates the computer names for correct formatting.
- **Search and Deletion**: Searches for computers by name in InsightVM, retrieves their IDs, and deletes them using the API.
- **Logging**: Logs all operations, including errors and successful deletions, to `asset_removal.log`.
- **Summary Report**: Outputs a detailed summary of the operation at the end of execution.

## How It Works

1. **Setup**: Before running, configure the `config.ini` file with your InsightVM credentials and API endpoint.
2. **Input File**: Create a `assets.csv` file with a list of computer names, one per line.
3. **Execution**:
   - The script reads the computer names from `assets.csv`.
   - Validates the format of each name.
   - Searches InsightVM for each computer by name.
   - Deletes the computer if found and logs the result.

## Prerequisites

1. **Python**: Ensure Python 3.6 or higher is installed.
2. **Dependencies**: Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration File**: Create a `config.ini` file in the script directory:

   ```ini
   [API]
   URL = https://<host>:<port>/api/3
   Username = your_username
   Password = your_password
   Token = optional_token_if_enabled
   ```

   - Replace `<host>:<port>` with your InsightVM server address.
   - Replace `your_username` and `your_password` with valid API credentials.

## Running the Script

To run the script, use:

```bash
python asset_removal.py
```

### Example

1. Prepare a CSV file (`assets.csv`) with computer names:

    computer1.example.com
    computer2.example.com

2. Run the script. It will:
   - Backup `assets.csv` to a timestamped file.
   - Search for each computer name in InsightVM.
   - Delete the computer if found.
   - Log results to `asset_removal.log`.

3. Review the summary report displayed in the console or check `processed_assets.log` for processed computers.

## Limitations

- Only works with InsightVM On-Premises using Basic Authentication.
- The script is designed for assets identified by **computer name**.

## License and Disclaimer

This script is open-source and licensed under the MIT License. Use it responsibly and always test in non-production environments before deploying.
