from app.core.log import logger
from app.state_machine import run_state_machine


def main():
    logger.info("=== Trunex VoIP Tester Booting ===")
    run_state_machine()


if __name__ == "__main__":
    main()
