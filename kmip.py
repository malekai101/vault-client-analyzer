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
                # loop through
                for mount in kmip_mounts:
                    scopes = self.vault_client.list_kmip_scopes(
                        mount["path"], namespace
                    )
                    mount["scopes"] = scopes
                # build summary
                # return the report
                kmip_report[namespace] = kmip_mounts
        return kmip_report

    def examine_namespace(self, namespace: str):
        pass
