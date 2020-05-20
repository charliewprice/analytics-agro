#!/bin/bash

find . -name '*-checkpoint.ipynb' -delete
find . -name '*.html' -delete
find . -name '*.pyc' -delete
rm -rf PorterFarms/EnvMonitoring/.ipynb_checkpoints
rm -rf PorterFarms/InfMonitoring/.ipynb_checkpoints
rm -rf PorterFarms/.ipynb_checkpoints

git status
git add .
git commit -m "update"
git push https://github.com/charliewprice/AgBotAnalytics master

