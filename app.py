"""
This module handles the application versioning using semantic_version.
"""
import datetime
import logging

import semantic_version
from fastapi import FastAPI, HTTPException
import requests

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# FastAPI instance
app = FastAPI()

@app.get("/version")
async def version():
    """Return application version."""
    app_version = semantic_version.Version('0.0.1')
    return str(app_version)

@app.get("/temperature")
async def temperature():
    """Return average temperature based on all sensebox data."""
    data_format = "json"
    phenomenon = "temperature"
    date = datetime.datetime.now().isoformat() + "Z"
    try:
        req = requests.get(
            f'https://api.opensensemap.org/boxes?date={date}&phenomenon={phenomenon}&format={data_format}',
            timeout=120)
        response = req.json()
    except requests.RequestException as e:
        logger.error("Error fetching temperature data", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e

    measurement = 0
    counter = 0
    for box in response:
        for sensor in box.get("sensors", []):
            if sensor.get("title") == "Temperature" and sensor.get("lastMeasurement"):
                counter += 1
                measurement += float(sensor["lastMeasurement"].get("value", 0))

    if counter == 0:
        raise HTTPException(status_code=404, detail="No temperature data found")
    data = measurement / counter
    return {"message": f"The average temperature is {round(data, 2)}"}

# Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8083)
