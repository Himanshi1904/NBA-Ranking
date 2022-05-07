# NBA-Ranking

## Introduction
In this repo, I have used python to scrape "ESPN" data and extracted information like:

- Teams participating in playoffs
- Information about the players from each roster:
    
    - Player's name, age and yearly salary etc
    - Stats for 2020-2021: points scored, games played, assists and rebounds
    
- We are using the above information to create a metric (weighted ratio) that helps us in selecting top 10 NBA players.

## Prerequisites required:
 
- Programming Language - Python (Code tested on 3.9.4)
- SQLite (Comes preinstalled in macOS)

## Running the Code

- Clone this repo and go to the folder
  
- Create a virtual env:

    - python -m venv "name_of_env" (eg: nba)
 
- Activate the venv -    
    - source nba/bin/activate
    
- Run below cmd to install packages:

    - pip install -r requirements.txt
    
- Run the code:
  
    - python Code.py
 
