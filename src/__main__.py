import os
import time
import logging
import multiprocessing as mp
from configparser import ConfigParser
from pc_power_controller import PowerStateController
from pc_power_status_reader import PowerStatusReader

run_log = logging.getLogger(__name__)
log_formatter = logging.Formatter(fmt="[%(asctime)s] <%(levelname)s> %(name)s: %(message)s",
                                  datefmt="%Y%m%d %H:%M:%S")

logfile_name = "../config/log/{0}.log".format("run")
open(logfile_name, "a")
run_logfile = logging.FileHandler(logfile_name)
run_logfile.setFormatter(log_formatter)
run_log.addHandler(run_logfile)
run_log.setLevel(logging.INFO)

power_gpio = 0
reboot_gpio = 0
buzzer_gpio = 0
status_gpio = 0


def load_gpio_configs():
    gpio_config_file = "../config/gpio.conf"
    gpio_config = ConfigParser()
    gpio_config.read(gpio_config_file)
    # Load Output Pin Identities
    global power_gpio
    power_gpio = int(gpio_config["OUTPUT_PINS"]["power_switch_gpio"])
    run_log.debug("Loaded Power GPIO = {0} from \'{1}\'".format(str(power_gpio), gpio_config_file))
    global reboot_gpio
    reboot_gpio = int(gpio_config["OUTPUT_PINS"]["reboot_switch_gpio"])
    run_log.debug("Loaded Reboot GPIO = {0} from \'{1}\'".format(str(reboot_gpio), gpio_config_file))
    global status_gpio
    status_gpio = int(gpio_config["INPUT_PINS"]["power_status_gpio"])
    run_log.debug("Loaded Status GPIO = {0} from \'{1}\'".format(str(status_gpio), gpio_config_file))
    global buzzer_gpio
    buzzer_gpio = int(gpio_config["INPUT_PINS"]["motherboard_buzzer_gpio"])
    run_log.debug("Loaded Buzzer GPIO = {0} from \'{1}\'".format(str(buzzer_gpio), gpio_config_file))


if __name__ == '__main__':

    load_gpio_configs()
    run_log.info("Loaded GPIO Configs")
    state_reader = PowerStatusReader(status_gpio, buzzer_gpio)

    time.sleep(1)

    state_controller = PowerStateController(power_gpio, reboot_gpio)

    input("turn on?\n")
    print(state_controller.power_on())
    input("turn off?\n")
    print(state_controller.power_off())
    input("reboot?\n")
    print(state_controller.reboot())

    input("end?\n")
    state_controller.shutdown_power_controller()
    state_reader.shutdown_status_reader()


