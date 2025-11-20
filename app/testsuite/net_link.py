import subprocess
from typing import Any, Optional


def run_network_test() -> dict[str, Any]:
    """
    Run a full network diagnostic test and return the results in a structured dictionary.

    This function performs basic network checks such as link detection, IP assignment,
    gateway reachability, DNS resolution, and internet connectivity. It summarizes all
    results into a single dictionary that can be used for logging, display, or APIs.

    Returns:
        dict[str, Any]: Dictionary containing network test results with the following keys:
            - **status** (str): "ok" if all tests pass, otherwise "fail".
            - **reason** (str): Human-readable reason for failure (e.g., "no link", "no ip", "dns failed").
            - **interface** (str): Network interface used for testing (e.g., "eth0").
            - **physical_link_up** (bool): Whether the Ethernet link is physically detected.
            - **physical_link_up** (bool): Whether the Ethernet link state is up.
            - **link_speed** (str): Detected link speed (e.g., "1G", "100M", "10M").
            - **ip_address** (str): The IP address assigned to the interface.
            - **gateway** (str): Default gateway address, if detected.
            - **dns_ok** (bool): Whether DNS resolution succeeded.
            - **ip_source** (str): Whether IP was assigned DHCP or static
    """
    default_interface = "eth0"

    result: dict[str, Any] = {
        "status": "ok",
        "reason": "",
        "interface": default_interface,
        "physical_link_up": False,
        "link_state_up": False,
        "link_speed": None,
        "ip_address": None,
        "gateway": None,
        "dns_ok": False,
        "ip_source": "none",
    }

    route_info = detect_default_route()
    route_interface = route_info.get("interface")
    route_gateway = route_info.get("gateway")
    route_ip = route_info.get("ip_address")

    has_default_route = route_interface is not None

    if has_default_route:
        result["interface"] = route_interface
        result["gateway"] = route_gateway
        result["ip_address"] = route_ip

    link_info = detect_interface_state(result["interface"])
    result["physical_link_up"] = link_info.get("physical_link_up", False)
    result["link_state_up"] = link_info.get("link_state_up", False)

    if not result["physical_link_up"]:
        result["status"] = "fail"
        result["reason"] = "no physical link"
        return result

    if not result["link_state_up"]:
        result["status"] = "fail"
        result["reason"] = "Link down"
        return result

    result["link_speed"] = get_link_speed(result["interface"])

    ip_info = detect_ip_source(result["interface"])
    result["ip_source"] = ip_info.get("ip_source", "none")

    if ip_info.get("ip_present"):
        result["ip_address"] = ip_info.get("ip_address")
    else:
        result["status"] = "fail"
        result["reason"] = "no ip address"
        return result

    result["dns_ok"] = dns_ok()
    if not result["dns_ok"]:
        result["status"] = "fail"
        result["reason"] = "dns failed"
        return result

    result["status"] = "ok"
    result["reason"] = ""

    return result


def detect_default_route() -> dict[str, Any]:
    """
    Ask the kernel how it would route traffic to 8.8.8.8 and extract:
    - interface (dev)
    - gateway (via)
    - ip_address (src)

    Returns a dict with keys:
      - "interface": str | None
      - "gateway": str | None
      - "ip_address: str | None
    """
    route_info: dict[str, Any] = {
        "gateway": None,
        "interface": None,
        "ip_address": None,
    }

    try:
        route_result = subprocess.run(
            ["ip", "route", "get", "8.8.8.8"], capture_output=True, text=True
        ).stdout
    except OSError as exc:
        route_info["error"] = str(exc)
        return route_info

    if not route_result:
        route_info["error"] = "no route output"
        return route_info
    tokens = route_result.strip().split()
    if not tokens:
        route_info["error"] = "empty route tokens"
        return route_info

    for i, token in enumerate(tokens):
        if token == "via" and i + 1 < len(tokens):
            route_info["gateway"] = tokens[i + 1]
        elif token == "dev" and i + 1 < len(tokens):
            route_info["interface"] = tokens[i + 1]
        elif token == "src" and i + 1 < len(tokens):
            route_info["ip_address"] = tokens[i + 1]

    return route_info


def detect_interface_state(interface: str) -> dict[str, Any]:
    """
    Check interface state using ip link show <interface> and extract:
    - LOWER UP (if physical interface is connected)
    - state UP (if interface is UP)
    :param interface: str

    :return: a dict with keys:
    - "physical_link_up": bool
    - "link_state_up": bool
    """
    interface_info: dict[str, Any] = {"physical_link_up": False, "link_state_up": False}

    try:
        result = subprocess.run(
            ["ip", "link", "show", interface], capture_output=True, text=True
        ).stdout
    except OSError as exc:
        interface_info["error"] = str(exc)
        return interface_info

    if not result:
        interface_info["error"] = "link state not available"
        return interface_info

    if "LOWER_UP" in result:
        interface_info["physical_link_up"] = True

    if "state UP" in result:
        interface_info["link_state_up"] = True

    return interface_info


def get_link_speed(interface: str) -> Optional[str]:
    """
    Check interface speed using ethtool <interface> abd extract:
    - link speed
    :param interface: str
    :return: a str representing link speed or None if unknown/unavailable
    """
    try:
        result = subprocess.run(
            ["ethtool", interface], capture_output=True, text=True
        ).stdout
    except OSError:
        return None

    lines = result.splitlines()
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("Speed:"):
            parts = stripped.split(":", 1)
            if len(parts) != 2:
                return None

            value = parts[1].strip()
            if not value:
                return None

            if "unknown" in value.lower():
                return None

            return value

    return None


def dns_ok() -> bool:
    """
    Check if DNS is working by doing query on google.com
    :return: bool
    """
    try:
        result = subprocess.run(
            ["dig", "+short", "google.com"], capture_output=True, text=True
        ).stdout.strip()
    except OSError:
        return False

    return bool(result)


def detect_ip_source(interface: str) -> dict[str, Any]:
    """
    Detect whether an interface's IPv4 address came from DHCP, static config, or if no IP is present.

    Uses: `ip -4 addr show dev <interface>`
    Logic:
      - If no 'inet ' line  → no IPv4 assigned (ip_source = "none")
      - If inet line contains 'dynamic' → DHCP
      - Else → static

    Returns a dict:
        {
            "ip_present": bool,
            "ip_address": str | None,
            "ip_source": "dhcp" | "static" | "none",
        }
    """

    info: dict[str, Any] = {
        "ip_present": False,
        "ip_address": None,
        "ip_source": "none",
    }

    try:
        result = subprocess.run(
            ["ip", "-4", "addr", "show", "dev", interface],
            capture_output=True,
            text=True,
        ).stdout
    except OSError as exc:
        info["error"] = str(exc)
        return info

    if not result:
        return info

    for line in result.splitlines():
        line = line.strip()

        if line.startswith("inet"):
            parts = line.split()
            if len(parts) < 2:
                continue

            addr = parts[1].split("/")[0]
            info["ip_address"] = addr
            info["ip_present"] = True

            if "dynamic" in line:
                info["ip_source"] = "dhcp"
            else:
                info["ip_source"] = "static"

            return info

    return info
