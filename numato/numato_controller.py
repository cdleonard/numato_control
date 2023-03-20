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
import telnetlib

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


@enum.unique
class GPIOState(enum.Enum):
    GPIO_LOW = (0, 'clear')
    GPIO_HIGH = (1, 'set')
    GPIO_ERROR = (2, 'error')

    @property
    def numeric(self):
        (numeric, _) = self.value
        return numeric

    @property
    def text(self):
        (_, text) = self.value
        return text


class numato_controller(object):

    def __init__(self, port='/dev/ttyACM0', address=None, method='serial'):
        self.method = method
        
        if method == 'serial':
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
        elif method == 'telnet':
            self.relay_telnet = telnetlib.Telnet(address)

            user = "admin"
            password = "admin"
            self.relay_telnet.read_until(b"login")
            self.relay_telnet.write(user.encode('ascii') + b"\r\n")

            # Wait for password prompt and enter password when prompted by device
            self.relay_telnet.read_until(b"Password: ")
            self.relay_telnet.write(password.encode('ascii') + b"\r\n")

            # Wait for device response
            log_result = self.relay_telnet.read_until(b"successfully\r\n")
            #print(log_result)
            self.relay_telnet.read_until(b">")

    def clear_and_reset_serial_port(self):
        """Clear UART before resuming activity.
        serial_port: A valid serial.Serial() object
        """
        self.relay_serial.reset_output_buffer()
        self.relay_serial.reset_input_buffer()
        self.relay_serial.write("\r".encode())
        self.relay_serial.read_until(terminator=b">")

    def get_board_version(self):

        if self.method == 'serial':
            self.clear_and_reset_serial_port()
            write = "\rver\r".encode()
            self.relay_serial.write(write)
            response = self.relay_serial.read_until(terminator=b">")
        elif self.method == 'telnet':
            write = "ver\r\n".encode()
            self.relay_telnet.write(write)
            response = self.relay_telnet.read_until(b">", timeout=1)
            response = response.decode()

        # Parse the on/off string from the response
        parsed = response[5:].partition('\n\r')[0]
        return parsed

    def write_relay_state(self, relay_index, new_state):
        """ Write new relay state (on or off).

        :param relay_index: Single-character value of relay (0, 1, A, etc)
        :type relay_index: :class:`string`
        :param new_state: Desired new state of relay
        :type new_state: :class:`RelayState`, boolean, int or a string containing "ON / OFF" or "TRUE / FALSE"
        :return: None
        """
        if len(str(relay_index)) != 1:
            raise ValueError("Index {} not supported.".format(relay_index))

        if isinstance(new_state, str):
            new_state = new_state.upper()
            if new_state in ["ON", "TRUE"]:
                new_state = RelayState.RELAY_ON
            else:
                new_state = RelayState.RELAY_OFF

        if isinstance(new_state, float):
            new_state = int(new_state)

        if isinstance(new_state, int):
            if new_state:
                new_state = RelayState.RELAY_ON
            else:
                new_state = RelayState.RELAY_OFF

        if not isinstance(new_state, RelayState):
            raise ValueError("Unknown new relay state.")

        if self.method == 'serial':
            self.clear_and_reset_serial_port()
            self.relay_serial.write(
                "relay {} {}\r".format(new_state.text, relay_index).encode())
        elif self.method == 'telnet':
            write = "relay {} {}\r\n".format(new_state.text, relay_index).encode()
            self.relay_telnet.write(write)
            response = self.relay_telnet.read_until(match=b">", timeout=1)

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

        if self.method == 'serial':
            self.clear_and_reset_serial_port()
            self.relay_serial.write(
                "relay read {}\r".format(relay_index).encode())
            response = self.relay_serial.read_until(terminator=b">")
        elif self.method == 'telnet':
            write = "relay read {}\r\n".format(relay_index).encode()
            self.relay_telnet.write(write)
            response = self.relay_telnet.read_until(b">", timeout=1)
            response.decode()
            #print(response)

        if b"off" in response:
            return RelayState.RELAY_OFF
        elif b"on" in response:
            return RelayState.RELAY_ON
        else:
            return RelayState.RELAY_ERROR

    def write_gpio_state(self, gpio_index, new_state):
        """ Write new relay state (on or off).

        :param gpio_index: Single-character value of gpio (0, 1, A, etc)
        :type gpio_index: :class:`string`
        :param new_state: Desired new state of gpio pin
        :type new_state: :class:`RelayState`, boolean, int or a string containing "ON / OFF" or "TRUE / FALSE"
        :return: None
        """
        if len(str(gpio_index)) != 1:
            raise ValueError("Index {} not supported.".format(gpio_index))

        if isinstance(new_state, str):
            new_state = new_state.upper()
            if new_state in ["ON", "TRUE", "HIGH"]:
                new_state = GPIOState.GPIO_HIGH
            else:
                new_state = GPIOState.GPIO_LOW

        if isinstance(new_state, float):
            new_state = int(new_state)

        if isinstance(new_state, int):
            if new_state:
                new_state = GPIOState.GPIO_HIGH
            else:
                new_state = GPIOState.GPIO_LOW

        if not isinstance(new_state, GPIOState):
            raise ValueError("Unknown new gpio state.")

        self.clear_and_reset_serial_port()
        self.relay_serial.write(
            "gpio {} {}\r".format(new_state.text, gpio_index).encode())

    def get_gpio_state(self, gpio_index):
        """ Read and return the state of the relay (on or off)

        :param gpio_index: Single-character index of gpio (0, 1, A, etc)
        :type gpio_index: :class:`string`
        :return: relay state
        :rtype: :class:`GPIOState`
        """
        if len(str(gpio_index)) != 1:
            raise ValueError("Index {} not supported.".format(gpio_index))

        self.clear_and_reset_serial_port()
        self.relay_serial.write(
            "gpio read {}\r".format(gpio_index).encode())
        response = self.relay_serial.read_until(terminator=b">")

        # Trying to handle both combinations of \n\r and \r\n in case different products aren't consistent
        if b"\r0\n" in response or b"\n0\r" in response:
            return GPIOState.GPIO_LOW
        elif b"\r1\n" in response or b"\n1\r" in response:
            return GPIOState.GPIO_HIGH
        else:
            return GPIOState.GPIO_ERROR

    def read_adc(self, gpio_index):
        """ Read and return the state of the relay (on or off)

        :param gpio_index: Single-character index of gpio (0, 1, A, etc)
        :type gpio_index: :class:`string`
        :return: relay state
        :rtype: :class:`GPIOState`
        """
        if len(str(gpio_index)) != 1:
            raise ValueError("Index {} not supported.".format(gpio_index))

        self.clear_and_reset_serial_port()
        self.relay_serial.write(
            "adc read {}\r".format(gpio_index).encode())
        response = self.relay_serial.read_until(terminator=b">")

        try:
            response.decode('utf-8')
            response = response.split(b"\n")
            return int(response[-2])
        except Exception as e:
            print(e)
            return -1

    def __exit__(self, type, value, traceback):
        self.relay_serial.close()

    def __enter__(self):
        return self
