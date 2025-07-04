# Reiners ETL - RETL

CLI tool to get raw data from different remotes and store them locally in your project folder.
The remotes and files which shall be downloaded, are read from a `.retl.yaml` configuration file,
which must be present in your project folder. 

## Usage

Note: Requires [rclone](https://rclone.org/install/) to be installed on your system.

Here are some options to use the tool:
- with [`uv`](https://docs.astral.sh/uv/) run: `uv tool run reiners-etl`
- with [`pipx`](https://pipx.pypa.io/stable/) run: `pipx run reiners-etl`

Usage with as python script is not recommended as you would have to install it using pip, 
which installs dependencies you might not want in your system or project python. 

This downloads all related files to your system. 
You might need to log in to a cloud provider first, this happens automatically.

## Configuration

The configuration file in which remotes and files are defined must be stored as `.retl.yaml` in your project folder.
A name defines each remote, and each remote holds information for rclone access point as well as file sources and targets, 
which are project-dependent.
You can run `rclone config` (you can add `--config <path-to-local-config-file>` to store configuration locally) to define a new remote. 
After configuration, you must translate rclone configuration format (`.conf`) into YAML format used by retl.
Additionally, you must define files which shall be downloaded from remote by defining a list of files with related sources and targets.
To list possible files to download from remote, you can run `rclone tree <name-of-remote>:` (note: ":" is crucial here). 

Example configuration file:
```yaml
sharepoint:
  type: onedrive
  client_id:
  client_secret:
  drive_id: b!J5kKSe-f_E6loyOdRZSpoFA76THG7klMiQjFV3H8CDreOkX_58VVRI8LsCw0U5sg
  drive_type: documentLibrary
  files:
    - name: slider
      source: "400_General/02 Arbeitspakete/03 AP Simulation und StEmp-Tool/2025-04-28_Daten.xlsx"
      target: "data/"
    - name: scenarios
      source: "400_General/02 Arbeitspakete/03 AP Simulation und StEmp-Tool/Scenarios.xlsx"
      target: "data/"
```


## Implementation

Config without tokens is stored in the project folder.
At first usage, the config file is copied to the temp folder (including the project name in the path) and rclone is started pointing to temp config.
This assures that the login token is stored in the temp config file and not in project config, which could lead to accidental pushing of secrets.
Afterwards, remote authentification is done if necessary.
Finally, files from all remotes are downloaded.