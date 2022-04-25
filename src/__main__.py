import sys
import time
import logging
from configparser import ConfigParser
from pc_power_controller import PowerStateController
from pc_power_status_reader import PowerStatusReader


run_log = logging.getLogger(__name__)
log_formatter = logging.Formatter(fmt="[%(asctime)s] <%(levelname)s> %(name)s: %(message)s",
                                      datefmt="%Y%m%d %H:%M:%S")
logfile_name = "./config/log/{0}.log".format("run")
open(logfile_name, "a")
run_logfile = logging.FileHandler(logfile_name)
run_logfile.setFormatter(log_formatter)
run_log.addHandler(run_logfile)
run_log.setLevel(logging.DEBUG)


def load_gpio_configs(filename):
    gpio_config = ConfigParser()
    gpio_config.read(filename)
    # Load Output Pin Identities
    loaded_pin_directory = {"power_gpio": int(gpio_config["OUTPUT_PINS"]["power_switch_gpio"]),
                            "reboot_gpio": int(gpio_config["OUTPUT_PINS"]["reboot_switch_gpio"]),
                            "status_gpio": int(gpio_config["INPUT_PINS"]["power_status_gpio"]),
                            "buzzer_gpio": int(gpio_config["INPUT_PINS"]["motherboard_buzzer_gpio"])}
    run_log.debug("Loaded Power GPIO = {0} from \'{1}\'".format(str(loaded_pin_directory["power_gpio"]), filename))
    run_log.debug("Loaded Reboot GPIO = {0} from \'{1}\'".format(str(loaded_pin_directory["reboot_gpio"]), filename))
    run_log.debug("Loaded Status GPIO = {0} from \'{1}\'".format(str(loaded_pin_directory["status_gpio"]), filename))
    run_log.debug("Loaded Buzzer GPIO = {0} from \'{1}\'".format(str(loaded_pin_directory["buzzer_gpio"]), filename))
    return loaded_pin_directory


if __name__ == '__main__':
    config_directory = str(sys.argv[1])
    log_directory = str(sys.argv[2])
    print("!!!!!" + config_directory + "/gpio.conf")
    pin_directory = load_gpio_configs(config_directory + "/gpio.conf")
    run_log.info("Loaded GPIO Configs")
    state_reader = PowerStatusReader(pin_directory["status_gpio"],
                                     pin_directory["buzzer_gpio"],
                                     log_level=logging.DEBUG)
    run_log.info("Loaded Status Reader")
    time.sleep(1)
    state_controller = PowerStateController(pin_directory["power_gpio"],
                                            pin_directory["reboot_gpio"], log_level=logging.DEBUG)
    run_log.info("Loaded Status Controller")

    input("turn on?\n")
    print(state_controller.power_on())
    input("turn off?\n")
    print(state_controller.power_off())
    input("reboot?\n")
    print(state_controller.reboot())

    input("end?\n")
    state_controller.shutdown_power_controller()
    state_reader.shutdown_status_reader()
