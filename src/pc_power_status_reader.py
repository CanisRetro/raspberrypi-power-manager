import os
import time
import logging
import multiprocessing as mp
from gpiozero import GPIOZeroError
from power_status import PowerStatus
from libs.custom_gpio_devices import BasicHighSensor


class PowerStatusReader():
    """
    Watch Input pins for changes and record/ report them
    Runs in multiple separate listener threads
    """
    _reader_log = logging.getLogger(__name__)
    _logfile_name = "../config/log/{0}.log".format(__name__)

    _status_gpio = None
    _buzzer_gpio = None

    _status_sensor = None
    _buzzer_sensor = None

    _status_filename = "../config/power_status"
    _buzzer_filename = "../config/debug_buzzer"

    _listener_pool = mp.Pool(processes=2)
    _listeners = []

    def __init__(self, status_gpio, buzzer_gpio, log_level=logging.INFO):
        """
        Initialize PowerStateReader object and prepare listening devices

        :param status_gpio: GPIO ID to be used to sense power state
        :type status_gpio: int
        :param buzzer_gpio: GPIO ID to be used to sense startup/boot buzzer
        :type buzzer_gpio: int
        """
        self._start_logging(log_level)
        self._status_gpio = status_gpio
        self._buzzer_gpio = buzzer_gpio
        self._setup_input_pins()
        self._start_listener_processes()

    def _start_logging(self, log_level=logging.INFO):
        """
        Start logging to a designated power state reader log file at the desired log level
        """
        log_formatter = logging.Formatter(fmt="[%(asctime)s] <%(levelname)s> %(name)s: %(message)s",
                                          datefmt="%Y%m%d %H:%M:%S")
        with open(self._logfile_name, "a") as reader_logfile:
            reader_logfile.write("[START NEW RUNTIME LOG]\n")
        reader_log_filehandler = logging.FileHandler(self._logfile_name)
        reader_log_filehandler.setFormatter(log_formatter)
        self._reader_log.addHandler(reader_log_filehandler)
        self._reader_log.setLevel(log_level)

    def _start_listener_processes(self):
        """
        Cleanly Start Required Background Listener Processes
        """
        # Power Status Listener
        power_status_listener = mp.Process(name="power_status_listener",
                                           target=self._start_power_status_listener)
        power_status_listener.start()
        self._listeners.append(power_status_listener)
        # Debug Buzzer Listener
        buzzer_listener = mp.Process(name="buzzer_listener", target=self._start_buzzer_listener)
        buzzer_listener.start()
        self._listeners.append(buzzer_listener)

    # PowerStateHandler Private Methods
    def _setup_input_pins(self):
        """
        Attempt to set GPIO or board pins to input mode
        Intended to be treated as private

        :return: True if successful, False if failed for any reason
        :rtype: Boolean

        """
        # Set up Power hookup pins as input pulled down
        try:
            self._status_sensor = BasicHighSensor(name="Power Status Sensor", pin=self._status_gpio)
            self._buzzer_sensor = BasicHighSensor(name="Buzzer Sensor", pin=self._buzzer_gpio)
            self._reader_log.debug("Successfully setup input pins as devices")
            return True
        except GPIOZeroError as gpio_error:
            self._reader_log.critical("{0}: Unable to setup input pins as devices".format(gpio_error))
            return False

    def _listen_for_power_status_change(self):
        self._reader_log.info("Power Status Listening Process Starting")
        while True:
            current_status = self._read_power_status()
            with open(self._status_filename, 'r') as status_file:
                last_status = int(status_file.readline())
            if not current_status == last_status:
                with open(self._status_filename, 'w') as status_file:
                    status_file.write(str(current_status))
                self._reader_log.info("Power Status changed from {0} to {1}".format(
                    PowerStatus.status_string[last_status],
                    PowerStatus.status_string[current_status]))
            time.sleep(0.01)

    def _read_power_status(self):
        """
        Read the GPIO Pin Value of the Status Sensor
        """
        try:
            if self._status_sensor.is_active:
                return PowerStatus.POWERED_ON
            else:
                return PowerStatus.POWERED_OFF
        except GPIOZeroError as gpio_error:
            self._reader_log.error("{0}: Unable to read power status".format(gpio_error))
            return PowerStatus.UNKNOWN

    def _listen_for_buzzer_start(self):
        """"""
        self._reader_log.info("Buzzer Listening Thread Starting")
        while True:
            self._buzzer_sensor.when_activated = lambda: self._count_buzz()
            time.sleep(0.01)

    def _count_buzz(self):
        """"""
        print("BUZZ")
        with open(self._buzzer_filename, 'r') as buzzer_file:
            buzz_count = int(buzzer_file.readline())
        with open(self._buzzer_filename, 'w') as buzzer_file:
            buzzer_file.write(str(buzz_count + 1))

    def _cleanup_input_devices(self):
        """
        Utility function for release of gpio resources
        Frees Status Sensor and Buzzer Sensor Resources

        :return:  True if successful, False if failed for any reason
        :rtype: boolean
        """
        try:
            self._status_sensor.close()
            self._buzzer_sensor.close()
            self._reader_log.info("Successfully shutdown/ closed input pin devices")
            return True
        except GPIOZeroError as gpio_error:
            self._reader_log.critical("{0}: Unable to shutdown/close input pin devices".format(gpio_error))
            return False

    def _delete_status_file(self):
        """
        Delete the power_status file uses to share power status between threads
        """
        try:
            if os.path.exists(self._status_filename):
                os.remove(self._status_filename)
                self._reader_log.debug("Successfully Deleted power_status file")
            else:
                self._reader_log.debug("power_status file not present")
        except OSError as os_error:
            self._reader_log.critical("{0}: Unable to delete power_status file".format(os_error))

    def _delete_buzzer_file(self):
        """
        Delete the debug_buzzer file uses to share power status between threads
        """
        try:
            if os.path.exists(self._status_filename):
                os.remove(self._status_filename)
                self._reader_log.debug("Successfully Deleted power_status file")
            else:
                self._reader_log.debug("power_status file not present")
        except OSError as os_error:
            self._reader_log.critical("{0}: Unable to delete power_status file".format(os_error))

    def _kill_listener_processes(self):
        """
        Kill ongoing listener processes
        """
        for process in self._listeners:
            # Terminate Listener Objects
            process.terminate()

    def _start_power_status_listener(self):
        """

        """
        with open(self._status_filename, 'w') as status_file:
            status_file.write(str(PowerStatus.UNKNOWN))
        self._reader_log.info("Created Power Status Tracking File")

        self._listen_for_power_status_change()

    def _start_buzzer_listener(self):
        """

        """
        with open(self._buzzer_filename, 'w') as buzzer_file:
            buzzer_file.write("0")
        self._reader_log.info("Created Debug Buzzer Tracking File")
        self._listen_for_buzzer_start()

    def shutdown_status_reader(self):
        """
        Utility function to cleanly shut-down PowerStatusReader
        """
        self._kill_listener_processes()
        self._delete_status_file()
        self._cleanup_input_devices()


