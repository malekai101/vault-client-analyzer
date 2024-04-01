import argparse
import os
from kmip import *

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--kmip", help="run kmip client analysis",
                    action="store_true")
args = parser.parse_args()

def validate_input(arg_dict) -> dict:

    # verify  the vault information is populated
    if os.environ.get("VAULT_ADDR") is None or os.environ.get("VAULT_TOKEN") is None:
        raise KeyError(
            "The environmental varaibles VAULT_ADDR and VAULT_TOKEN must be defined"
        )

    settings = {
        "vault_address": os.environ.get("VAULT_ADDR"),
        "vault_token": os.environ.get("VAULT_TOKEN"),
        "kmip": args.kmip
    }
    return settings


def main_routine():
    """
    The program entry point
    :return: None
    """
    settings = validate_input(args)
    if not settings["kmip"]:
        print("KMIP not selected.  No work to do")
        exit(0)

    kmip = KMIP_Reporter(settings["vault_address"], settings["vault_token"])
    report = kmip.build_kmip_report()
    print(report)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main_routine()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
