import time
import logging
from string import Template
from gpiozero import GPIOZeroError
from power_status import PowerStatus
from libs.custom_gpio_devices import LowTriggerSwitch


class PowerStateController:
    """
    Control Power Operations for a connected PC via Raspberry Pi
    Logs commands and live power state
    """

    _controller_log = logging.getLogger(__name__)
    _logfile_name = "../config/log/{0}.log".format(__name__)

    _status_filename = "../config/power_status"
    _buzzer_filename = "../config/buzzer_code"

    _message_template = "{\"command_status\"=\"${command_status}\",\"message\"=\"${message}\"}"

    _power_gpio = None
    _reboot_gpio = None

    _power_switch = None
    _reboot_switch = None

    _reboot_duration_seconds = 2
    _power_on_duration_seconds = 2
    _power_off_duration_seconds = 4

    def __init__(self, power_gpio, reboot_gpio, log_level=logging.DEBUG):
        """
        Initialize PowerStateController object and prepare output devices

        :param power_gpio: GPIO ID to be used for power switch
        :type power_gpio: int
        :param reboot_gpio: GPIO ID to be used for reboot switch
        :type reboot_gpio: int
        :param log_level: desired log level for
        """
        self._start_logging(log_level)
        self._power_gpio = power_gpio
        self._reboot_gpio = reboot_gpio
        self._setup_output_pins()

    def _start_logging(self, log_level):
        log_formatter = logging.Formatter(fmt="[%(asctime)s] <%(levelname)s> %(name)s: %(message)s",
                                          datefmt="%Y%m%d %H:%M:%S")
        with open(self._logfile_name, "a") as controller_logfile:
            controller_logfile.write("[START NEW RUNTIME LOG]\n")
        controller_log_filehandler = logging.FileHandler(self._logfile_name)
        controller_log_filehandler.setFormatter(log_formatter)
        self._controller_log.addHandler(controller_log_filehandler)
        self._controller_log.setLevel(log_level)

    # PowerStateController Private Methods
    def _setup_output_pins(self):
        """
        Attempt to set GPIO pins to ready for use (HIGH)
        Intended to be treated as private

        :return: True if successful, False if failed for any reason
        :rtype: Boolean
        """
        # Attempt to clear GPIO devices in case last shutdown not clean
        try:
            self._power_switch.close()
            self._reboot_switch.close()
            self._controller_log.debug("Closed Output Devices and Releasing GPIO")
        except (GPIOZeroError, AttributeError) as error:
            self._controller_log.debug("{0}: Did not need to clear output devices before continuing".format(error))

        try:
            self._power_switch = LowTriggerSwitch(name="Power Switch", pin=self._power_gpio)
            self._reboot_switch = LowTriggerSwitch(name="Reboot Switch", pin=self._reboot_gpio)
            self._controller_log.info("Successfully setup PowerStateController output devices")
            return True
        except GPIOZeroError as gpio_error:
            self._controller_log.critical("{0}: Unable to setup output pins as devices".format(gpio_error))
            return False

    def _hold_low_switch_on(self, low_switch, duration):
        """
        Hold a requested low trigger device in the LOW state for a given duration

        :param low_switch: GPIO Switch to hold on
        :type low_switch: LowTriggerSwitch
        :param duration: Duration in seconds
        :type duration: float
        :return: True if successful, False if failed for any reason
        :rtype: Boolean
        """
        self._controller_log.debug("Attempting hold {0} on for {1} seconds".format(low_switch.name, duration))
        try:
            low_switch.close_circuit()
            time.sleep(duration)
            low_switch.open_circuit()
            return True
        except (GPIOZeroError, AttributeError) as device_exception:
            self._controller_log.error("{0}: Unable to hold {1} on".format(device_exception, low_switch.name))
            return False

    def _hold_low_switch_off(self, low_switch, duration):
        """
        Hold a requested low trigger device in the HIGH state for a given duration

        :param low_switch: GPIO Switch to hold on
        :type low_switch: LowTriggerSwitch
        :param duration: Duration in seconds
        :type duration: float
        :return: True if successful, False if failed for any reason
        :rtype: Boolean
        """
        self._controller_log.debug("Attempting hold {0} on for {1} seconds".format(low_switch.name, duration))
        try:
            low_switch.close_circuit()
            time.sleep(duration)
            low_switch.open_circuit()
            return True
        except (GPIOZeroError, AttributeError) as device_exception:
            self._controller_log.error("{0}: Unable to hold {1} on".format(device_exception, low_switch.name))
            return False

    def _read_power_status(self):
        """
        Read last value written to status file
        """
        with open(self._status_filename, 'r') as status_file:
            return int(status_file.read())

    def _cleanup_output_devices(self):
        """
        Utility function for clean shutdown and release of gpio resources
        Frees Power Switch and Reboot Switch Resources

        :return:  True if successful, False if failed for any reason
        :rtype: boolean
        """
        try:
            self._power_switch.close()
            self._reboot_switch.close()
            self._controller_log.info("Successfully shutdown/ closed output pin devices")
            return True
        except GPIOZeroError as gpio_error:
            self._controller_log.critical("{0}: Unable to shutdown/close output pin devices".format(gpio_error))
        return True

    # PowerStateController public methods
    def reboot(self):
        """
        Use power switch bypass to reboot connected target machine
        """
        last_power_status = self._read_power_status()
        last_status_string = PowerStatus.status_string[last_power_status]
        if last_power_status == PowerStatus.POWERED_ON:
            self._controller_log.debug("Attempting to send Reboot Command")
            if self._hold_low_switch_on(self._reboot_switch, self._reboot_duration_seconds):
                self._controller_log.info("Reboot Command Sent")
                return_message = Template(self._message_template).substitute(
                    command_status="SUCCESS",
                    message="Reboot Command Sent")
            else:
                self._controller_log.error("Reboot Command NOT Sent Due to Some Error")
                return_message = Template(self._message_template).substitute(
                    command_status="ERROR",
                    message="Reboot Command NOT Sent Due to Some Error")
        else:
            self._controller_log.info("Reboot Command NOT Sent: PC Power State {0}".format(last_status_string))
            return_message = Template(self._message_template).substitute(
                command_status="ERROR",
                message="Reboot Command NOT Sent: PC Power State {0}".format(last_status_string))
        return return_message

    def power_on(self):
        """
        Use power switch bypass to power on connected target machine
        """
        last_power_status = self._read_power_status()
        last_status_string = PowerStatus.status_string[last_power_status]
        if last_power_status == PowerStatus.POWERED_OFF:
            self._controller_log.debug("Attempting to Send Power On Command")
            if self._hold_low_switch_on(self._power_switch, self._power_on_duration_seconds):
                self._controller_log.info("Power On Command Sent")
                return_message = Template(self._message_template).substitute(
                    command_status="SUCCESS",
                    message="Power On Command Sent")
            else:
                self._controller_log.error("Power On Command NOT Sent Due to Some Error")
                return_message = Template(self._message_template).substitute(
                    command_status="ERROR",
                    message="Power On Command NOT Sent Due to Some Error")
        else:
            self._controller_log.info("Power On Command NOT Sent: PC Power State {0}".format(last_status_string))
            return_message = Template(self._message_template).substitute(
                command_status="ERROR",
                message="Power On Command NOT Sent: PC Power State {0}".format(last_status_string))
        return return_message

    def power_off(self):
        """
        Use power switch bypass to power on connected target machine
        """
        last_power_status = self._read_power_status()
        last_status_string = PowerStatus.status_string[last_power_status]
        if last_power_status == PowerStatus.POWERED_ON:
            self._controller_log.debug("Attempting to Send Power Off Command")
            if self._hold_low_switch_on(self._power_switch, self._power_off_duration_seconds):
                self._controller_log.info("Power Off Command Sent")
                return_message = Template(self._message_template).substitute(
                    command_status="SUCCESS",
                    message="Power Off Command Sent")
            else:
                self._controller_log.error("Power Off Command NOT Sent Due to Some Error")
                return_message = Template(self._message_template).substitute(
                    command_status="ERROR",
                    message="Power Off Command NOT Sent Due to Some Error")
        else:
            self._controller_log.info("Power Off Command NOT Sent: PC Power State {0}".format(last_status_string))
            return_message = Template(self._message_template).substitute(
                command_status="ERROR",
                message="Power Off Command NOT Sent: PC Power State {0}".format(last_status_string))
        return return_message

    def shutdown_power_controller(self):
        self._cleanup_output_devices()
