# energous-packaging

## Configuration

Create a `.env` file from `.env.example` and set a unique `SECRET_KEY`,
`ADMIN_PASSWORD`, and the database connection values before starting the app.
The app loads `.env` automatically for local runs and exits during startup if
any required value is missing. For local development, start it with
`python run.py`.

Run with `docker compose up --build`. The container uses Gunicorn and stores
timestamps in the `Asia/Manila` timezone. VI reads unit state from
`energous.esense_main`, and VI scan records and admin reports use the production
`energous.esense_packaging` table. Operators scan only the Prog ID; the app retrieves
its associated serial number from `energous.esense_progtest` for validation and
recording, and packaging records also store the scanned `prog_id`. Failed
inspections are recorded with serial suffixes
`_1` through `_3` and matching `test_rep` values; a fourth FAIL attempt is not
accepted.
