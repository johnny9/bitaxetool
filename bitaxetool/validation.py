
def check_validate_dependencies() -> Optional[str]:
    try:
        import cerberus
    except ImportError:
        return \
        """The --validate_config option requires the cerberus package.
        Install it with: pip install cerberus or pip install bitaxetool[validate]
        """

    return None
