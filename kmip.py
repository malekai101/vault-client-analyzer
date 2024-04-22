from vault_api import *


# The KMIP reporter class gathers information about KMIP mounts on the instance
class KMIPReporter:
    """
    KMIP Reporter class builds a report from KMIP data.  It is tied to a Vault instance by the
    VaultAPIHelper attached to the instance and built in the constructor.
    """

    def __init__(self, addr, token):
        self.vault_client = VaultAPIHelper(addr, token)

    def process_roles(
        self, scope_name: str, role_name: str, mount_path: str, namespace: str
    ) -> dict:
        """
        Processes the credentials in the KMIP role
        :param scope_name: The scope to which the role belongs
        :param role_name: The name of the role to process
        :param mount_path: The mount path of the KMIP mount
        :param namespace: The namespace of the KMIP mount
        :return: A dict containing the credentials in the role
        """
        role_dict = dict()
        role_dict["name"] = role_name

        credentials = self.vault_client.list_kmip_credentials(
            mount_path=mount_path, scope=scope_name, role=role_name, namespace=namespace
        )
        role_dict["credentials"] = credentials
        role_dict["certificates"] = len(credentials)

        return role_dict

    def process_scopes(self, scope_name: str, mount_path: str, namespace: str) -> dict:
        """
        Processes the roles in the KMIP scope
        :param scope_name: The name of the scope
        :param mount_path: The mount path of the KMIP mount
        :param namespace: The namespace of the KMIP mount
        :return: A dict of roles and their credentials in the scope
        """
        scope_dict = dict()
        scope_cert_count = 0

        scope_dict["name"] = scope_name
        scope_dict["roles"] = dict()
        roles = self.vault_client.list_kmip_roles(
            mount_path=mount_path, scope=scope_name, namespace=namespace
        )
        for role in roles:
            scope_dict["roles"][role] = self.process_roles(
                scope_name=scope_name,
                role_name=role,
                mount_path=mount_path,
                namespace=namespace,
            )
        scope_dict["role_count"] = len(roles)
        for role in scope_dict["roles"].values():
            scope_cert_count += role.get("certificates", 0)
        scope_dict["certificates"] = scope_cert_count
        return scope_dict

    def process_mounts(self, kmip_mounts: list, namespace: str) -> dict:
        """
        Processes the scopes in the KMIP mount
        :param kmip_mounts: A list of KMIP mounts
        :param namespace: The namespace of the KMIP mounts
        :return: A dict of KMIP mounts and their metadata
        """
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
                    namespace=namespace,
                )
            # pull summary data for the mount
            mount_dict[mount_entry["path"]]["scope_count"] = len(scopes)
            for scope in mount_dict[mount_entry["path"]]["scopes"].values():
                mount_certificates += scope.get("certificates", 0)
            mount_dict[mount_entry["path"]]["certificates"] = mount_certificates
        return mount_dict

    def build_kmip_report(self) -> dict:
        """
        Builds the KMIP report for Vault cluster attached the the instance
        :return: A dict report containing the KMIP metadata for the cluster
        """
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

        # build the totals
        for namespace in kmip_report["namespaces"].values():
            kmip_report["total_kmip_mounts"] += len(namespace["mounts"])
            for mount in namespace["mounts"].values():
                kmip_report["total_kmip_scopes"] += len(mount["scopes"])
                kmip_report["total_kmip_client_count"] += mount.get("certificates", 0)
                for scope in mount["scopes"].values():
                    kmip_report["total_kmip_roles"] += len(scope["roles"])

        return kmip_report
