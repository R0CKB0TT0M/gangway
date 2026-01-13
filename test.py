import time

from modules.ws2805_controller import RGBCCT, WS2805Controller


def run_led_cycle(device: WS2805Controller) -> None:
    for x in range(device.strip.size):
        device.fill(RGBCCT())
        device.show()

        for i in range(-5, 5):
            if 0 > i + x or i + x > device.strip.size:
                continue

            device.set_color(x + i, RGBCCT(cw=255, ww=255))

        device.show()
        time.sleep(0.01)


def run_led_cycle_strobo(device: WS2805Controller) -> None:
    colors = [
        RGBCCT(r=255),
    ]

    while True:
        for color in colors:
            device.clear()
            device.fill(color)
            device.show()


if __name__ == "__main__":
    device = WS2805Controller(count=150)

    while True:
        run_led_cycle_strobo(device)
