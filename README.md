# Photobooks Online
Photobooks online is a web application designed to store and share your photos packed (thematically, or else) inside photobooks, share them with others, as well as follow other people's photobooks

Project was made using Agile methodology (Scrum Framework) using Atlassian Jira software <br>
![](https://i.ibb.co/7kZSL9y/photo-2020-11-19-10-55-38.jpg)

App design was made in Figma <br>
![](https://i.ibb.co/cgWjpbs/photo-2020-11-19-11-00-07.jpg)

Database ERM in Lucidchart <br> 
![](https://i.ibb.co/2FK0Y4P/photo-2020-11-19-10-59-07.jpg)

Testing
Testing was realized as a separate sprint with all of the existing functionalities. We decided to not automate the process because doing so would slow down our actual software development progress, as configuring automation of tests would take more time than the actual development.

VCS Usign Git / Github <br>

## Installation
1. Clone the repository
2. install the packages required (from requirements.txt)
  in pip you can do that like this:
  ```bash
  pip install -r requirements.txt
  ```
3. Create the database (You can clear it the same way):
```bash
python3
from app import app, db, reinitialize
with app.app_context():
  reinitialize(db)
```

4. Run the app:
```bash
export FLASK_APP=app.py
flask run
```

## Usage:
Flask app manages the application on localhost:5000 (or 5001 if that is closed and so on)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
