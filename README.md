# numato_control
Python control library for Numato relay hardware.

Originally built as a basic monitor and control tool for the
(Numato 2 Channel USB Relay Module)[https://docs.numato.com/doc/2-channel-usb-relay-module/], it should be 

Currently supports retrieving status and writing to any relay on the device.

Example Use:

```

# Defaults to port /dev/ttyACM0
from numato_controller import numato_controller

device = numato_controller()

device.get_relay_state(0)  # Retrieve state of relay index 0
<RelayState.RELAY_OFF: (0, 'off')>

device.turn_on_relay(0)  # Turn on relay index 0

device.get_relay_state(0)
<RelayState.RELAY_ON: (1, 'on')>
```
