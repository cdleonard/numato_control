# numato_control

Python control library for Numato relay hardware.

Originally built as a basic monitor and control tool for the
[Numato 2 Channel USB Relay Module](https://docs.numato.com/doc/2-channel-usb-relay-module/), it should be usable on almost any Numato USB device that uses
the same serial command scheme.

Currently supports retrieving status and writing to any relay on the device.

**Supports Python versions between 2.7.x and 3.4**
(Due to use of the `enum34` library)

Later versions of Python should work with the built in enums.

Example Use:

```

# Defaults to port /dev/ttyACM0
from numato.numato_controller import numato_controller

device = numato_controller()

device.get_relay_state(0)  # Retrieve state of relay index 0
<RelayState.RELAY_OFF: (0, 'off')>

device.turn_on_relay(0)  # Turn on relay index 0
device.write_relay_state(relay_index=1, new_state=0)  # Turning off relay index 1

device.get_relay_state(0)
<RelayState.RELAY_ON: (1, 'on')>

device.write_gpio_state(gpio_index=0, new_state=1) # Setting (high) GPIO index 0
device.write_gpio_state(gpio_index=1, new_state=0) # Clearing (low) GPIO index 1

device.get_gpio_state(gpio_index=1)
<GPIOState.GPIO_LOW: (0, 'clear')>

device.read_adc(gpio_index=0)
1023

```

## Testing

To execute the tests, from the repository root, use `python -m unittest`:

```

~$ python -m unittest
.......
----------------------------------------------------------------------
Ran 7 tests in 0.805s

```

It is also possible to use other tools such as
[pytest](https://docs.pytest.org/en/latest/) and
[nose2](https://docs.nose2.io/en/latest/)
