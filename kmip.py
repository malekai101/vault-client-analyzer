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
                    mount_count = 0
                    scopes = self.vault_client.list_kmip_scopes(
                        mount["path"], namespace
                    )
                    mount["scopes"] = scopes
                    # find the roles and clients in each scope.
                    for scope in scopes:
                        roles = self.vault_client.list_kmip_roles(
                            mount["path"], scope, namespace
                        )
                        for role in roles:
                            certs = self.vault_client.list_kmip_credentials(
                                mount["path"], scope, role, namespace
                            )
                            clients = len(certs)
                            mount_count += clients
                    mount["clients"] = mount_count
                    total_client_count += mount_count
                # build summary
                # return the report
                kmip_report[namespace] = kmip_mounts
        kmip_report["total_client_count"] = total_client_count
        return kmip_report

    def examine_namespace(self, namespace: str):
        pass
