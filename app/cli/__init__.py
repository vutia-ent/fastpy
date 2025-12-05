"""
Fastpy CLI modules.

This package contains CLI command implementations for the Fastpy framework.
"""
from app.cli.deploy import (
    DeployConfig,
    deploy_init,
    deploy_nginx,
    deploy_ssl,
    deploy_systemd,
    deploy_pm2,
    deploy_supervisor,
    deploy_process_manager,
    deploy_full,
    domain_add,
    domain_remove,
    domain_list,
    env_set,
    env_get,
    env_list,
    show_status,
    check_requirements,
    install_requirements,
)

from app.cli.setup import (
    setup_db,
    setup_secret,
    setup_admin,
    setup_hooks,
    setup_env,
    run_migrations,
    full_setup,
    DatabaseConfig,
)

__all__ = [
    # Deploy
    "DeployConfig",
    "deploy_init",
    "deploy_nginx",
    "deploy_ssl",
    "deploy_systemd",
    "deploy_pm2",
    "deploy_supervisor",
    "deploy_process_manager",
    "deploy_full",
    "domain_add",
    "domain_remove",
    "domain_list",
    "env_set",
    "env_get",
    "env_list",
    "show_status",
    "check_requirements",
    "install_requirements",
    # Setup
    "setup_db",
    "setup_secret",
    "setup_admin",
    "setup_hooks",
    "setup_env",
    "run_migrations",
    "full_setup",
    "DatabaseConfig",
]
