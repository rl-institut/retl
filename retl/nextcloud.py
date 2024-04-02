import os
from collections import namedtuple

from pathlib import Path
import requests
from defusedxml.ElementTree import fromstring

NEXTCLOUD_USER = os.getenv("NEXTCLOUD_USER")
NEXTCLOUD_PASSWORD = os.getenv("NEXTCLOUD_PASSWORD")
NEXTCLOUD_HOST = "https://wolke.rl-institut.de"
NEXTCLOUD_OCS_API = "ocs/v1.php"
NEXTCLOUD_WEBDAV_API = "remote.php/dav/files"

File = namedtuple("File", ["path", "is_directory"])


# Get UUID:
def get_user_id(session: requests.Session) -> str:
    response = session.get(
        f"{NEXTCLOUD_HOST}/{NEXTCLOUD_OCS_API}/cloud/user",
        headers={"OCS-APIRequest": "true"},
    )
    et = fromstring(response.text)
    user_id = et.find("data").find("id").text
    return user_id


# Get files in folder:
def get_files_in_folder(session: requests.Session, folder: str) -> list[File]:
    response = session.request(
        method="PROPFIND",
        url=f"{NEXTCLOUD_HOST}/{NEXTCLOUD_WEBDAV_API}/{session.user_id}/{folder}",
    )
    namespaces = {
        "d": "DAV:",
    }
    root = fromstring(response.text)
    elements = root.findall(".//d:response", namespaces)
    for element in elements[1:]:
        href = element.find("./d:href", namespaces).text
        path = "/".join(href.split("/")[5:])
        resourcetype_element = element.find(".//d:resourcetype", namespaces)
        try:
            # Element is directory
            yield File(path, "collection" in resourcetype_element[0].tag)
        except IndexError:
            # Element is a file
            yield File(path, False)


def download(session: requests.Session, path: str, destination: Path | str):
    if isinstance(destination, str):
        destination = Path(destination)
    for file in get_files_in_folder(session, path):
        if file.is_directory:
            destination = destination / file.path.split("/")[-2]
            destination.mkdir(exist_ok=True)
            download(session, file.path, destination)
        if not file.is_directory:
            filename = file.path.split("/")[-1]
            response = session.request(
                method="GET", url=f"{NEXTCLOUD_HOST}/{NEXTCLOUD_WEBDAV_API}/{session.user_id}/{file.path}", stream=True
            )
            with open(destination / filename, "wb") as f:
                for chunk in response.raw.stream(1024, decode_content=True):
                    if chunk:
                        f.write(chunk)


session = requests.Session()
session.auth = (NEXTCLOUD_USER, NEXTCLOUD_PASSWORD)
session.user_id = get_user_id(session)

folder = "359_EmPowerPlan/Projektinhalte/Daten_Analyse/_Pipeline_Ergebnisdaten/2024-03-13/datapackage/data"
files = list(get_files_in_folder(session, folder))
download(session, folder, "./data")
