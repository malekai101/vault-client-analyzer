from vault_api import *


class KMIP_Reporter:
    def __init__(self, addr, token):
        self.vault_client = VaultAPIHelper(addr, token)

    def build_kmip_report(self) -> dict:
        kmip_report = dict()
        kmip_report_namespaces = dict()
        total_client_count = 0
        total_kmip_mounts = 0
        total_kmip_scopes = 0
        total_kmip_roles = 0

        # build namespace list and get kmip namespaces
        namespaces = self.vault_client.get_child_namespaces()
        for namespace in namespaces.values():
            kmip_mounts = self.vault_client.get_secret_mounts_by_type("kmip", namespace)
            if len(kmip_mounts) > 0:
                # loop through
                total_kmip_mounts += len(kmip_mounts)
                for mount in kmip_mounts:
                    mount_count = 0
                    scopes = self.vault_client.list_kmip_scopes(
                        mount["path"], namespace
                    )
                    mount["scopes"] = scopes
                    # find the roles and clients in each scope.
                    total_kmip_scopes += len(scopes)
                    for scope in scopes:
                        roles = self.vault_client.list_kmip_roles(
                            mount["path"], scope, namespace
                        )
                        total_kmip_roles += len(roles)
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
                kmip_report_namespaces[namespace] = kmip_mounts
        kmip_report["namespaces"] = kmip_report_namespaces
        kmip_report["total_kmip_client_count"] = total_client_count
        kmip_report["total_kmip_mounts"] = total_kmip_mounts
        kmip_report["total_kmip_scopes"] = total_kmip_scopes
        kmip_report["total_kmip_roles"] = total_kmip_roles
        return kmip_report

    def examine_namespace(self, namespace: str):
        pass
