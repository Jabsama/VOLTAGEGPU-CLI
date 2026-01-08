<p align="center">
  <img src="https://voltagegpu.com/logo-voltage.png" alt="VoltageGPU Logo" width="200"/>
</p>

<h1 align="center">⚡ VoltageGPU CLI</h1>

<p align="center">
  <strong>The fastest way to deploy and manage GPU pods for AI/ML workloads</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/voltagegpu-cli/"><img src="https://img.shields.io/pypi/v/voltagegpu-cli?color=blue&label=PyPI" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/voltagegpu-cli/"><img src="https://img.shields.io/pypi/pyversions/voltagegpu-cli" alt="Python Versions"></a>
  <a href="https://github.com/Jabsama/VOLTAGEGPU-CLI/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="https://voltagegpu.com"><img src="https://img.shields.io/badge/website-voltagegpu.com-orange" alt="Website"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-python-sdk">Python SDK</a> •
  <a href="#-documentation">Documentation</a>
</p>

---

## 🎯 What is VoltageGPU?

**VoltageGPU** is a GPU cloud platform offering affordable access to high-performance GPUs for AI/ML training, inference, and development. Deploy pods with **NVIDIA RTX 4090**, **A100**, and **H100** GPUs in seconds.

### Why VoltageGPU?

| Feature | VoltageGPU | AWS | GCP |
|---------|------------|-----|-----|
| **RTX 4090** | $0.35/hr | N/A | N/A |
| **A100 80GB** | $1.89/hr | $4.10/hr | $3.67/hr |
| **H100** | $2.85/hr | $5.12/hr | $4.50/hr |
| **Setup Time** | < 60 seconds | 5-10 minutes | 5-10 minutes |
| **No Commitment** | ✅ Pay-as-you-go | ❌ Reserved | ❌ Reserved |

---

## 🚀 Quick Start

```bash
# Install the CLI
pip install voltagegpu-cli

# Configure your API key
export VOLT_API_KEY="your_api_key_here"

# List available templates
volt templates list

# Create a GPU pod
volt pods create --template pytorch-cuda12 --name my-training-pod

# SSH into your pod
volt pods ssh <pod_id>
```

