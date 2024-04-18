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
            kmip_mounts_list = self.vault_client.get_secret_mounts_by_type(
                "kmip", namespace
            )
            kmip_mounts = dict()
            for mount_entry in kmip_mounts_list:
                kmip_mounts[mount_entry["path"]] = mount_entry
            if len(kmip_mounts) > 0:
                # loop through
                total_kmip_mounts += len(kmip_mounts)
                for mount in kmip_mounts.values():
                    mount_count = 0
                    scopes = self.vault_client.list_kmip_scopes(
                        mount["path"], namespace
                    )
                    mount["scopes"] = dict()
                    # find the roles and clients in each scope.
                    total_kmip_scopes += len(scopes)
                    for scope in scopes:
                        mount["scopes"][scope] = dict()
                        mount["scopes"][scope]["name"] = scope
                        mount["scopes"][scope]["roles"] = dict()
                        roles = self.vault_client.list_kmip_roles(
                            mount["path"], scope, namespace
                        )
                        total_kmip_roles += len(roles)
                        for role in roles:
                            mount["scopes"][scope]["roles"][role] = dict()
                            mount["scopes"][scope]["roles"][role]["name"] = role
                            mount["scopes"][scope]["roles"][role][
                                "certificates"
                            ] = list()
                            certs = self.vault_client.list_kmip_credentials(
                                mount["path"], scope, role, namespace
                            )
                            mount["scopes"][scope]["roles"][role][
                                "certificates"
                            ] = certs
                            clients = len(certs)
                            mount["scopes"][scope]["roles"][role][
                                "certificate_count"
                            ] = clients
                            mount_count += clients

                    mount["total_mount_certificates"] = mount_count
                    total_client_count += mount_count
                # build summary
                # return the report
                kmip_report_namespaces[namespace] = kmip_mounts
                # kmip_report_namespaces[namespace]["path"] = namespace
                # kmip_report_namespaces[namespace]["mounts"] = dict()
                # kmip_report_namespaces[namespace]["mounts"] = kmip_mounts
        kmip_report["namespaces"] = kmip_report_namespaces
        kmip_report["total_kmip_client_count"] = total_client_count
        kmip_report["total_kmip_mounts"] = total_kmip_mounts
        kmip_report["total_kmip_scopes"] = total_kmip_scopes
        kmip_report["total_kmip_roles"] = total_kmip_roles
        return kmip_report

    def examine_namespace(self, namespace: str):
        pass

    def process_roles(self) -> dict:
        pass

    def process_scopes(self, scope_name: str, mount_path: str, namesspace: str) -> dict:
        return {"certificates": 3}

    def process_mounts(self, kmip_mounts: list, namespace: str) -> dict:
        mount_dict = dict()
        mount_count = 0

        for mount_entry in kmip_mounts:
            mount_certificates = 0
            mount_dict[mount_entry["path"]] = mount_entry
            mount_count += 1
            # process the scopes
            mount_dict[mount_entry["path"]]["scopes"] = dict()
            scopes = self.vault_client.list_kmip_scopes(mount_entry["path"], namespace)
            for scope in scopes:
                mount_dict[mount_entry["path"]]["scopes"][scope] = self.process_scopes(
                    scope_name=scope,
                    mount_path=mount_entry["path"],
                    namesspace=namespace,
                )
            # pull summary data for the mount
            mount_dict[mount_entry["path"]]["scope_count"] = len(scopes)
            for scope in mount_dict[mount_entry["path"]]["scopes"].values():
                mount_certificates += scope.get("certificates", 0)
            mount_dict[mount_entry["path"]]["certificates"] = mount_certificates
        return mount_dict

    def build_kmip_report_new(self) -> dict:
        kmip_report = dict()
        kmip_report["namespaces"] = dict()
        kmip_report["total_kmip_client_count"] = 0
        kmip_report["total_kmip_mounts"] = 0
        kmip_report["total_kmip_scopes"] = 0
        kmip_report["total_kmip_roles"] = 0

        # Pull all of the namespaces on the cluster
        namespaces = self.vault_client.get_child_namespaces()
        # Get all of the kmip mounts in all of the namespaces
        kmip_mounts_list = dict()
        kmip_report["namespaces"] = dict()
        for namespace in namespaces.values():
            kmip_mounts_list = self.vault_client.get_secret_mounts_by_type(
                "kmip", namespace
            )
            if len(kmip_mounts_list) > 0:
                kmip_report["namespaces"][namespace] = dict()
                kmip_report["namespaces"][namespace]["mounts"] = self.process_mounts(
                    kmip_mounts_list, namespace
                )

        return kmip_report
