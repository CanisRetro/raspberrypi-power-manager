import os
import logging
from configparser import ConfigParser
from src.pc_power_controller import PowerStateController, PowerStatusReader

# Configure Default Logging Mode
logfile_name = "./config/log/{0}.log".format("run")
# open(logfile_name, "a")
logging.basicConfig(filename=logfile_name,
                    format="[%(asctime)s] <%(levelname)s> %(name)s: %(message)s",
                    datefmt="%Y%m%d %H:%M:%S",
                    level=logging.DEBUG)
log = logging.getLogger(__name__)

power_gpio = None
reboot_gpio = None
buzzer_gpio = None
status_gpio = None


def load_gpio_configs():
    gpio_config_file = "./config/gpio.conf"
    gpio_config = ConfigParser()
    gpio_config.read(gpio_config_file)
    # Load Output Pin Identities
    global power_gpio
    power_gpio = int(gpio_config["OUTPUT_PINS"]["power_switch_gpio"])
    log.debug("Loaded Power GPIO = {0} from \'{1}\'".format(str(power_gpio), gpio_config_file))
    global reboot_gpio
    reboot_gpio = int(gpio_config["OUTPUT_PINS"]["reboot_switch_gpio"])
    log.debug("Loaded Reboot GPIO = {0} from \'{1}\'".format(str(reboot_gpio), gpio_config_file))
    global status_gpio
    status_gpio = int(gpio_config["INPUT_PINS"]["power_status_gpio"])
    log.debug("Loaded Status GPIO = {0} from \'{1}\'".format(str(status_gpio), gpio_config_file))
    global buzzer_gpio
    buzzer_gpio = int(gpio_config["INPUT_PINS"]["motherboard_buzzer_gpio"])
    log.debug("Loaded Buzzer GPIO = {0} from \'{1}\'".format(str(buzzer_gpio), gpio_config_file))


def __main__():
    load_gpio_configs()
    state_controller = PowerStateController(power_gpio, reboot_gpio)
    state_reader = PowerStatusReader(status_gpio, buzzer_gpio)
    input("turn on?\n")
    state_controller.power_on()
    input("turn off?\n")
    state_controller.power_off()
    input("reboot?\n")
    state_controller.reboot()

    input("end?\n")
    state_controller.cleanup_output_devices()
    state_reader.cleanup_input_devices()


__main__()

