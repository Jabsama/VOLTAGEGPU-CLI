"""VoltageGPU SDK Client - Main API client for VoltageGPU."""

import httpx
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .config import Config


@dataclass
class Pod:
    """Represents a GPU pod."""
    id: str
    name: str
    status: str
    gpu_type: str
    gpu_count: int
    hourly_price: float
    ssh_host: Optional[str] = None
    ssh_port: Optional[int] = None
    template_id: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class Template:
    """Represents a pod template."""
    id: str
    name: str
    description: str
    docker_image: str
    gpu_type: str
    min_gpu: int
    max_gpu: int
    hourly_price: float
    category: Optional[str] = None


@dataclass
class SSHKey:
    """Represents an SSH key."""
    id: str
    name: str
    public_key: str
    fingerprint: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class Machine:
    """Represents an available machine."""
    id: str
    gpu_type: str
    gpu_count: int
    cpu_cores: int
    ram_gb: int
    storage_gb: int
    hourly_price: float
    available: bool
    location: Optional[str] = None


class VoltageGPUClient:
    """Main client for interacting with VoltageGPU API."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the client with optional config."""
        self.config = config or Config.load()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "VoltageGPU-CLI/0.1.0"
            },
            timeout=30.0
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    # ==================== PODS ====================

    def list_pods(self) -> List[Pod]:
        """List all pods for the current user."""
        response = self._client.get("/volt/pods")
        response.raise_for_status()
        data = response.json()
        return [self._parse_pod(p) for p in data.get("pods", data)]

    def get_pod(self, pod_id: str) -> Pod:
        """Get details of a specific pod."""
        response = self._client.get(f"/volt/pods/{pod_id}")
        response.raise_for_status()
        return self._parse_pod(response.json())

    def create_pod(
        self,
        template_id: str,
        name: str,
        gpu_count: int = 1,
        ssh_key_ids: Optional[List[str]] = None,
        docker_credentials_id: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Pod:
        """Create a new pod from a template."""
        payload = {
            "templateId": template_id,
            "name": name,
            "gpuCount": gpu_count,
        }
        if ssh_key_ids:
            payload["sshKeyIds"] = ssh_key_ids
        if docker_credentials_id:
            payload["dockerCredentialsId"] = docker_credentials_id
        if env_vars:
            payload["envVars"] = env_vars

        response = self._client.post("/volt/pods", json=payload)
        response.raise_for_status()
        return self._parse_pod(response.json())

    def start_pod(self, pod_id: str) -> Pod:
        """Start a stopped pod."""
        response = self._client.post(f"/volt/pods/{pod_id}/start")
        response.raise_for_status()
        return self._parse_pod(response.json())

    def stop_pod(self, pod_id: str) -> Pod:
        """Stop a running pod."""
        response = self._client.post(f"/volt/pods/{pod_id}/stop")
        response.raise_for_status()
        return self._parse_pod(response.json())

    def delete_pod(self, pod_id: str) -> bool:
        """Delete a pod."""
        response = self._client.delete(f"/volt/pods/{pod_id}")
        response.raise_for_status()
        return True

    def _parse_pod(self, data: Dict[str, Any]) -> Pod:
        """Parse pod data from API response."""
        return Pod(
            id=data.get("id", data.get("podId", "")),
            name=data.get("name", ""),
            status=data.get("status", "unknown"),
            gpu_type=data.get("gpuType", data.get("gpu_type", "")),
            gpu_count=data.get("gpuCount", data.get("gpu_count", 1)),
            hourly_price=float(data.get("hourlyPrice", data.get("hourly_price", 0))),
            ssh_host=data.get("sshHost", data.get("ssh_host")),
            ssh_port=data.get("sshPort", data.get("ssh_port")),
            template_id=data.get("templateId", data.get("template_id")),
            created_at=data.get("createdAt", data.get("created_at"))
        )

    # ==================== TEMPLATES ====================

    def list_templates(self, category: Optional[str] = None) -> List[Template]:
        """List available templates."""
        params = {}
        if category:
            params["category"] = category
        response = self._client.get("/volt/templates", params=params)
        response.raise_for_status()
        data = response.json()
        return [self._parse_template(t) for t in data.get("templates", data)]

    def get_template(self, template_id: str) -> Template:
        """Get details of a specific template."""
        response = self._client.get(f"/volt/templates/{template_id}")
        response.raise_for_status()
        return self._parse_template(response.json())

    def _parse_template(self, data: Dict[str, Any]) -> Template:
        """Parse template data from API response."""
        return Template(
            id=data.get("id", data.get("templateId", "")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            docker_image=data.get("dockerImage", data.get("docker_image", "")),
            gpu_type=data.get("gpuType", data.get("gpu_type", "")),
            min_gpu=data.get("minGpu", data.get("min_gpu", 1)),
            max_gpu=data.get("maxGpu", data.get("max_gpu", 8)),
            hourly_price=float(data.get("hourlyPrice", data.get("hourly_price", 0))),
            category=data.get("category")
        )

    # ==================== SSH KEYS ====================

    def list_ssh_keys(self) -> List[SSHKey]:
        """List all SSH keys for the current user."""
        response = self._client.get("/volt/ssh-keys")
        response.raise_for_status()
        data = response.json()
        return [self._parse_ssh_key(k) for k in data.get("sshKeys", data.get("keys", data))]

    def add_ssh_key(self, name: str, public_key: str) -> SSHKey:
        """Add a new SSH key."""
        response = self._client.post("/volt/ssh-keys", json={
            "name": name,
            "publicKey": public_key
        })
        response.raise_for_status()
        return self._parse_ssh_key(response.json())

    def delete_ssh_key(self, key_id: str) -> bool:
        """Delete an SSH key."""
        response = self._client.delete(f"/volt/ssh-keys/{key_id}")
        response.raise_for_status()
        return True

    def _parse_ssh_key(self, data: Dict[str, Any]) -> SSHKey:
        """Parse SSH key data from API response."""
        return SSHKey(
            id=data.get("id", data.get("keyId", "")),
            name=data.get("name", ""),
            public_key=data.get("publicKey", data.get("public_key", "")),
            fingerprint=data.get("fingerprint"),
            created_at=data.get("createdAt", data.get("created_at"))
        )

    # ==================== MACHINES ====================

    def list_machines(self, gpu_type: Optional[str] = None) -> List[Machine]:
        """List available machines."""
        params = {}
        if gpu_type:
            params["gpuType"] = gpu_type
        response = self._client.get("/volt/machines", params=params)
        response.raise_for_status()
        data = response.json()
        return [self._parse_machine(m) for m in data.get("machines", data)]

    def _parse_machine(self, data: Dict[str, Any]) -> Machine:
        """Parse machine data from API response."""
        return Machine(
            id=data.get("id", data.get("machineId", "")),
            gpu_type=data.get("gpuType", data.get("gpu_type", "")),
            gpu_count=data.get("gpuCount", data.get("gpu_count", 1)),
            cpu_cores=data.get("cpuCores", data.get("cpu_cores", 0)),
            ram_gb=data.get("ramGb", data.get("ram_gb", 0)),
            storage_gb=data.get("storageGb", data.get("storage_gb", 0)),
            hourly_price=float(data.get("hourlyPrice", data.get("hourly_price", 0))),
            available=data.get("available", True),
            location=data.get("location")
        )

    # ==================== ACCOUNT ====================

    def get_balance(self) -> float:
        """Get current account balance."""
        response = self._client.get("/user/balance")
        response.raise_for_status()
        data = response.json()
        return float(data.get("balance", 0))

    def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        response = self._client.get("/account")
        response.raise_for_status()
        return response.json()


__all__ = ["VoltageGPUClient", "Pod", "Template", "SSHKey", "Machine"]
