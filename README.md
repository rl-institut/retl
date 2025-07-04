# Reiners ETL - RETL

## Installation

Requires rclone: https://rclone.org/install/
Install 

## Usage



## Implementation

Config without tokens is stored in the project folder.
At first usage, the config file is copied to the temp folder (including the project name in the path) and rclone is started pointing to temp config.
This assures that the login token is stored in the temp config file and not in project config, which could lead to accidental pushing of secrets.