from app.core.log import logger
from app.io.leds_button import LedButtonIO
from app.io.oled import OledDisplay
from app.testsuite.net_link import run_network_test


def run_state_machine():
    display = OledDisplay()
    io = LedButtonIO()

    logger.info("State machine started")

    display.show_message("Trunex VoIP Tester\nReady")
    io.led_idle()

    while True:
        event = io.read_button_event()

        if event == "single":
            logger.info("Running network test")
            display.show_message("Running Net Test...")
            io.led_busy()

            result = run_network_test()

            display.show_message(
                f"Status: {result['status']}"
                f"\nInterface: {result['interface']}"
                f"\nPhysical Link Up: {result['physical_link_up']}"
                f"\nLink State Up: {result["link_state_up"]}"
                f"\nLink Speed: {result['link_speed']}"
                f"\nIP: {result['ip_address']}"
                f"\nGateway:{result['gateway']}"
                f"\nDNS OK: {result['dns_ok']}"
                f"\nIP Source: {result['ip_source']}"
            )
            io.led_success()

        elif event == "double":
            display.show_message("SIP Test\n(Not Implemented)")
            logger.info("SIP test placeholder")
            io.led_error()

        elif event == "long":
            display.show_message("Shutdown\n(Not Implemented)")
            logger.info("Long press action placeholder")

        # loop continues waiting for next button event