**Get your API key at [voltagegpu.com/dashboard](https://voltagegpu.com/dashboard)**

---

## ✨ Features

### 🖥️ **Pod Management**
- Create, start, stop, and delete GPU pods
- Real-time status monitoring
- SSH access with one command

### 📦 **Pre-built Templates**
- PyTorch, TensorFlow, JAX environments
- vLLM for LLM inference
- Stable Diffusion for image generation
- Custom Docker images support

### 🔑 **SSH Key Management**
- Add and manage SSH keys
- Secure access to your pods

### 💰 **Cost Tracking**
- Real-time balance monitoring
- Per-pod cost breakdown
- Usage history

### 🐍 **Python SDK**
- Full programmatic access
- Async support
- Type hints included

---

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install voltagegpu-cli
```

### From Source

```bash
git clone https://github.com/Jabsama/VOLTAGEGPU-CLI.git
cd VOLTAGEGPU-CLI
pip install -e .
```

### Requirements

- Python 3.8+
- pip

---

## ⚙️ Configuration

### Option 1: Environment Variable (Recommended)

```bash
export VOLT_API_KEY="your_api_key_here"
```

### Option 2: Configuration File

Create `~/.volt/config.ini`:

```ini
[api]
api_key = your_api_key_here
```

### Option 3: Pass Directly

```python
from volt import VoltageGPUClient

client = VoltageGPUClient(api_key="your_api_key_here")
```

---

## 📖 Usage

### Pods

```bash
# List all your pods
volt pods list

# Get pod details
volt pods get <pod_id>

# Create a new pod
volt pods create --template <template_id> --name <name> [--gpu-count 1]

# Start a stopped pod
volt pods start <pod_id>

# Stop a running pod
volt pods stop <pod_id>

# Delete a pod
volt pods delete <pod_id> --yes

# Get SSH command for a pod
volt pods ssh <pod_id>
```

### Templates

```bash
# List all available templates
volt templates list

# Filter by category
volt templates list --category llm

# Get template details
volt templates get <template_id>
```

### SSH Keys

```bash
# List your SSH keys
volt ssh-keys list

# Add a new SSH key from file
volt ssh-keys add --name "my-laptop" --file ~/.ssh/id_ed25519.pub

# Add a new SSH key directly
volt ssh-keys add --name "my-key" --key "ssh-ed25519 AAAA..."

# Delete an SSH key
volt ssh-keys delete <key_id>
```

### Machines

```bash
# List available machines
volt machines list

# Filter by GPU type
volt machines list --gpu RTX4090
volt machines list --gpu A100
volt machines list --gpu H100
```

### Account

```bash
# Check your balance
volt account balance

# Get account information
volt account info
```

### JSON Output

All list commands support `--json` for machine-readable output:

```bash
volt pods list --json | jq '.[] | select(.status == "running")'
```

---

## 🐍 Python SDK

### Basic Usage

```python
from volt import VoltageGPUClient

# Initialize client
client = VoltageGPUClient()

# List pods
pods = client.list_pods()
for pod in pods:
    print(f"{pod.name}: {pod.status} ({pod.gpu_type})")

# Create a pod
pod = client.create_pod(
    template_id="pytorch-cuda12",
    name="my-training-pod",
    gpu_count=2
)
print(f"Created pod: {pod.id}")

# Get SSH info
print(f"SSH: ssh -p {pod.ssh_port} root@{pod.ssh_host}")

# Stop and delete
client.stop_pod(pod.id)
client.delete_pod(pod.id)
```

### Context Manager

```python
from volt import VoltageGPUClient

with VoltageGPUClient() as client:
    templates = client.list_templates()
    for t in templates:
        print(f"{t.name}: ${t.hourly_price}/hr")
```

### Available Methods

| Method | Description |
|--------|-------------|
| `list_pods()` | List all your pods |
| `get_pod(pod_id)` | Get pod details |
| `create_pod(template_id, name, gpu_count)` | Create a new pod |
| `start_pod(pod_id)` | Start a stopped pod |
| `stop_pod(pod_id)` | Stop a running pod |
| `delete_pod(pod_id)` | Delete a pod |
| `list_templates(category)` | List available templates |
| `get_template(template_id)` | Get template details |
| `list_ssh_keys()` | List your SSH keys |
| `add_ssh_key(name, public_key)` | Add a new SSH key |
| `delete_ssh_key(key_id)` | Delete an SSH key |
| `list_machines(gpu_type)` | List available machines |
| `get_balance()` | Get account balance |
| `get_account_info()` | Get account information |

---

## 🎓 Examples

### Launch a Training Job

```bash
# Find a suitable template
volt templates list --category ml

# Create pod with SSH key
volt pods create \
  --template pytorch-cuda12 \
  --name training-job \
  --gpu-count 4 \
  --ssh-key my-key-id

# Get SSH command
volt pods ssh <pod_id>
```

### Deploy vLLM for Inference

```bash
# Create vLLM pod
volt pods create \
  --template vllm-inference \
  --name llm-server \
  --gpu-count 1

# Access the API
curl http://<pod_ip>:8000/v1/models
```

### Batch Operations

```bash
# Stop all running pods
volt pods list --json | jq -r '.[] | select(.status == "running") | .id' | xargs -I {} volt pods stop {}

# Delete all stopped pods
volt pods list --json | jq -r '.[] | select(.status == "stopped") | .id' | xargs -I {} volt pods delete {} --yes
```

---

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VOLT_API_KEY` | Your VoltageGPU API key | - |
| `VOLT_BASE_URL` | API base URL | `https://voltagegpu.com/api` |

---

## 📚 Documentation

- **Website**: [voltagegpu.com](https://voltagegpu.com)
- **API Reference**: [docs.voltagegpu.com](https://docs.voltagegpu.com)
- **Pricing**: [voltagegpu.com/pricing](https://voltagegpu.com/pricing)
- **Templates**: [voltagegpu.com/templates](https://voltagegpu.com/templates)

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Clone the repository
git clone https://github.com/Jabsama/VOLTAGEGPU-CLI.git
cd VOLTAGEGPU-CLI

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Website**: [voltagegpu.com](https://voltagegpu.com)
- **GitHub**: [github.com/Jabsama/VOLTAGEGPU-CLI](https://github.com/Jabsama/VOLTAGEGPU-CLI)
- **PyPI**: [pypi.org/project/voltagegpu-cli](https://pypi.org/project/voltagegpu-cli)
- **Twitter**: [@VoltageGPU](https://twitter.com/VoltageGPU)
- **Discord**: [discord.gg/voltagegpu](https://discord.gg/voltagegpu)

---

<p align="center">
  <strong>⚡ Power your AI with VoltageGPU ⚡</strong>
</p>

<p align="center">
  Made with ❤️ by the VoltageGPU Team
</p>
