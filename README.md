# py-charge-amps

A Flask-based web application for retrieving and exporting charging session data from Charge Amps systems.

## Features

- Web interface for entering RFID and date range.
- Retrieves charging session data using Charge Amps API.
- Exports results as an Excel (`.xlsx`) file.
- Optional endpoint to fetch registered RFID tags.

## Requirements

- Python 3.8+
- A `mycfg.ini` configuration file containing your Charge Amps API credentials and base URL.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/py-charge-amps.git
   cd py-charge-amps```

2. Create a virtual environment and activate it:
    ```python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
```bash 
pip install -r requirements.txt
```

4.	Add a mycfg.ini file in the root directory with the following structure:
```bash
[user]
email = your-email@example.com
password = your-password
apiKey = your-api-key

[general]
baseUrl = https://api.chargeamps.com
pricekWh = 0.30
```


## Usage
Start the Flask application:
```bash
python app.py
```
Then open your browser and go to http://127.0.0.1:5000/.

## Endpoints
### `/`
- **GET**: Displays the form.
- **POST**: Accepts RFID and date range, fetches charging sessions, and downloads an .xlsx file.

### `/get_rfid_tags`
- **POST**: Returns available RFID tags as a JSON response.

## File Structure
```bash
app.py                   # Main Flask application
chargeampsclient.py      # API client for Charge Amps
chargeampscfgparser.py   # INI configuration parser
xlsxresultwriter.py      # Excel writer for output
templates/index.html     # HTML template for form
mycfg.ini                # User and API configuration
```

## Running with Docker

This project includes a multi-stage `Dockerfile` for building and running the application in a lightweight container.

### Build the Docker image

From the root of the project directory, run:

```bash
docker build -t py-charge-amps .
```

This builds the image using:
- Build stage: Installs all Python dependencies into a minimal install directory using Alpine Linux.
- inal stage: Copies only the necessary files and dependencies into the final image.

## Run the container

You can run the container with:
```bash
docker run -p 5000:5000 --env-file .env py-charge-amps
```

Alternatively, if you need to bind a local mycfg.ini file into the container:
```bash
docker run -p 5000:5000 -v $(pwd)/mycfg.ini:/app/mycfg.ini py-charge-amps
```

## Notes
- The app listens on port 5000 by default.
- hypercorn is used as the ASGI server.
- You can configure credentials and settings via mycfg.ini, which should be present in the working directory or mounted as a volume.

## License

MIT License. See LICENSE file for details.