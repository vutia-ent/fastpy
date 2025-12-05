"""
Fastpy Deploy - Production deployment commands for FastAPI applications.

Similar to Laravel Forge, this module handles:
- Server setup (Nginx, systemd, SSL)
- Domain management (CORS, allowed origins)
- Environment configuration
- Process management

Usage:
    fastpy deploy:init              # Initialize deployment configuration
    fastpy deploy:nginx             # Generate/apply Nginx configuration
    fastpy deploy:ssl               # Setup SSL with Let's Encrypt
    fastpy deploy:systemd           # Create systemd service
    fastpy deploy:run               # Full deployment
    fastpy domain:add               # Add allowed domain for CORS
    fastpy domain:list              # List configured domains
    fastpy env:set KEY=value        # Set environment variable
"""
import os
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Rich imports for CLI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    console = Console()
except ImportError:
    console = None


# ============================================================================
# CONFIGURATION
# ============================================================================

DEPLOY_CONFIG_FILE = ".fastpy/deploy.json"
ENV_FILE = ".env"
NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"
SYSTEMD_DIR = "/etc/systemd/system"


@dataclass
class DeployConfig:
    """Deployment configuration."""
    # App info
    app_name: str = "fastpy-app"
    app_path: str = ""

    # Server
    domain: str = ""
    port: int = 8000
    workers: int = 4

    # Domains for CORS
    allowed_origins: List[str] = field(default_factory=list)
    frontend_domains: List[str] = field(default_factory=list)

    # SSL
    ssl_enabled: bool = False
    ssl_email: str = ""
    ssl_type: str = "letsencrypt"  # letsencrypt, selfsigned, none

    # Process management
    process_manager: str = "systemd"  # systemd, pm2, supervisor
    user: str = "www-data"
    group: str = "www-data"

    # Python
    python_path: str = ""
    venv_path: str = ""

    # Gunicorn/Uvicorn
    use_gunicorn: bool = True
    uvicorn_workers: int = 4

    # Nginx
    nginx_enabled: bool = True

    # Timestamps
    created_at: str = ""
    updated_at: str = ""

    def save(self):
        """Save configuration to file."""
        config_path = Path(DEPLOY_CONFIG_FILE)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = self.updated_at
        config_path.write_text(json.dumps(asdict(self), indent=2))

    @classmethod
    def load(cls) -> "DeployConfig":
        """Load configuration from file."""
        config_path = Path(DEPLOY_CONFIG_FILE)
        if config_path.exists():
            data = json.loads(config_path.read_text())
            return cls(**data)
        return cls()

    @classmethod
    def exists(cls) -> bool:
        """Check if config exists."""
        return Path(DEPLOY_CONFIG_FILE).exists()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log_info(msg: str):
    """Log info message."""
    if console:
        console.print(f"[blue][INFO][/blue] {msg}")
    else:
        print(f"[INFO] {msg}")


def log_success(msg: str):
    """Log success message."""
    if console:
        console.print(f"[green][OK][/green] {msg}")
    else:
        print(f"[OK] {msg}")


def log_warning(msg: str):
    """Log warning message."""
    if console:
        console.print(f"[yellow][WARN][/yellow] {msg}")
    else:
        print(f"[WARN] {msg}")


def log_error(msg: str):
    """Log error message."""
    if console:
        console.print(f"[red][ERROR][/red] {msg}")
    else:
        print(f"[ERROR] {msg}")


