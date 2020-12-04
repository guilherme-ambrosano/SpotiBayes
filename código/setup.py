import os
from getpass import getpass

def setup():
    with open(os.path.join(".", "config"), "w") as config_file:
        redirect_uri=input("Redirect URI: ").strip()
        client_id=getpass("Client ID: ").strip()
        client_secret=getpass("Client secret: ").strip()

        config_file.writelines(["client_id="+client_id,
                                "\nclient_secret="+client_secret,
                                "\nredirect_uri="+redirect_uri])