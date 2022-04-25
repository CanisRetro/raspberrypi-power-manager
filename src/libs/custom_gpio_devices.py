from gpiozero import DigitalOutputDevice, DigitalInputDevice


# Custom Output Devices
class CustomOutputDevice(DigitalOutputDevice):
    """ Subclass of DigitalOutputDevice that adds a \'name\' parameter
        for clarity, readability, and logging

    :param name:
        String Name value of the Output Device for identification
    :type name: str
    """

    # New Custom Name Value
    name = ""

    # override
    def __init__(self, name="", pin=None, active_high=True, initial_value=False, pin_factory=None):
        self.name = name
        super().__init__(pin=pin, active_high=active_high, initial_value=initial_value, pin_factory=pin_factory)


class HighTriggerSwitch(CustomOutputDevice):
    """ Subclass of CustomOutputDevice For use with
    HIGH-Trigger Relays and Digital Switches

    GPIO Pin values will be set High/1/True when circuit is set to closed
    """

    # override
    def __init__(self, name="", pin=None):
        super().__init__(name=name, pin=pin, active_high=True, initial_value=False)

    def close_circuit(self):
        """ Set Switch or Relay pin value to HIGH,
        closing the connected circuit"""

        super().on()

    def open_circuit(self):
        """ Set Switch or Relay pin value to LOW,
        opening the connected circuit"""
        super().off()


class LowTriggerSwitch(CustomOutputDevice):
    """ Subclass of CustomOutputDevice for use with
    LOW-Trigger Relays and Digital Switches

    GPIO Pin values will be set Low/0/False when circuit is set to closed
    """

    def __init__(self, name="", pin=None):
        super().__init__(name=name, pin=pin, active_high=False, initial_value=False)

    def close_circuit(self):
        """ Set Switch or Relay pin value to LOW,
        closing the connected circuit"""
        super().on()

    def open_circuit(self):
        """ Set Switch or Relay pin value to HIGH,
        opening the connected circuit
        """
        super().off()


# Custom Input Devices
class CustomInputDevice(DigitalInputDevice):
    """ Subclass of DigitalInputDevice that adds a \'name\' parameter
        for clarity, readability, and logging

    :param name:
        String Name value of the Input Device for identification
    :type name: str
    """
    # New Custom Name Value
    name = ""

    # override
    def __init__(self, name="", pin=None, pull_up=False, active_state=None, bounce_time=None, pin_factory=None):
        self.name = name
        super().__init__(pin=pin, pull_up=pull_up, active_state=active_state,
                         bounce_time=bounce_time, pin_factory=pin_factory)


class BasicHighSensor(CustomInputDevice):
    """ Subclass of CustomInputDevice for use with basic 3.3 volt input HI/LO values
    """

    def __init__(self, name="", pin=None):
        super().__init__(name=name, pin=pin, pull_up=False, active_state=None,
                         bounce_time=None, pin_factory=None)
