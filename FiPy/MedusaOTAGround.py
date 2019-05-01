import json
import os
from FiPyFunctions import LED_PURPLE, LED_TEAL, LED_YELLOW, LED_OFF
from FiPyFunctions import log_message, reset_handler
from urequests import get
from sys import print_exception


GoldenFightAPI = "https://9fpoqvgcvi.execute-api.us-east-1.amazonaws.com/prod"


def remove_dir(directory, raise_exceptions=False):
    try:
        for filename in os.listdir(directory):
            path = "{}/{}".format(directory, filename)
            remove_dir(path)
        os.remove(directory)
        return True
    except Exception as e:
        log_message("Failed to remove {}".format(directory))
        if raise_exceptions:
            raise

        return False


def OTA(flashing_light):
    log_message("Checking for GoldenFight updates")

    # Open current summary
    with open("goldenfight.json", "r") as f:
        current_summary = json.loads(f.read())

    log_message("Current version is {}".format(current_summary['version']))

    # Download latest version summary
    try:
        resp = get(GoldenFightAPI + "/ota")

        if resp.status_code != 200:
            raise Exception("Unacceptable Status Code: " + str(resp.status_code))
    except Exception as e:
        log_message("Failed to download GoldenFight Version Summary")
        print_exception(e)
        raise Exception("Failed Summary Retrieval")

    latest_summary = resp.json()
    resp.close()

    # If newer version available, update files
    if current_summary['version'] < latest_summary['version']:
        log_message("Update needed. Latest Version: {}".format(latest_summary['version']))
        flashing_light.colors = [LED_PURPLE, LED_OFF, LED_TEAL] + [LED_OFF] * 4

        # Download all files into directory named after version
        try:
            os.mkdir(latest_summary['version'])
        except Exception as e:
            log_message("Failed to create directory.")
            remove_dir(latest_summary['version'])

        filenames = [fn for fn in latest_summary['files'] if fn not in latest_summary['ignore_files']]
        for filename in filenames:
            chunk_index = 0
            chunks_remaining = True
            while chunks_remaining:
                log_message("Retrieving {} Chunk {}".format(filename, chunk_index))
                get_file = get(GoldenFightAPI + "/ota/{}?chunk={}".format(filename, chunk_index))

                if get_file.status_code != 200:
                    msg = "Failed to retrieve {}".format(filename)
                    log_message(msg)
                    raise Exception(msg)

                get_file_resp = get_file.json()
                get_file.close()

                log_message("Storing {} chunk {} locally".format(filename, chunk_index))
                with open("{}/{}".format(latest_summary['version'], filename), "a") as f:
                    f.write(get_file_resp['content_chunk'])

                chunk_index += 1
                chunks_remaining = int(get_file_resp['total_chunks']) - chunk_index
                if chunks_remaining > 0:
                    log_message("Chunks remaining: {}".format(chunks_remaining))
                    chunks_remaining = True

        log_message("File downloads complete. Installing new firmware...")

        # Copy new files into place
        flashing_light.colors = [LED_YELLOW, LED_OFF, LED_OFF, LED_TEAL, LED_OFF, LED_OFF]
        for filename in filenames:
            log_message("Installing {}".format(filename))
            orig_path = "{}/{}".format(latest_summary['version'], filename)
            try:
                log_message("Removing existing version")
                remove_dir(filename, raise_exceptions=True)
            except Exception as e:
                log_message("Failed removing the existing version")
                print_exception(e)
            os.rename(orig_path, filename)

        log_message("Deleting unneeded files")

        # Delete any files not in filenames or latest_summary['save_files']
        current_files = os.listdir()
        for cf in current_files:
            if cf not in filenames + latest_summary['save_files'] + [latest_summary['version']]:
                log_message("Removing {}".format(cf))
                try:
                    remove_dir(cf)
                except Exception as e:
                    log_message("Failure to remove {}".format(cf))
                    print_exception(e)

        log_message("GoldenFight updated to {}".format(latest_summary['version']))
        reset_handler()
    else:
        log_message("Current version is up to date")
