#!/bin/sh
sudo pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

