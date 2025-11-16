from app.core.log import logger
from app.testsuite.net_link import basic_network_test
from app.io.oled import OledDisplay
from app.io.leds_button import LedButtonIO


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

            result = basic_network_test()

            display.show_message(f"IP: {result['ip']}\nPing:{result['ping_status']}")
            io.led_success()

        elif event == "double":
            display.show_message("SIP Test\n(Not Implemented)")
            logger.info("SIP test placeholder")
            io.led_error()

        elif event == "long":
            display.show_message("Shutdown\n(Not Implemented)")
            logger.info("Long press action placeholder")

        # loop continues waiting for next button event
