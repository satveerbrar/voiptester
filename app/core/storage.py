# Add keystore, saved settings, etc. later

def save_value(key: str, value: str):
    with open("/tmp/voiptester_storage.txt", "a") as f:
        f.write(f"{key}={value}\n")


def load_all():
    try:
        with open("/tmp/voiptester_storage.txt") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []