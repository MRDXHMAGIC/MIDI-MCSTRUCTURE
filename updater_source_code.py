from os import path, makedirs, listdir, remove
from time import sleep
from json import load, dump
from py7zr import SevenZipFile
from shutil import rmtree, move
from traceback import format_exc
from subprocess import Popen

def save_log(log_position, log_type, log_info):
    if log[0][1]:
        log[0][0] = True
        if log_type != "":
            log[log_position].append(log_type)
        for info in log_info.splitlines():
            log[log_position].append("  " + info)

log = [[False, True], ["Updater:"]]
root = path.split(path.realpath(__file__))[0][:-18].replace("\\", "/") + "/"

try:
    sleep(0.1)
    save_log(1, "Normal:", "Load Old Settings")
    with open(root + "Asset/text/setting.json", "r") as io:
        old_setting = load(io)
    save_log(1, "Information:", "MMS Updater V250619P | MMS V" + old_setting["setting"]["version"])
    save_log(1, "Normal:", "Position: " + root)
    if path.exists(root + "Cache"):
        save_log(1, "Normal:", "Remove Directory: Cache")
        rmtree(root + "Cache")
    save_log(1, "Normal:", "Make Directory: Cache")
    makedirs(root + "Cache")

    save_log(1, "Normal:", "Extract Package")
    with SevenZipFile(root + "Asset/update/package.7z", "r") as io:
        io.extractall(root + "Cache")

    save_log(1, "Normal:", "Load New Settings")
    with open(root + "Cache/Asset/text/setting.json", "r") as io:
        new_setting = load(io)
    save_log(1, "", "Copy Settings:")
    for k in list(old_setting["setting"].keys()):
        if k in new_setting["setting"] and k not in ("version", "edition", "color", "background_hash", "exceptional_version"):
            save_log(1, "", "  " + str(k) + ": " + str(old_setting["setting"][k]) + " -> " + str(new_setting["setting"][k]))
            new_setting["setting"][k] = old_setting["setting"][k]
    save_log(1, "", "Save Settings")
    with open(root + "Cache/Asset/text/setting.json", "w") as io:
        dump(new_setting, io)

    if path.exists(root + "Cache/Asset/mcstructure") and path.exists(root + "Asset/mcstructure"):
        save_log(1, "Normal:", "Move Structures:")
        for i in listdir(root + "Asset/mcstructure"):
            if path.splitext(i)[1] == ".mcstructure":
                save_log(1, "", "    Find: " + i)
                if not path.exists(root + "Cache/Asset/mcstructure/" + i):
                    save_log(1, "", "    Move: " + i)
                    move(root + "Asset/mcstructure/" + i, root + "Cache/Asset/mcstructure/" + i)

    if path.exists(root + "Cache/Asset/profile") and path.exists(root + "Asset/profile"):
        save_log(1, "Normal:", "Move SoundFonts:")
        for i in listdir(root + "Asset/profile"):
            if path.splitext(i)[1] == ".json":
                save_log(1, "", "    Find: " + i)
                if not path.exists(root + "Cache/Asset/profile/" + i):
                    save_log(1, "", "    Move: " + i)
                    move(root + "Asset/profile/" + i, root + "Cache/Asset/profile/" + i)

    save_log(1, "Normal:", "Install Update:")
    for i in listdir(root):
        save_log(1, "", "  Try to Remove: " + i)
        if i not in ("Updater", "Cache"):
            n = 0
            while n <= 16:
                try:
                    if path.isdir(root + i):
                        rmtree(root + i)
                    elif path.isfile(root + i):
                        remove(root + i)
                    break
                except Exception:
                    n += 1

    for i in listdir(root + "Cache"):
        save_log(1, "", "  Try to Move: " + i)
        if path.splitext(i)[1] == ".exe":
            move(root + "Cache/" + i, root + "MIDI-MCSTRUCTURE.exe")
        elif path.isdir(root + "Cache/" + i) and i != "Updater":
            move(root + "Cache/" + i, root + i)

    save_log(1, "Update Successfully:", "V" + str(old_setting["setting"]["version"]) + " -> V" + str(new_setting["setting"]["version"]))
except Exception:
    save_log(1, "Error:", format_exc())
finally:
    if log[0][0] and log[0][1]:
        with open(root + "update_log.txt", "w") as file:
            for texts in log[1:]:
                if len(texts) == 1:
                    texts.append("None")
                for m, text in enumerate(texts):
                    if m != 0:
                        text = "  " + text
                    file.write(str(text) + "\n")
    sleep(1)
    Popen(root + "MIDI-MCSTRUCTURE.exe")