def run_command(cmd: List[str], check: bool = True, sudo: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command."""
    if sudo:
        cmd = ["sudo"] + cmd
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def is_root() -> bool:
    """Check if running as root."""
    return os.geteuid() == 0


def check_command_exists(cmd: str) -> bool:
    """Check if a command exists."""
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0


def detect_python_env() -> tuple:
    """Detect Python and virtualenv paths."""
    # Check if in virtualenv
    venv_path = os.environ.get("VIRTUAL_ENV", "")
    if not venv_path:
        # Check for common venv locations
        for venv_name in ["venv", ".venv", "env"]:
            if Path(venv_name).exists():
                venv_path = str(Path(venv_name).absolute())
                break

    python_path = sys.executable
    return python_path, venv_path


# ============================================================================
# NGINX CONFIGURATION
# ============================================================================

def generate_nginx_config(config: DeployConfig) -> str:
    """Generate Nginx configuration for FastAPI."""

    # Build allowed origins for CORS
    all_origins = set(config.allowed_origins + config.frontend_domains)
    if config.domain:
        all_origins.add(f"https://{config.domain}")
        all_origins.add(f"http://{config.domain}")

    cors_origins = " ".join(f'"{origin}"' for origin in sorted(all_origins)) if all_origins else '"*"'

    # SSL configuration
    if config.ssl_enabled and config.ssl_type == "letsencrypt":
        ssl_config = f"""
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    ssl_certificate /etc/letsencrypt/live/{config.domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{config.domain}/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;"""

        http_redirect = f"""
# HTTP to HTTPS redirect
server {{
    listen 80;
    listen [::]:80;
    server_name {config.domain};
    return 301 https://$server_name$request_uri;
}}
"""
    else:
        ssl_config = """
    listen 80;
    listen [::]:80;"""
        http_redirect = ""

    nginx_config = f"""{http_redirect}
# FastAPI Application: {config.app_name}
# Generated by Fastpy CLI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

upstream {config.app_name}_backend {{
    server 127.0.0.1:{config.port};
    keepalive 64;
}}

server {{
    {ssl_config}

    server_name {config.domain};

    # Logging
    access_log /var/log/nginx/{config.app_name}_access.log;
    error_log /var/log/nginx/{config.app_name}_error.log;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # CORS headers (handled by FastAPI, but can be added here too)
    # Allowed origins: {', '.join(sorted(all_origins)) if all_origins else '*'}

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;

    # Client settings
    client_max_body_size 100M;
    client_body_buffer_size 128k;

    # Proxy settings
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    proxy_set_header Connection "";

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # WebSocket support
    location /ws {{
        proxy_pass http://{config.app_name}_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }}

    # API endpoints
    location / {{
        proxy_pass http://{config.app_name}_backend;

        # Handle preflight requests
        if ($request_method = 'OPTIONS') {{
            add_header 'Access-Control-Allow-Origin' $http_origin always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, PATCH, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }}
    }}

    # Static files (if serving from FastAPI)
    location /static {{
        alias {config.app_path}/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}

    # Health check endpoint (no logging)
    location /health {{
        proxy_pass http://{config.app_name}_backend;
        access_log off;
    }}

    # Deny access to sensitive files
    location ~ /\\. {{
        deny all;
    }}

    location ~ \\.(env|git|md)$ {{
        deny all;
    }}
}}
"""
    return nginx_config


# ============================================================================
# SYSTEMD SERVICE
# ============================================================================

def generate_systemd_service(config: DeployConfig) -> str:
    """Generate systemd service file for FastAPI."""

    if config.use_gunicorn:
        # Gunicorn with Uvicorn workers (recommended for production)
        exec_start = f"{config.venv_path}/bin/gunicorn main:app -w {config.uvicorn_workers} -k uvicorn.workers.UvicornWorker -b 127.0.0.1:{config.port}"
    else:
        # Direct Uvicorn
        exec_start = f"{config.venv_path}/bin/uvicorn main:app --host 127.0.0.1 --port {config.port} --workers {config.uvicorn_workers}"

    service = f"""[Unit]
Description={config.app_name} FastAPI Application
After=network.target
Wants=network-online.target

[Service]
Type=exec
User={config.user}
Group={config.group}
WorkingDirectory={config.app_path}
Environment="PATH={config.venv_path}/bin"
EnvironmentFile={config.app_path}/.env
ExecStart={exec_start}
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StartLimitInterval=0

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={config.app_path}

# Logging
StandardOutput=append:/var/log/{config.app_name}/app.log
StandardError=append:/var/log/{config.app_name}/error.log

[Install]
WantedBy=multi-user.target
"""
    return service


# ============================================================================
# PM2 CONFIGURATION
# ============================================================================

def generate_pm2_ecosystem(config: DeployConfig) -> str:
    """Generate PM2 ecosystem.config.js for FastAPI."""

    if config.use_gunicorn:
        script = f"{config.venv_path}/bin/gunicorn"
        args = f"main:app -w {config.uvicorn_workers} -k uvicorn.workers.UvicornWorker -b 127.0.0.1:{config.port}"
    else:
        script = f"{config.venv_path}/bin/uvicorn"
        args = f"main:app --host 127.0.0.1 --port {config.port} --workers {config.uvicorn_workers}"

    ecosystem = f"""// PM2 Ecosystem Configuration
// Generated by Fastpy CLI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Start: pm2 start ecosystem.config.js
// Restart: pm2 restart {config.app_name}
// Logs: pm2 logs {config.app_name}

module.exports = {{
  apps: [
    {{
      name: "{config.app_name}",
      script: "{script}",
      args: "{args}",
      cwd: "{config.app_path}",
      interpreter: "none",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {{
        NODE_ENV: "production",
        PATH: "{config.venv_path}/bin:" + process.env.PATH,
      }},
      env_file: "{config.app_path}/.env",
      error_file: "/var/log/{config.app_name}/pm2-error.log",
      out_file: "/var/log/{config.app_name}/pm2-out.log",
      log_file: "/var/log/{config.app_name}/pm2-combined.log",
      time: true,
      merge_logs: true,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",

      // Graceful shutdown
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000,

      // Restart policy
      exp_backoff_restart_delay: 100,
      max_restarts: 10,
      restart_delay: 1000,
    }},
  ],
}};
"""
    return ecosystem


def generate_pm2_startup_script(config: DeployConfig) -> str:
    """Generate PM2 startup commands."""
    return f"""#!/bin/bash
# PM2 Startup Script for {config.app_name}
# Generated by Fastpy CLI

# Create log directory
sudo mkdir -p /var/log/{config.app_name}
sudo chown {config.user}:{config.group} /var/log/{config.app_name}

# Start the application
cd {config.app_path}
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Setup PM2 to start on boot (run as root)
# pm2 startup systemd -u {config.user} --hp /home/{config.user}

echo "Application started with PM2"
echo "Commands:"
echo "  pm2 status          - Check status"
echo "  pm2 logs {config.app_name}  - View logs"
echo "  pm2 restart {config.app_name} - Restart app"
echo "  pm2 stop {config.app_name}    - Stop app"
"""


# ============================================================================
# SUPERVISOR CONFIGURATION
# ============================================================================

def generate_supervisor_config(config: DeployConfig) -> str:
    """Generate Supervisor configuration for FastAPI."""

    if config.use_gunicorn:
        command = f"{config.venv_path}/bin/gunicorn main:app -w {config.uvicorn_workers} -k uvicorn.workers.UvicornWorker -b 127.0.0.1:{config.port}"
    else:
        command = f"{config.venv_path}/bin/uvicorn main:app --host 127.0.0.1 --port {config.port} --workers {config.uvicorn_workers}"

    supervisor_conf = f"""; Supervisor Configuration for {config.app_name}
; Generated by Fastpy CLI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
;
; Install: sudo cp {config.app_name}.conf /etc/supervisor/conf.d/
; Reload:  sudo supervisorctl reread && sudo supervisorctl update
; Start:   sudo supervisorctl start {config.app_name}
; Status:  sudo supervisorctl status {config.app_name}
; Logs:    sudo supervisorctl tail -f {config.app_name}

[program:{config.app_name}]
command={command}
directory={config.app_path}
user={config.user}
group={config.group}
autostart=true
autorestart=true
startsecs=10
startretries=3
stopwaitsecs=10
stopasgroup=true
killasgroup=true

; Environment
environment=PATH="{config.venv_path}/bin:%(ENV_PATH)s"

; Logging
stdout_logfile=/var/log/{config.app_name}/supervisor-stdout.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=/var/log/{config.app_name}/supervisor-stderr.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10
redirect_stderr=false

; Process management
numprocs=1
process_name=%(program_name)s

; Priority (lower = start earlier)
priority=100
"""
    return supervisor_conf


def generate_supervisor_group(config: DeployConfig) -> str:
    """Generate Supervisor group configuration (for multiple apps)."""
    return f"""; Supervisor Group for Fastpy Applications
; Add to /etc/supervisor/conf.d/fastpy-group.conf

[group:fastpy]
programs={config.app_name}
priority=999
"""


# ============================================================================
# CORS/DOMAIN MANAGEMENT
# ============================================================================

def update_env_cors(config: DeployConfig):
    """Update .env file with CORS origins."""
    env_path = Path(config.app_path) / ".env" if config.app_path else Path(".env")

    all_origins = sorted(set(config.allowed_origins + config.frontend_domains))
    cors_value = ",".join(all_origins) if all_origins else "*"

    if env_path.exists():
        content = env_path.read_text()
        lines = content.split("\n")
        updated = False

        for i, line in enumerate(lines):
            if line.startswith("CORS_ORIGINS=") or line.startswith("ALLOWED_ORIGINS="):
                lines[i] = f"CORS_ORIGINS={cors_value}"
                updated = True
                break

        if not updated:
            lines.append(f"CORS_ORIGINS={cors_value}")

        env_path.write_text("\n".join(lines))
    else:
        env_path.write_text(f"CORS_ORIGINS={cors_value}\n")

    log_success(f"Updated CORS_ORIGINS in {env_path}")


def generate_cors_middleware_code(config: DeployConfig) -> str:
    """Generate CORS middleware configuration code."""
    all_origins = sorted(set(config.allowed_origins + config.frontend_domains))

    if not all_origins:
        origins_code = '["*"]  # Allow all origins (development)'
    else:
        origins_list = ",\n        ".join(f'"{origin}"' for origin in all_origins)
        origins_code = f"""[
        {origins_list},
    ]"""

    return f'''# CORS Configuration - Generated by fastpy deploy
# Add this to your main.py

from fastapi.middleware.cors import CORSMiddleware
import os

# Get origins from environment or use defaults
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    origins = {origins_code}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)
'''


# ============================================================================
# DEPLOY COMMANDS
# ============================================================================

def deploy_init(
    app_name: Optional[str] = None,
    domain: Optional[str] = None,
    port: int = 8000,
    interactive: bool = True
) -> DeployConfig:
    """Initialize deployment configuration."""

    config = DeployConfig.load() if DeployConfig.exists() else DeployConfig()

    if interactive:
        if console:
            console.print(Panel.fit(
                "[bold cyan]Fastpy Deploy Initialization[/bold cyan]\n"
                "Configure your FastAPI application for production deployment.",
                border_style="cyan"
            ))

        # App name
        default_name = config.app_name or Path.cwd().name
        config.app_name = Prompt.ask(
            "Application name",
            default=default_name
        ) if console else input(f"Application name [{default_name}]: ") or default_name

        # Domain
        config.domain = Prompt.ask(
            "Domain name (e.g., api.example.com)",
            default=config.domain or ""
        ) if console else input(f"Domain name [{config.domain}]: ") or config.domain

        # Port
        config.port = int(Prompt.ask(
            "Application port",
            default=str(config.port)
        ) if console else input(f"Application port [{config.port}]: ") or config.port)

        # Workers
        import multiprocessing
        default_workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
        config.uvicorn_workers = int(Prompt.ask(
            "Number of workers",
            default=str(default_workers)
        ) if console else input(f"Workers [{default_workers}]: ") or default_workers)

        # SSL
        ssl_choice = Prompt.ask(
            "SSL type",
            choices=["letsencrypt", "selfsigned", "none"],
            default="letsencrypt" if config.domain else "none"
        ) if console else "letsencrypt"
        config.ssl_type = ssl_choice
        config.ssl_enabled = ssl_choice != "none"

        if config.ssl_enabled and config.ssl_type == "letsencrypt":
            config.ssl_email = Prompt.ask(
                "Email for Let's Encrypt",
                default=config.ssl_email
            ) if console else input(f"SSL Email [{config.ssl_email}]: ") or config.ssl_email

        # Frontend domains
        frontend_input = Prompt.ask(
            "Frontend domains for CORS (comma-separated, or empty)",
            default=",".join(config.frontend_domains)
        ) if console else input("Frontend domains: ")

        if frontend_input:
            config.frontend_domains = [d.strip() for d in frontend_input.split(",") if d.strip()]

        # Process manager
        pm_choice = Prompt.ask(
            "Process manager",
            choices=["systemd", "pm2", "supervisor"],
            default=config.process_manager or "systemd"
        ) if console else "systemd"
        config.process_manager = pm_choice

        # User
        config.user = Prompt.ask(
            "System user to run the app",
            default=config.user or "www-data"
        ) if console else input(f"User [{config.user}]: ") or config.user

    else:
        if app_name:
            config.app_name = app_name
        if domain:
            config.domain = domain
        config.port = port

    # Auto-detect paths
    config.app_path = str(Path.cwd().absolute())
    python_path, venv_path = detect_python_env()
    config.python_path = python_path
    config.venv_path = venv_path or f"{config.app_path}/venv"

    # Save config
    config.save()

    log_success(f"Configuration saved to {DEPLOY_CONFIG_FILE}")
    return config


def deploy_nginx(config: Optional[DeployConfig] = None, apply: bool = False):
    """Generate and optionally apply Nginx configuration."""

    if not config:
        if not DeployConfig.exists():
            log_error("No deployment config found. Run 'fastpy deploy:init' first.")
            return
        config = DeployConfig.load()

    if not config.domain:
        log_error("Domain not configured. Run 'fastpy deploy:init' first.")
        return

    nginx_config = generate_nginx_config(config)

    # Save to local file
    local_path = Path(f".fastpy/nginx/{config.app_name}.conf")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(nginx_config)
    log_success(f"Nginx config saved to {local_path}")

    if apply:
        if not is_root():
            log_error("Root privileges required to apply Nginx config. Run with sudo.")
            return

        # Copy to Nginx sites-available
        nginx_path = Path(f"{NGINX_SITES_AVAILABLE}/{config.app_name}")
        nginx_path.write_text(nginx_config)
        log_success(f"Nginx config written to {nginx_path}")

        # Enable site
        enabled_path = Path(f"{NGINX_SITES_ENABLED}/{config.app_name}")
        if not enabled_path.exists():
            enabled_path.symlink_to(nginx_path)
            log_success(f"Site enabled: {enabled_path}")

        # Test config
        result = run_command(["nginx", "-t"], check=False, sudo=True)
        if result.returncode == 0:
            log_success("Nginx configuration test passed")

            # Reload Nginx
            run_command(["systemctl", "reload", "nginx"], sudo=True)
            log_success("Nginx reloaded")
        else:
            log_error(f"Nginx config test failed: {result.stderr}")
    else:
        log_info(f"To apply: sudo cp {local_path} {NGINX_SITES_AVAILABLE}/{config.app_name}")
        log_info(f"Then: sudo ln -s {NGINX_SITES_AVAILABLE}/{config.app_name} {NGINX_SITES_ENABLED}/")
        log_info("Then: sudo nginx -t && sudo systemctl reload nginx")


def deploy_ssl(config: Optional[DeployConfig] = None):
    """Setup SSL with Let's Encrypt."""

    if not config:
        if not DeployConfig.exists():
            log_error("No deployment config found. Run 'fastpy deploy:init' first.")
            return
        config = DeployConfig.load()

    if not config.domain:
        log_error("Domain not configured.")
        return

    if config.ssl_type != "letsencrypt":
        log_warning("SSL type is not Let's Encrypt. Skipping.")
        return

    if not is_root():
        log_error("Root privileges required for SSL setup. Run with sudo.")
        return

    # Check certbot
    if not check_command_exists("certbot"):
        log_info("Installing certbot...")
        run_command(["apt-get", "update"], sudo=True)
        run_command(["apt-get", "install", "-y", "certbot", "python3-certbot-nginx"], sudo=True)

    # Run certbot
    cmd = [
        "certbot", "certonly", "--nginx",
        "-d", config.domain,
        "--non-interactive",
        "--agree-tos",
        "-m", config.ssl_email
    ]

    # Add www subdomain if it's a root domain
    if config.domain.count(".") == 1:
        cmd.extend(["-d", f"www.{config.domain}"])

    result = run_command(cmd, check=False, sudo=True)
    if result.returncode == 0:
        log_success("SSL certificate obtained successfully")

        # Update config
        config.ssl_enabled = True
        config.save()

        # Regenerate Nginx config with SSL
        deploy_nginx(config, apply=True)
    else:
        log_error(f"Certbot failed: {result.stderr}")


def deploy_systemd(config: Optional[DeployConfig] = None, apply: bool = False):
    """Generate and optionally apply systemd service."""

    if not config:
        if not DeployConfig.exists():
            log_error("No deployment config found. Run 'fastpy deploy:init' first.")
            return
        config = DeployConfig.load()

    service_content = generate_systemd_service(config)

    # Save to local file
    local_path = Path(f".fastpy/systemd/{config.app_name}.service")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(service_content)
    log_success(f"Systemd service saved to {local_path}")

    if apply:
        if not is_root():
            log_error("Root privileges required. Run with sudo.")
            return

        # Create log directory
        log_dir = Path(f"/var/log/{config.app_name}")
        log_dir.mkdir(parents=True, exist_ok=True)
        run_command(["chown", f"{config.user}:{config.group}", str(log_dir)], sudo=True)

        # Copy service file
        service_path = Path(f"{SYSTEMD_DIR}/{config.app_name}.service")
        service_path.write_text(service_content)
        log_success(f"Service file written to {service_path}")

        # Reload systemd
        run_command(["systemctl", "daemon-reload"], sudo=True)

        # Enable and start service
        run_command(["systemctl", "enable", config.app_name], sudo=True)
        run_command(["systemctl", "start", config.app_name], sudo=True)
        log_success(f"Service {config.app_name} enabled and started")

        # Show status
        result = run_command(["systemctl", "status", config.app_name], check=False, sudo=True)
        if console:
            console.print(result.stdout)
    else:
        log_info(f"To apply: sudo cp {local_path} {SYSTEMD_DIR}/")
        log_info("Then: sudo systemctl daemon-reload")
        log_info(f"Then: sudo systemctl enable --now {config.app_name}")


def deploy_pm2(config: Optional[DeployConfig] = None, apply: bool = False):
    """Generate and optionally apply PM2 ecosystem configuration."""

    if not config:
        if not DeployConfig.exists():
            log_error("No deployment config found. Run 'fastpy deploy:init' first.")
            return
        config = DeployConfig.load()

    # Generate ecosystem.config.js
    ecosystem_content = generate_pm2_ecosystem(config)

    # Save to local file
    local_path = Path(f".fastpy/pm2/ecosystem.config.js")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(ecosystem_content)
    log_success(f"PM2 ecosystem config saved to {local_path}")

    # Also save to project root for convenience
    root_ecosystem = Path("ecosystem.config.js")
    root_ecosystem.write_text(ecosystem_content)
    log_success(f"PM2 ecosystem config saved to {root_ecosystem}")

    # Generate startup script
    startup_script = generate_pm2_startup_script(config)
    startup_path = Path(f".fastpy/pm2/start.sh")
    startup_path.write_text(startup_script)
    startup_path.chmod(0o755)
    log_success(f"PM2 startup script saved to {startup_path}")

    if apply:
        # Check if PM2 is installed
        if not check_command_exists("pm2"):
            log_error("PM2 is not installed. Install with: npm install -g pm2")
            return

        # Create log directory
        log_dir = Path(f"/var/log/{config.app_name}")
        if is_root():
            log_dir.mkdir(parents=True, exist_ok=True)
            run_command(["chown", f"{config.user}:{config.group}", str(log_dir)], sudo=True)

        # Start with PM2
        result = run_command(["pm2", "start", "ecosystem.config.js"], check=False)
        if result.returncode == 0:
            log_success(f"Application started with PM2")

            # Save PM2 process list
            run_command(["pm2", "save"], check=False)
            log_info("PM2 process list saved")

            # Show status
            result = run_command(["pm2", "status"], check=False)
            if console:
                console.print(result.stdout)
        else:
            log_error(f"PM2 start failed: {result.stderr}")
    else:
        log_info("To start with PM2:")
        log_info("  pm2 start ecosystem.config.js")
        log_info("  pm2 save")
        log_info("  pm2 startup  # to start on boot")


def deploy_supervisor(config: Optional[DeployConfig] = None, apply: bool = False):
    """Generate and optionally apply Supervisor configuration."""

    if not config:
        if not DeployConfig.exists():
            log_error("No deployment config found. Run 'fastpy deploy:init' first.")
            return
        config = DeployConfig.load()

    # Generate supervisor config
    supervisor_content = generate_supervisor_config(config)

    # Save to local file
    local_path = Path(f".fastpy/supervisor/{config.app_name}.conf")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(supervisor_content)
    log_success(f"Supervisor config saved to {local_path}")

    if apply:
        if not is_root():
            log_error("Root privileges required. Run with sudo.")
            return

        # Check if supervisor is installed
        if not check_command_exists("supervisorctl"):
            log_info("Installing supervisor...")
            run_command(["apt-get", "update"], sudo=True)
            run_command(["apt-get", "install", "-y", "supervisor"], sudo=True)

        # Create log directory
        log_dir = Path(f"/var/log/{config.app_name}")
        log_dir.mkdir(parents=True, exist_ok=True)
        run_command(["chown", f"{config.user}:{config.group}", str(log_dir)], sudo=True)

        # Copy config to supervisor conf.d
        supervisor_conf_dir = Path("/etc/supervisor/conf.d")
        target_path = supervisor_conf_dir / f"{config.app_name}.conf"
        target_path.write_text(supervisor_content)
        log_success(f"Supervisor config written to {target_path}")

        # Reload supervisor
        run_command(["supervisorctl", "reread"], sudo=True)
        run_command(["supervisorctl", "update"], sudo=True)
        log_success("Supervisor configuration reloaded")

        # Start the app
        result = run_command(["supervisorctl", "start", config.app_name], check=False, sudo=True)
        if result.returncode == 0:
            log_success(f"Application {config.app_name} started with Supervisor")
        else:
            log_warning(f"Start result: {result.stderr or result.stdout}")

        # Show status
        result = run_command(["supervisorctl", "status", config.app_name], check=False, sudo=True)
        if console:
            console.print(result.stdout)
    else:
        log_info(f"To apply: sudo cp {local_path} /etc/supervisor/conf.d/")
        log_info("Then: sudo supervisorctl reread && sudo supervisorctl update")
        log_info(f"Then: sudo supervisorctl start {config.app_name}")


def deploy_process_manager(config: Optional[DeployConfig] = None, apply: bool = False):
    """Deploy using the configured process manager."""

    if not config:
        if not DeployConfig.exists():
            log_error("No deployment config found. Run 'fastpy deploy:init' first.")
            return
        config = DeployConfig.load()

    pm = config.process_manager

    if pm == "systemd":
        deploy_systemd(config, apply=apply)
    elif pm == "pm2":
        deploy_pm2(config, apply=apply)
    elif pm == "supervisor":
        deploy_supervisor(config, apply=apply)
    else:
        log_error(f"Unknown process manager: {pm}")
        log_info("Supported: systemd, pm2, supervisor")


def deploy_full(apply: bool = False):
    """Run full deployment."""

    if not DeployConfig.exists():
        log_info("No configuration found. Starting initialization...")
        config = deploy_init()
    else:
        config = DeployConfig.load()

    if console:
        console.print(Panel.fit(
            f"[bold]Deploying: {config.app_name}[/bold]\n"
            f"Domain: {config.domain}\n"
            f"Port: {config.port}\n"
            f"Process Manager: {config.process_manager}\n"
            f"SSL: {config.ssl_type}",
            title="Deployment Summary",
            border_style="green"
        ))

    # Update CORS
    update_env_cors(config)

    # Generate Nginx config
    deploy_nginx(config, apply=apply)

    # Generate process manager config (systemd/pm2/supervisor)
    deploy_process_manager(config, apply=apply)

    # SSL (only if applying)
    if apply and config.ssl_enabled and config.ssl_type == "letsencrypt":
        deploy_ssl(config)

    log_success("Deployment configuration complete!")

    if not apply:
        if console:
            console.print("\n[yellow]To apply the configuration:[/yellow]")
            console.print("  sudo fastpy deploy:run --apply")
            console.print("\nOr apply individually:")
            console.print("  sudo fastpy deploy:nginx --apply")
            console.print("  sudo fastpy deploy:systemd --apply")
            console.print("  sudo fastpy deploy:ssl")


def domain_add(domain: str, domain_type: str = "cors"):
    """Add a domain to allowed origins."""

    if not DeployConfig.exists():
        log_error("No deployment config found. Run 'fastpy deploy:init' first.")
        return

    config = DeployConfig.load()

    # Normalize domain
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"

    if domain_type == "frontend":
        if domain not in config.frontend_domains:
            config.frontend_domains.append(domain)
            log_success(f"Added frontend domain: {domain}")
        else:
            log_warning(f"Domain already in frontend list: {domain}")
    else:
        if domain not in config.allowed_origins:
            config.allowed_origins.append(domain)
            log_success(f"Added CORS origin: {domain}")
        else:
            log_warning(f"Domain already in CORS list: {domain}")

    config.save()
    update_env_cors(config)

    # Show CORS middleware code
    if console:
        console.print("\n[cyan]Update your CORS middleware:[/cyan]")
        console.print(generate_cors_middleware_code(config))


def domain_remove(domain: str):
    """Remove a domain from allowed origins."""

    if not DeployConfig.exists():
        log_error("No deployment config found.")
        return

    config = DeployConfig.load()

    # Try both with and without protocol
    variants = [domain]
    if not domain.startswith(("http://", "https://")):
        variants.extend([f"https://{domain}", f"http://{domain}"])

    removed = False
    for d in variants:
        if d in config.allowed_origins:
            config.allowed_origins.remove(d)
            removed = True
        if d in config.frontend_domains:
            config.frontend_domains.remove(d)
            removed = True

    if removed:
        config.save()
        update_env_cors(config)
        log_success(f"Removed domain: {domain}")
    else:
        log_warning(f"Domain not found: {domain}")


def domain_list():
    """List all configured domains."""

    if not DeployConfig.exists():
        log_error("No deployment config found.")
        return

    config = DeployConfig.load()

    if console:
        table = Table(title="Configured Domains")
        table.add_column("Domain", style="cyan")
        table.add_column("Type", style="green")

        for domain in config.allowed_origins:
            table.add_row(domain, "CORS Origin")

        for domain in config.frontend_domains:
            table.add_row(domain, "Frontend")

        if config.domain:
            table.add_row(f"https://{config.domain}", "Primary")

        console.print(table)
    else:
        print("Configured Domains:")
        for domain in config.allowed_origins:
            print(f"  {domain} (CORS)")
        for domain in config.frontend_domains:
            print(f"  {domain} (Frontend)")


def env_set(key: str, value: str):
    """Set an environment variable in .env file."""

    env_path = Path(".env")

    if env_path.exists():
        content = env_path.read_text()
        lines = content.split("\n")
        updated = False

        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                updated = True
                break

        if not updated:
            lines.append(f"{key}={value}")

        env_path.write_text("\n".join(lines))
    else:
        env_path.write_text(f"{key}={value}\n")

    log_success(f"Set {key} in .env")


def env_get(key: str) -> Optional[str]:
    """Get an environment variable from .env file."""

    env_path = Path(".env")

    if not env_path.exists():
        return None

    content = env_path.read_text()
    for line in content.split("\n"):
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1]

    return None


def env_list():
    """List all environment variables."""

    env_path = Path(".env")

    if not env_path.exists():
        log_warning("No .env file found")
        return

    if console:
        table = Table(title="Environment Variables")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        content = env_path.read_text()
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                # Mask sensitive values
                if any(s in key.lower() for s in ["secret", "password", "key", "token"]):
                    value = "*" * min(len(value), 8)
                table.add_row(key, value)

        console.print(table)
    else:
        print(env_path.read_text())


def show_status():
    """Show deployment status."""

    if not DeployConfig.exists():
        log_warning("No deployment configuration found")
        return

    config = DeployConfig.load()

    if console:
        # Config panel
        console.print(Panel.fit(
            f"[bold]App:[/bold] {config.app_name}\n"
            f"[bold]Domain:[/bold] {config.domain or 'Not configured'}\n"
            f"[bold]Port:[/bold] {config.port}\n"
            f"[bold]Workers:[/bold] {config.uvicorn_workers}\n"
            f"[bold]SSL:[/bold] {config.ssl_type}\n"
            f"[bold]Path:[/bold] {config.app_path}",
            title="Deployment Configuration",
            border_style="cyan"
        ))

        # Check service status
        result = subprocess.run(
            ["systemctl", "is-active", config.app_name],
            capture_output=True, text=True
        )
        service_status = result.stdout.strip()
        status_color = "green" if service_status == "active" else "red"

        console.print(f"\n[bold]Service Status:[/bold] [{status_color}]{service_status}[/{status_color}]")

        # Check Nginx
        nginx_enabled = Path(f"{NGINX_SITES_ENABLED}/{config.app_name}").exists()
        nginx_status = "enabled" if nginx_enabled else "not enabled"
        nginx_color = "green" if nginx_enabled else "yellow"

        console.print(f"[bold]Nginx:[/bold] [{nginx_color}]{nginx_status}[/{nginx_color}]")

        # Check SSL
        if config.ssl_enabled:
            cert_path = Path(f"/etc/letsencrypt/live/{config.domain}/fullchain.pem")
            ssl_status = "valid" if cert_path.exists() else "not found"
            ssl_color = "green" if cert_path.exists() else "red"
            console.print(f"[bold]SSL Certificate:[/bold] [{ssl_color}]{ssl_status}[/{ssl_color}]")


# ============================================================================
# HELPER: Check server requirements
# ============================================================================

def check_requirements() -> Dict[str, bool]:
    """Check if server requirements are met."""

    requirements = {
        "python3": check_command_exists("python3"),
        "pip": check_command_exists("pip3") or check_command_exists("pip"),
        "nginx": check_command_exists("nginx"),
        "systemctl": check_command_exists("systemctl"),
        "certbot": check_command_exists("certbot"),
    }

    # Check Python packages
    try:
        import uvicorn
        requirements["uvicorn"] = True
    except ImportError:
        requirements["uvicorn"] = False

    try:
        import gunicorn
        requirements["gunicorn"] = True
    except ImportError:
        requirements["gunicorn"] = False

    return requirements


def install_requirements():
    """Install missing server requirements."""

    if not is_root():
        log_error("Root privileges required. Run with sudo.")
        return

    log_info("Updating package lists...")
    run_command(["apt-get", "update"], sudo=True)

    packages = ["nginx", "certbot", "python3-certbot-nginx"]

    for pkg in packages:
        log_info(f"Installing {pkg}...")
        run_command(["apt-get", "install", "-y", pkg], sudo=True, check=False)

    # Python packages
    log_info("Installing Python packages...")
    run_command([sys.executable, "-m", "pip", "install", "gunicorn", "uvicorn[standard]"])

    log_success("Requirements installed")
