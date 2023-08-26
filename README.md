# InterPoll - A Polling App

## Description

This is a polling app that allows users to create polls and vote on them. Users can also view the results of the polls.

## Installation

To install this app, clone the repository and run `pip install -r requirements.txt` to install the dependencies. 

Copy the `.env.example` file to `.env` and fill in the values.

Then, run `python -m interpoll`, and the app will be running on `localhost:5000`.

For a production setup, use a WSGI server such as [Gunicorn](https://gunicorn.org/), instead of the built-in Flask server.

## Usage

Go to <http://localhost:5000> to view the app.