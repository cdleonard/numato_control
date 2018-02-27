import nose.tools
from numato import numato_controller as module


class TestModule(object):
    def test_relay__instantiate_new_relay_valid_port__no_error_raised(self):
        module.numato_controller(port=None)

    @nose.tools.raises(ValueError)
    def test_relay__instantiate_new_relay_invalid_port__error_raised(self):
        module.numato_controller(port='/dev/ttyPORTOCALL')

    def test_relay__write_valid_relay__no_error(self):
        device = module.numato_controller(port='loop://')
        device.write_relay_state(0, module.RelayState.RELAY_OFF)
        device.write_relay_state(0, module.RelayState.RELAY_ON)
        device.write_relay_state(1, module.RelayState.RELAY_OFF)
        device.write_relay_state(1, module.RelayState.RELAY_ON)
        device.write_relay_state('A', module.RelayState.RELAY_OFF)
        device.write_relay_state('A', module.RelayState.RELAY_ON)

    @nose.tools.raises(ValueError)
    def test_relay__write_invalid_relay__error_raised(self):
        device = module.numato_controller(port='loop://')
        device.write_relay_state(56, module.RelayState.RELAY_OFF)

    @nose.tools.raises(ValueError)
    def test_relay__write_invalid_new_state__error_raised(self):
        device = module.numato_controller(port='loop://')
        device.write_relay_state(2, "ON!")

    def test_relay__read_valid_relay_bad_response__error_type(self):
        device = module.numato_controller(port='loop://')

        # Errors because loopback module just feeds RX<->TX
        nose.tools.assert_equal(
            device.get_relay_state(0),
            module.RelayState.RELAY_ERROR)

    @nose.tools.raises(ValueError)
    def test_relay__read_invalid_relay__error_raised(self):
        device = module.numato_controller(port='loop://')
        device.get_relay_state(56)
