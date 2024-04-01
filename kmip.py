from vault_api import *


class KMIP_Reporter:
    def __init__(self, addr, token):
        self.vault_client = VaultAPIHelper(addr, token)

    def build_kmip_report(self) -> dict:
        kmip_report = dict()
        kmip_report['test'] = "done"

        # build namespace list
        #namespaces = self.vault_client.get_namespaces()

        # loop through
        # build summary
        # return the report
        return kmip_report

    def examine_namespace(self, namespace: str):
        pass