from vault_api import *


class KMIP_Reporter:
    def __init__(self, addr, token):
        self.vault_client = VaultAPIHelper(addr, token)

    def build_kmip_report(self) -> dict:
        kmip_report = dict()
        total_client_count = 0

        # build namespace list and get kmip namespaces
        namespaces = self.vault_client.get_child_namespaces()
        for namespace in namespaces.values():
            kmip_mounts = self.vault_client.get_secret_mounts_by_type("kmip", namespace)
            if len(kmip_mounts) > 0:
                kmip_report[namespace] = kmip_mounts
                # loop through
                # build summary
                # return the report
        return kmip_report

    def examine_namespace(self, namespace: str):
        pass
