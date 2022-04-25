
class PowerStatus:
    """ Pseudo ENUM Class to Identify Possible Power States """

    BOOTING = 0
    POWERED_ON = 1
    POWERED_OFF = 2
    SHUTTING_DOWN = 3
    ERROR = 4
    UNKNOWN = 5

    status_string = {BOOTING: "Booting", POWERED_ON: "Powered On", POWERED_OFF: "Powered Off",
                     SHUTTING_DOWN: "Shutting Down", ERROR: "Error", UNKNOWN: "Unknown"}
