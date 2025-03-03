from os import path, makedirs, listdir
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
root = path.split(path.realpath(__file__))[0][:-8]

try:
    if path.exists(root + "/Cache"):
        rmtree(root + "/Cache")
    makedirs(root + "/Cache")

    with ZipFile(root + "/Asset/update/package.zip", "r") as io:
        io.extractall(root + "/Cache")
    rmtree(root + "/Asset/update")

    with open(root + "/Asset/text/setting.json", "r") as io:
        old_setting = load(io)
    with open(root + "/Cache/Asset/text/setting.json", "r") as io:
        new_setting = load(io)
    for k in list(old_setting["setting"].keys()):
        if k in new_setting["setting"] and k != "version":
            new_setting["setting"][k] = old_setting["setting"][k]
    with open(root + "/Cache/Asset/text/setting.json", "w") as io:
        dump(new_setting, io)

    for i in listdir(root + "/Cache"):
        if path.splitext(i)[1] == ".exe":
            move(root + "/Cache/" + i, "MIDI-MCSTRUCTURE.exe")
        elif path.isdir(root + "/Cache/" + i) and i != "Updater":
            try:
                rmtree(root + "/" + i)
            finally:
                move(root + "/Cache/" + i, root + "/" + i)
except Exception as error_info:
    save_log(1, str(error_info), format_exc())
finally:
    if log[0][0] and log[0][1]:
        with open(root + "/log.txt", "a") as file:
            for texts in log[1:]:
                if len(texts) == 1:
                    texts.append("None")
                for m, text in enumerate(texts):
                    if m != 0:
                        text = "  " + text
                    file.write(str(text) + "\n")
    Popen(root + "/MIDI-MCSTRUCTURE.exe")