"""VoltageGPU CLI - Main entry point."""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from volt.sdk import VoltageGPUClient, Config

console = Console()


def get_client() -> VoltageGPUClient:
    """Get configured VoltageGPU client."""
    try:
        return VoltageGPUClient()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\n[yellow]To configure your API key:[/yellow]")
        console.print("  1. Set VOLT_API_KEY environment variable")
        console.print("  2. Or create ~/.volt/config.ini with:")
        console.print("     [api]")
        console.print("     api_key = your_api_key_here")
        sys.exit(1)


@click.group()
@click.version_option(version="0.1.0", prog_name="volt")
def cli():
    """VoltageGPU CLI - Manage GPU pods from the command line.
    
    VoltageGPU provides affordable GPU cloud computing for AI/ML workloads.
    """
    pass


# ==================== PODS COMMANDS ====================

@cli.group()
def pods():
    """Manage GPU pods."""
    pass


@pods.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def pods_list(as_json: bool):
    """List all your pods."""
    with get_client() as client:
        pods = client.list_pods()
        
        if as_json:
            import json
            data = [{"id": p.id, "name": p.name, "status": p.status, 
                    "gpu_type": p.gpu_type, "gpu_count": p.gpu_count,
                    "hourly_price": p.hourly_price} for p in pods]
            click.echo(json.dumps(data, indent=2))
            return
        
        if not pods:
            console.print("[yellow]No pods found.[/yellow]")
            console.print("Create one with: volt pods create --template <template_id> --name <name>")
            return
        
        table = Table(title="Your Pods")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="bold")
        table.add_column("GPU", style="magenta")
        table.add_column("Count")
        table.add_column("$/hr", style="yellow")
        
        for pod in pods:
            status_color = {
                "running": "green",
                "stopped": "red",
                "starting": "yellow",
                "stopping": "yellow"
            }.get(pod.status.lower(), "white")
            
            table.add_row(
                pod.id[:12] + "...",
                pod.name,
                f"[{status_color}]{pod.status}[/{status_color}]",
                pod.gpu_type,
                str(pod.gpu_count),
                f"${pod.hourly_price:.2f}"
            )
        
        console.print(table)


@pods.command("get")
@click.argument("pod_id")
def pods_get(pod_id: str):
    """Get details of a specific pod."""
    with get_client() as client:
        try:
            pod = client.get_pod(pod_id)
            
            panel = Panel(
                f"""[cyan]ID:[/cyan] {pod.id}
[cyan]Name:[/cyan] {pod.name}
[cyan]Status:[/cyan] {pod.status}
[cyan]GPU Type:[/cyan] {pod.gpu_type}
[cyan]GPU Count:[/cyan] {pod.gpu_count}
[cyan]Hourly Price:[/cyan] ${pod.hourly_price:.2f}
[cyan]SSH Host:[/cyan] {pod.ssh_host or 'N/A'}
[cyan]SSH Port:[/cyan] {pod.ssh_port or 'N/A'}
[cyan]Created:[/cyan] {pod.created_at or 'N/A'}""",
                title=f"Pod: {pod.name}",
                border_style="green"
            )
            console.print(panel)
            
            if pod.ssh_host and pod.ssh_port:
                console.print(f"\n[yellow]SSH Command:[/yellow] ssh -p {pod.ssh_port} root@{pod.ssh_host}")
                
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@pods.command("create")
@click.option("--template", "-t", required=True, help="Template ID to use")
@click.option("--name", "-n", required=True, help="Name for the pod")
@click.option("--gpu-count", "-g", default=1, help="Number of GPUs (default: 1)")
@click.option("--ssh-key", "-k", multiple=True, help="SSH key ID(s) to add")
def pods_create(template: str, name: str, gpu_count: int, ssh_key: tuple):
    """Create a new pod from a template."""
    with get_client() as client:
        try:
            console.print(f"[yellow]Creating pod '{name}'...[/yellow]")
            
            ssh_key_ids = list(ssh_key) if ssh_key else None
            pod = client.create_pod(
                template_id=template,
                name=name,
                gpu_count=gpu_count,
                ssh_key_ids=ssh_key_ids
            )
            
            console.print(f"[green]✓ Pod created successfully![/green]")
            console.print(f"  ID: {pod.id}")
            console.print(f"  Status: {pod.status}")
            
            if pod.ssh_host and pod.ssh_port:
                console.print(f"\n[yellow]SSH Command:[/yellow] ssh -p {pod.ssh_port} root@{pod.ssh_host}")
                
        except Exception as e:
            console.print(f"[red]Error creating pod:[/red] {e}")
            sys.exit(1)


