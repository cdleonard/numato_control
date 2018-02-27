""" Numato Controller: Monitor/Control Relays on Numato Modules

This module provides an interface to control the relay functionality of Numato
devices which include relays
(e.g. https://numato.com/product/2-channel-usb-relay-module).

This is intended for programmatic use, and removes the need to handle low-level
serial port or relay commands.  It should work with any Numato USB controller

This tool is set to default to the serial port '/dev/ttyACM0'.  Simply supply
the appropriate port name when creating an instance of `numato_controller` if
necessary, e.g.:

    `ctrl = numato_controller('/dev/tty.usbmodem141141')`

Future development opportunities include:

    * Read analog inputs
    * Read/Set GPIO
"""

import serial
import logging
import enum

logger = logging.getLogger(__name__)


@enum.unique
class RelayState(enum.Enum):
    RELAY_OFF = (0, 'off')
    RELAY_ON = (1, 'on')
    RELAY_ERROR = (2, 'error')

    @property
    def numeric(self):
        (numeric, _) = self.value
        return numeric

    @property
    def text(self):
        (_, text) = self.value
        return text


class numato_controller(object):

    def __init__(self, port='/dev/ttyACM0'):
        try:
            if port != 'loop://':
                self.relay_serial = serial.Serial(
                    port=port,
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=0.1,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False)
            else:
                # loopback port, for testing.
                self.relay_serial = serial.serial_for_url(
                    'loop://',
                    timeout=0.1)
        except:
            raise ValueError("Serial port {} is already in use".format(port))

    def clear_and_reset_serial_port(self):
        """Clear UART before resuming activity.
        serial_port: A valid serial.Serial() object
        """
        self.relay_serial.reset_output_buffer()
        self.relay_serial.reset_input_buffer()
        self.relay_serial.read(1000)

    def get_board_version(self):
        self.clear_and_reset_serial_port()
        self.relay_serial.write("\rver\r".encode())
        response = self.relay_serial.read(100)

        # Parse the on/off string from the response
        parsed = response[5:].partition('\n\r')[0]
        return parsed

    def write_relay_state(self, relay_index, new_state):
        """ Write new relay state (on or off).

        :param relay_index: Integer value of relay (0 or 1) to write
        :type relay_index: :class:`int`
        :param new_state: Desired new state of relay
        :type new_state: :class:`RelayState`
        :return: None
        """
        if len(str(relay_index)) != 1:
            raise ValueError("Index {} not supported.".format(relay_index))

        if not isinstance(new_state, RelayState):
            raise ValueError("Unknown new relay state.")

        self.clear_and_reset_serial_port()
        self.relay_serial.write(
            "\rrelay {} {}\r".format(new_state.text, relay_index).encode())

    def turn_on_relay(self, relay_index):
        """ Convenience function to turn on a relay index.

        :param relay_index: Single-character value of relay (0, 1, A, etc)
        :type relay_index: :class:`string`
        """

        self.write_relay_state(relay_index, RelayState.RELAY_ON)

    def turn_off_relay(self, relay_index):
        """ Convenience function to turn off a relay index.

        :param relay_index: Single-character index of relay (0, 1, A, etc)
        :type relay_index: :class:`string`
        """

        self.write_relay_state(relay_index, RelayState.RELAY_OFF)

    def get_relay_state(self, relay_index):
        """ Read and return the state of the relay (on or off)

        :param relay_index: Single-character index of relay (0, 1, A, etc) 
        :type relay_index: :class:`string`
        :return: relay state
        :rtype: :class:`RelayState`
        """
        if len(str(relay_index)) != 1:
            raise ValueError("Index {} not supported.".format(relay_index))

        self.clear_and_reset_serial_port()
        self.relay_serial.write(
            "\rrelay read {}\r".format(relay_index).encode())
        response = self.relay_serial.read(100)

        # Parse the on/off string from the response
        parsed = response[17:].partition('\n\r')[0]
        if parsed == 'off':
            return RelayState.RELAY_OFF
        elif parsed == 'on':
            return RelayState.RELAY_ON
        else:
            return RelayState.RELAY_ERROR
