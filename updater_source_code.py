from os import path, makedirs, listdir, remove
from time import sleep
from json import load, dump
from shutil import rmtree, move
from zipfile import ZipFile
from traceback import format_exc
from subprocess import Popen


def save_log(log_position, log_type, log_info):
    if log[0][1]:
        log[0][0] = True
        log[log_position].append(log_type)
        for info in log_info.splitlines():
            log[log_position].append("  " + info)

log = [[False, True], ["Updater:"]]
root = path.split(path.realpath(__file__))[0][:-18]

try:
    sleep(0.1)
    if path.exists(root + "/Cache"):
        save_log(1, "Normal:", "Remove Directory: Cache")
        rmtree(root + "/Cache")
    save_log(1, "Normal:", "Make Directory: Cache")
    makedirs(root + "/Cache")

    save_log(1, "Normal:", "Extract Package")
    with ZipFile(root + "/Asset/update/package.zip", "r") as io:
        io.extractall(root + "/Cache")

    save_log(1, "Normal:", "Load Settings")
    with open(root + "/Asset/text/setting.json", "r") as io:
        old_setting = load(io)
    with open(root + "/Cache/Asset/text/setting.json", "r") as io:
        new_setting = load(io)
    save_log(1, "Normal:", "Copy Settings")
    for k in list(old_setting["setting"].keys()):
        if k in new_setting["setting"] and k != "version":
            new_setting["setting"][k] = old_setting["setting"][k]
    save_log(1, "Normal:", "Save Settings")
    with open(root + "/Cache/Asset/text/setting.json", "w") as io:
        dump(new_setting, io)

    save_log(1, "Normal:", "Remove Files")
    for i in listdir(root):
        if i not in ("Updater", "Cache"):
            n = 0
            while n <= 16:
                try:
                    save_log(1, "Normal:", "Try to Remove: " + i)
                    if path.isdir(root + "/" + i):
                        rmtree(root + "/" + i)
                    elif path.isfile(root + "/" + i):
                        remove(root + "/" + i)
                    break
                except Exception:
                    n += 1

    save_log(1, "Normal:", "Install Update")
    for i in listdir(root + "/Cache"):
        if path.splitext(i)[1] == ".exe":
            move(root + "/Cache/" + i, root + "/MIDI-MCSTRUCTURE.exe")
        elif path.isdir(root + "/Cache/" + i) and i != "Updater":
            save_log(1, "Normal:", "Try to Move: " + i)
            move(root + "/Cache/" + i, root + "/" + i)

    save_log(1, "Update Successfully!", "V" + str(old_setting["setting"]["version"]) + "-> V" + str(new_setting["setting"]["version"]))
except Exception:
    save_log(1, "Error:", format_exc())
finally:
    if log[0][0] and log[0][1]:
        with open(root + "/update_log.txt", "w") as file:
            for texts in log[1:]:
                if len(texts) == 1:
                    texts.append("None")
                for m, text in enumerate(texts):
                    if m != 0:
                        text = "  " + text
                    file.write(str(text) + "\n")
    sleep(1)
    Popen(root + "/MIDI-MCSTRUCTURE.exe")