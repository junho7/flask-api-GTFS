# Junho Park
## Local Test

1. Install dependencies

    ```bash
    python3 -m pip install -r requirements.txt
    ```

2. Run the Flask server
    ```bash
    python3 run.py
    ```

3. How to test
- In Postman, `post` the request as below:

  ```bash
  localhost:8000/schedule
  ```
- With JSON like below:
  ```jsonv
  {"coordinates": {"latitude": "41.09", "longitude": "-73.92"}, "destination_station_id": "TARRYT", "limit": 10, "order": "asc"}
  ```

## Test on Heroku

- API Endpoint
  ```
  https://cedar-challenge.herokuapp.com/schedule
  ```