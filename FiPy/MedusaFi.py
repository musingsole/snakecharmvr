from FiPyFunctions import get_timestamp, get_device_id, enable_ntp
from FiPyFunctions import LED_BLUE, LED_GREEN, LED_OFF
from FiPyFunctions import button_handler, reset_handler, log_message
from FiPyFunctions import connect_lte, simple_connect, bringup_wlan
from time import sleep
import json
from machine import Timer, reset
import os
import time
from MedusaOTAGround import OTA
from uwebsockets import connect as connect_websocket


MedusaWebSocket = "wss://8pp64nk6vl.execute-api.us-east-1.amazonaws.com/prod"


wifi_sec_type = {
    1: "WEP",
    2: "WPA",
    3: "WPA2",
    5: "WPA2 Enterprise"
}


class Medusa(dict):
    @staticmethod
    def clear_device(*args, **kwargs):
        log_message("Processing halted. Clearing device")

        time.sleep(5)

        # Remove stored configuration, resetting device to freshly
        # installed state
        os.remove("medusa.json")

        reset_handler()

    def __init__(self, FLASHING_LIGHT, **kwargs):
        self.FLASHING_LIGHT = FLASHING_LIGHT

        # Configure push button to clear device
        self.button = button_handler(self.clear_device)

        self.last_upload = None
        self['id'] = get_device_id()

        # Recover configuration if it exists
        try:
            with open("medusa.json", "r") as f:
                self.configuration = json.loads(f.read())
        except Exception:
            self.configuration = {}

        # Set operational cursor
        self.cursor = get_timestamp()
        self.monitor_delay = 60

        self.threads = {}

        self.lte = None
        self.wlan = None

    def heartbeat(self, status):
        return {
            "TREE": "goldenfight_status",
            "TRUNK": get_timestamp(),
            "STATUS": status
        }

    def create_thread(self,
                      name,
                      handler,
                      **kwargs):
        if name in self.threads:
            raise Exception("Thread {} already exists".format(name))

        def thread_handler(arg=None):
            try:
                if arg is None:
                    handler()
                else:
                    handler(arg)
            except Exception as e:
                log_message("{} Thread Failed: {}".format(name, e))
                time.sleep(5)
                reset()

        thread = Timer.Alarm(
            handler=thread_handler,
            **kwargs
        )

        self.threads[name] = thread

    def cancel_threads(self):
        for name, thread in self.threads.items():
            thread.cancel()

    def lte_reset_handler(self, *args, **kwargs):
        if self.lte is not None:
            self.lte.deinit()

        print("Resetting device in 5 seconds")
        time.sleep(5)
        reset()

    def main(self):
        try:
            """ Operational Function for Medusa Device """
            log_message("Medusa!")

            # Start thread to reset device after 10 monitoring cycles
            self.create_thread(name="reset",
                               handler=self.lte_reset_handler,
                               s=self.monitor_delay * 10 + 5,
                               periodic=True)

            # Flash light blue to show Medusa is configuring itself (may indicate WiFi AP is up)
            self.FLASHING_LIGHT.colors = [LED_BLUE, LED_OFF]

            try:
                log_message("Attempting WiFi connection")
                with open("networks.json", "r") as f:
                    networks = json.loads(f.read())

                known_ssids = list(networks.keys())

                self.wlan = bringup_wlan()

                # List of visible network tuples (SSID, bssid, sec, channel, rssi)
                visible_networks = self.wlan.scan()
                visible_known = [net for net in visible_networks if net[0] in known_ssids]

                for network in visible_known:
                    try:
                        ssid = network[0]
                        pw = networks[ssid]
                        simple_connect(ssid, pw, wlan=self.wlan)
                    except Exception:
                        log_message("Failed to connect to {}".format(network))

                if self.wlan.isconnected() is not True:
                    raise Exception("Failed to find network")

            except Exception:
                log_message("Failed to find WiFi network.")
                self.receive_instructions()

            self.monitor()
        except Exception as e:
            log_message("Main thread failed: {}".format(e))
            raise

    def receive_instructions(self):
        log_message("Starting cellular connection")
        self.lte = connect_lte()

        enable_ntp()

        log_message("Connecting WebSocket")
        self.websocket = connect_websocket(MedusaWebSocket)

        log_message("Sending heartbeat")
        heartbeat = self.heartbeat("Cellular")
        self.upload_memories([heartbeat])

        log_message("Making instructions request")
        request = {
            "action": "request",
            "REQUEST_TREE": "medusa_networks",
            "Limit": 1,
            "ScanIndexForward": False
        }
        self.websocket.send(json.dumps(request))

        try:
            with open("networks.json", "r") as f:
                known_networks = json.loads(f.read())
        except Exception:
            known_networks = {}

        log_message("Waiting for response")
        resp = {"NEW_NETWORKS": []}
        while not resp["NEW_NETWORKS"]:
            resp = self.websocket.recv()
            log_message("Received: {}".format(resp))
            log_message(type(resp))
            resp = json.loads(resp)[0]
            resp['NETWORKS'] = json.loads(resp['NETWORKS'])

            resp['NEW_NETWORKS'] = [ssid for ssid in resp['NETWORKS'].keys() if ssid not in known_networks]

        with open("networks.json", "w") as f:
            f.write(json.dumps(resp['NETWORKS']))

        log_message("Received updated network list. Resetting device")
        self.lte_reset_handler()

    def monitor(self):
            enable_ntp()

            # Flash light green and blue to show device has connected to network and is registering with Mobius
            self.FLASHING_LIGHT.colors = [LED_BLUE, LED_GREEN] + [LED_OFF] * 4

            # Check for firmware updates
            OTA(self.FLASHING_LIGHT)

            # Build websocket
            log_message("Connecting WebSocket")
            self.websocket = connect_websocket(MedusaWebSocket)

            # Flash light green slowly to show Medusa is connected, configured and operational. Green will pulse throughout operation
            self.FLASHING_LIGHT.colors = [LED_GREEN] + [LED_OFF] * 4
            self.FLASHING_LIGHT.set_milliseconds(500)

            # Start monitoring loop
            while True:
                sleep(1)

    def upload_memories(self, memories, log=log_message):
        data = json.dumps({"action": "upload", "memories": memories})
        self.websocket.send(data)
