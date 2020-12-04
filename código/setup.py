import os

def setup():
    with open(os.path.join(".", "config"), "w") as config_file:
        client_id=input("Client ID: ").strip()
        client_secret=input("Client secret: ").strip()
        redirect_uri=input("Redirect URI: ").strip()

        config_file.writelines(["client_id="+client_id,
                                "\nclient_secret="+client_secret,
                                "\nredirect_uri="+redirect_uri])