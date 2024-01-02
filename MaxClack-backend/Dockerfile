FROM python:3.12

WORKDIR /app

COPY ./backend.py ./backend.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

# flask run by default runs on port 5000
EXPOSE 5000

# https://flask.palletsprojects.com/en/3.0.x/quickstart/
# If you have the debugger disabled or trust the users on your network,
# you can make the server publicly available simply by adding --host=0.0.0.0 to the command line
CMD [ "python", "-m", "flask", "--app", "backend", "run", "--host=0.0.0.0" ]