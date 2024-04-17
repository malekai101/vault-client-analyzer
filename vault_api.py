import json
import requests
from requests.exceptions import HTTPError
from dataclasses import dataclass


class VaultAPIHelper:
    def __init__(self, addr, token):
        self.addr = f"{addr}/v1"
        self.token = token

    def build_header(self, namespace="") -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-VAULT-NAMESPACE": namespace,
            "X-VAULT-TOKEN": self.token,
        }

    def get_namespaces(self, namespace="") -> list:
        endpoint = f"{self.addr}/sys/namespaces"
        headers = self.build_header(namespace)
        resp = requests.request("LIST", endpoint, headers=headers)
        try:
            resp.raise_for_status()
            return [
                {"path": i.get("path"), "id": i.get("id")}
                for i in resp.json()["data"]["key_info"].values()
            ]
        except HTTPError as exp:
            if exp.response.status_code == 404:
                # 404 is not child namespaces
                return []
            else:
                raise exp
        except Exception:
            raise

    def has_child_namespaces(self, namespace="") -> bool:
        endpoint = f"{self.addr}/sys/namespaces"
        headers = self.build_header(namespace)
        resp = requests.request("LIST", endpoint, headers=headers)
        try:
            resp.raise_for_status()
        except HTTPError as exp:
            if exp.response.status_code == 404:
                # 404 is no child namespaces
                return False
            else:
                raise exp
        except Exception:
            raise

        return True

    def get_child_namespaces(self) -> dict:
        return self._get_child_namespaces()

    def _get_child_namespaces(self, namespace="", **kwargs) -> dict:
        if "nslist" in kwargs.keys():
            nslist = kwargs.get("nslist")  # type: dict
            nslist[kwargs.get("id")] = namespace
        else:
            nslist = {"root": namespace}

        if self.has_child_namespaces(namespace=namespace):
            children = self.get_namespaces(namespace=namespace)
            for ns in children:
                nslist = self._get_child_namespaces(
                    ns.get("path"), nslist=nslist, id=ns.get("id")
                )
        else:
            return nslist
        return nslist

    def get_client_detail_over_time(self, start: int, end: int) -> list:
        endpoint = f"{self.addr}/sys/internal/counters/activity/export?start_time={start}&end_time={end}"
        headers = self.build_header()
        try:
            resp = requests.request("GET", endpoint, headers=headers)
            resp.raise_for_status()
            json_list = [json.loads(x) for x in resp.text.split("\n") if x != ""]
            return json_list
        except:
            raise

    def lookup_entity_from_id(self, namespace: str, entity_id: str) -> dict:
        endpoint = f"{self.addr}/identity/lookup/entity"
        headers = self.build_header(namespace=namespace)
        try:
            data = {"id": entity_id}
            resp = requests.request("POST", endpoint, headers=headers, json=data)
            resp.raise_for_status()
        except Exception:
            raise

    def get_secret_mounts(self, namespace="") -> list:
        endpoint = f"{self.addr}/sys/mounts"
        headers = self.build_header(namespace=namespace)
        try:
            resp = requests.request("GET", endpoint, headers=headers)
            resp.raise_for_status()
            return [
                {"path": k, "accessor": v.get("accessor"), "type": v.get("type")}
                for k, v in resp.json().get("data").items()
            ]
        except Exception:
            raise

    def get_secret_mounts_by_type(self, mount_type: str, namespace="") -> list:
        try:
            return [
                x
                for x in self.get_secret_mounts(namespace=namespace)
                if str.upper(x["type"]) == mount_type.upper()
            ]
        except Exception:
            raise

    def list_kmip_scopes(self, mount_path: str, namespace="") -> list:
        endpoint = f"{self.addr}/{mount_path}scope"
        headers = self.build_header(namespace=namespace)
        try:
            resp = requests.request("LIST", endpoint, headers=headers)
            resp.raise_for_status()
            return [v for v in resp.json().get("data").get("keys")]
        except HTTPError as httpexp:
            if httpexp.response.status_code == 404:
                return []
        except Exception:
            raise

    def list_kmip_roles(self, mount_path: str, scope: str, namespace="") -> list:
        endpoint = f"{self.addr}/{mount_path}scope/{scope}/role"
        headers = self.build_header(namespace=namespace)
        try:
            resp = requests.request("LIST", endpoint, headers=headers)
            resp.raise_for_status()
            return [v for v in resp.json().get("data").get("keys")]
        except HTTPError as httpexp:
            if httpexp.response.status_code == 404:
                return []
        except Exception:
            raise

    def list_kmip_credentials(
        self, mount_path: str, scope: str, role: str, namespace=""
    ) -> list:
        endpoint = f"{self.addr}/{mount_path}scope/{scope}/role/{role}/credential"
        headers = self.build_header(namespace=namespace)
        try:
            resp = requests.request("LIST", endpoint, headers=headers)
            resp.raise_for_status()
            return [v for v in resp.json().get("data").get("keys")]
        except HTTPError as httpexp:
            if httpexp.response.status_code == 404:
                return []
        except Exception:
            raise
