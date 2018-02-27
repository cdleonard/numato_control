# numato_control
Python control library for Numato relay hardware.

Originally built as a basic monitor and control tool for the
[Numato 2 Channel USB Relay Module](https://docs.numato.com/doc/2-channel-usb-relay-module/), it should be usable on almost any Numato USB device that uses
the same serial command scheme.

Currently supports retrieving status and writing to any relay on the device.

** Supports Python versions between 2.7.x and 3.4 **
(Due to use of the `enum34` library)

Example Use:

```

# Defaults to port /dev/ttyACM0
from numato import numato_controller

device = numato_controller()

device.get_relay_state(0)  # Retrieve state of relay index 0
<RelayState.RELAY_OFF: (0, 'off')>

device.turn_on_relay(0)  # Turn on relay index 0

device.get_relay_state(0)
<RelayState.RELAY_ON: (1, 'on')>
```

To execute the tests, from the repository root, use `nosetests`:

```

~$ nosetests test/test_numato_controller.py
.......
----------------------------------------------------------------------
Ran 7 tests in 0.805s

OK

```
