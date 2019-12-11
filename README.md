# FlaskCommentAPI

This is a toy project using docker and flask to set up a simple api to log comments and likes to those comments.

## Setup

Setup will require git and docker.

First clone this repo:

```
git clone https://github.com/AlexNVanPatten/FlaskCommentAPI.git
```
Then navigate to the top level folder of this repo and run:
```
docker-compose build
```
Then, run
```
docker-compose up
```
From there docker should set everything up. For instructions 
on how to use the api, once the container is up you can navigate to
```
127.0.0.1:80/readme
```
