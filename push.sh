#!/bin/bash

find . -name '*.html' -delete
git status
git add .
git commit -m "update"
git push https://github.com/charliewprice/AgBotAnalytics master
