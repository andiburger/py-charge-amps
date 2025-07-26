# py-charge-amps

A Flask-based web application for retrieving and exporting charging session data from Charge Amps systems.

## Features

- Web interface for entering RFID and date range.
- Retrieves charging session data using Charge Amps API.
- Exports results as an Excel (`.xlsx`) file.
- Optional endpoint to fetch registered RFID tags.

## Requirements

- Python 3.8+

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


## Usage
Start the Flask application:
```bash
python app.py
```
Then open your browser and go to http://127.0.0.1:5000/.

Click on Configure Connection Settings and fill out the required information (username, password, api key, etc.)

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
docker run -p 5000:5000 py-charge-amps
```

## Notes
- The app listens on port 5000 by default.
- hypercorn is used as the ASGI server.
- You can configure credentials within the website

## License

MIT License. See LICENSE file for details.
