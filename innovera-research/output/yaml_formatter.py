"""
YAML output formatter for the evidence package.
"""
import yaml


def format_yaml_package(package: dict) -> str:
    """Format the evidence package as YAML."""
    return yaml.dump(
        package,
        default_flow_style=False,
        allow_unicode=True,
        width=120,
        sort_keys=False,
    )
