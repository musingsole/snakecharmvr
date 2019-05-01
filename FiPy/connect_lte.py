from network import LTE
from time import sleep


def connect(timeout=30, lte=None):
    if lte is None:
        lte = LTE()         # instantiate the LTE object

    lte.attach()        # attach the cellular modem to a base station
    cycles = 0
    while not lte.isattached():
        sleep(1)
        cycles += 1
        if cycles > timeout:
            raise Exception("Failed to attach cellular modem to base station")

    lte.connect()       # start a data session and obtain an IP address
    cycles = 0
    while not lte.isconnected():
        sleep(1)
        cycles += 1
        if cycles > timeout:
            raise Exception("Failed to obtain cellular data session")

    return lte
