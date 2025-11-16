import subprocess

def basic_network_test():
    # Get IP
    ip = subprocess.getoutput("hostname -I").strip() or "no ip"

    # Ping
    result = subprocess.run(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL)
    ping_status = "OK" if result.returncode == 0 else "FAIL"

    return {
        "ip": ip,
        "ping_status": ping_status,
    }