@pods.command("start")
@click.argument("pod_id")
def pods_start(pod_id: str):
    """Start a stopped pod."""
    with get_client() as client:
        try:
            console.print(f"[yellow]Starting pod {pod_id}...[/yellow]")
            pod = client.start_pod(pod_id)
            console.print(f"[green]✓ Pod started![/green] Status: {pod.status}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@pods.command("stop")
@click.argument("pod_id")
def pods_stop(pod_id: str):
    """Stop a running pod."""
    with get_client() as client:
        try:
            console.print(f"[yellow]Stopping pod {pod_id}...[/yellow]")
            pod = client.stop_pod(pod_id)
            console.print(f"[green]✓ Pod stopped![/green] Status: {pod.status}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@pods.command("delete")
@click.argument("pod_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def pods_delete(pod_id: str, yes: bool):
    """Delete a pod."""
    if not yes:
        if not click.confirm(f"Are you sure you want to delete pod {pod_id}?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    with get_client() as client:
        try:
            console.print(f"[yellow]Deleting pod {pod_id}...[/yellow]")
            client.delete_pod(pod_id)
            console.print(f"[green]✓ Pod deleted![/green]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@pods.command("ssh")
@click.argument("pod_id")
def pods_ssh(pod_id: str):
    """SSH into a pod (prints the command)."""
    with get_client() as client:
        try:
            pod = client.get_pod(pod_id)
            
            if not pod.ssh_host or not pod.ssh_port:
                console.print("[red]Error:[/red] SSH not available for this pod")
                sys.exit(1)
            
            ssh_cmd = f"ssh -p {pod.ssh_port} root@{pod.ssh_host}"
            console.print(f"[green]SSH Command:[/green] {ssh_cmd}")
            console.print("\n[yellow]Tip:[/yellow] Copy and paste this command to connect")
            
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


# ==================== TEMPLATES COMMANDS ====================

@cli.group()
def templates():
    """Browse available templates."""
    pass


@templates.command("list")
@click.option("--category", "-c", help="Filter by category")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def templates_list(category: str, as_json: bool):
    """List available templates."""
    with get_client() as client:
        templates = client.list_templates(category=category)
        
        if as_json:
            import json
            data = [{"id": t.id, "name": t.name, "gpu_type": t.gpu_type,
                    "hourly_price": t.hourly_price, "category": t.category} for t in templates]
            click.echo(json.dumps(data, indent=2))
            return
        
        if not templates:
            console.print("[yellow]No templates found.[/yellow]")
            return
        
        table = Table(title="Available Templates")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("GPU", style="magenta")
        table.add_column("GPUs", justify="center")
        table.add_column("$/hr", style="yellow")
        table.add_column("Category")
        
        for t in templates:
            table.add_row(
                t.id[:12] + "..." if len(t.id) > 15 else t.id,
                t.name[:30] + "..." if len(t.name) > 33 else t.name,
                t.gpu_type,
                f"{t.min_gpu}-{t.max_gpu}",
                f"${t.hourly_price:.2f}",
                t.category or "-"
            )
        
        console.print(table)


@templates.command("get")
@click.argument("template_id")
def templates_get(template_id: str):
    """Get details of a specific template."""
    with get_client() as client:
        try:
            t = client.get_template(template_id)
            
            panel = Panel(
                f"""[cyan]ID:[/cyan] {t.id}
[cyan]Name:[/cyan] {t.name}
[cyan]Description:[/cyan] {t.description}
[cyan]Docker Image:[/cyan] {t.docker_image}
[cyan]GPU Type:[/cyan] {t.gpu_type}
[cyan]GPU Range:[/cyan] {t.min_gpu} - {t.max_gpu}
[cyan]Hourly Price:[/cyan] ${t.hourly_price:.2f}
[cyan]Category:[/cyan] {t.category or 'N/A'}""",
                title=f"Template: {t.name}",
                border_style="blue"
            )
            console.print(panel)
            
            console.print(f"\n[yellow]Create a pod:[/yellow] volt pods create --template {t.id} --name my-pod")
            
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


# ==================== SSH KEYS COMMANDS ====================

@cli.group("ssh-keys")
def ssh_keys():
    """Manage SSH keys."""
    pass


@ssh_keys.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def ssh_keys_list(as_json: bool):
    """List your SSH keys."""
    with get_client() as client:
        keys = client.list_ssh_keys()
        
        if as_json:
            import json
            data = [{"id": k.id, "name": k.name, "fingerprint": k.fingerprint} for k in keys]
            click.echo(json.dumps(data, indent=2))
            return
        
        if not keys:
            console.print("[yellow]No SSH keys found.[/yellow]")
            console.print("Add one with: volt ssh-keys add --name <name> --key <public_key>")
            return
        
        table = Table(title="Your SSH Keys")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Fingerprint", style="dim")
        
        for key in keys:
            table.add_row(
                key.id[:12] + "..." if len(key.id) > 15 else key.id,
                key.name,
                key.fingerprint or "-"
            )
        
        console.print(table)


@ssh_keys.command("add")
@click.option("--name", "-n", required=True, help="Name for the SSH key")
@click.option("--key", "-k", help="Public key string")
@click.option("--file", "-f", "key_file", type=click.Path(exists=True), help="Path to public key file")
def ssh_keys_add(name: str, key: str, key_file: str):
    """Add a new SSH key."""
    if not key and not key_file:
        console.print("[red]Error:[/red] Provide either --key or --file")
        sys.exit(1)
    
    if key_file:
        with open(key_file) as f:
            key = f.read().strip()
    
    with get_client() as client:
        try:
            ssh_key = client.add_ssh_key(name=name, public_key=key)
            console.print(f"[green]✓ SSH key added![/green]")
            console.print(f"  ID: {ssh_key.id}")
            console.print(f"  Name: {ssh_key.name}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@ssh_keys.command("delete")
@click.argument("key_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def ssh_keys_delete(key_id: str, yes: bool):
    """Delete an SSH key."""
    if not yes:
        if not click.confirm(f"Are you sure you want to delete SSH key {key_id}?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    with get_client() as client:
        try:
            client.delete_ssh_key(key_id)
            console.print(f"[green]✓ SSH key deleted![/green]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


# ==================== MACHINES COMMANDS ====================

@cli.group()
def machines():
    """Browse available machines."""
    pass


@machines.command("list")
@click.option("--gpu", "-g", help="Filter by GPU type (e.g., RTX4090, A100, H100)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def machines_list(gpu: str, as_json: bool):
    """List available machines."""
    with get_client() as client:
        machines = client.list_machines(gpu_type=gpu)
        
        if as_json:
            import json
            data = [{"id": m.id, "gpu_type": m.gpu_type, "gpu_count": m.gpu_count,
                    "hourly_price": m.hourly_price, "available": m.available} for m in machines]
            click.echo(json.dumps(data, indent=2))
            return
        
        if not machines:
            console.print("[yellow]No machines found.[/yellow]")
            return
        
        table = Table(title="Available Machines")
        table.add_column("ID", style="cyan")
        table.add_column("GPU", style="magenta")
        table.add_column("GPUs", justify="center")
        table.add_column("CPU", justify="center")
        table.add_column("RAM", justify="center")
        table.add_column("Storage", justify="center")
        table.add_column("$/hr", style="yellow")
        table.add_column("Status")
        
        for m in machines:
            status = "[green]Available[/green]" if m.available else "[red]In Use[/red]"
            table.add_row(
                m.id[:12] + "...",
                m.gpu_type,
                str(m.gpu_count),
                f"{m.cpu_cores} cores",
                f"{m.ram_gb} GB",
                f"{m.storage_gb} GB",
                f"${m.hourly_price:.2f}",
                status
            )
        
        console.print(table)


# ==================== ACCOUNT COMMANDS ====================

@cli.group()
def account():
    """Manage your account."""
    pass


@account.command("balance")
def account_balance():
    """Show your account balance."""
    with get_client() as client:
        try:
            balance = client.get_balance()
            console.print(f"[green]Account Balance:[/green] ${balance:.2f}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@account.command("info")
def account_info():
    """Show account information."""
    with get_client() as client:
        try:
            info = client.get_account_info()
            
            panel = Panel(
                "\n".join([f"[cyan]{k}:[/cyan] {v}" for k, v in info.items()]),
                title="Account Information",
                border_style="green"
            )
            console.print(panel)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


# ==================== CONFIG COMMAND ====================

@cli.command()
def config():
    """Show current configuration."""
    try:
        cfg = Config.load()
        console.print("[green]Configuration loaded successfully![/green]")
        console.print(f"  Base URL: {cfg.base_url}")
        console.print(f"  API Key: {cfg.api_key[:8]}...{cfg.api_key[-4:]}")
        if cfg.ssh_key_path:
            console.print(f"  SSH Key: {cfg.ssh_key_path}")
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
