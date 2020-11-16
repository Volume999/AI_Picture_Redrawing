# Photobooks Online
Photobooks online is a web application designed to store and share your photos packed (thematically, or else) inside photobooks, share them with others, as well as follow other people's photobooks

## Installation
1. Clone the repository
2. install the packages required (from requirements.txt)
  in pip you can do that like this:
  ```bash
  pip install -r requirements.txt
  ```
3. Run the app:
```bash
export FLASK_APP=app.py
flask run
```
4. for clearing the database:
```bash
python3
from app import app, db, reinitialize
with app.app_context():
  reinitialize(db)

```
## Usage:
Flask app manages the application on localhost:5000 (or 5001 if that is closed and so on)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
