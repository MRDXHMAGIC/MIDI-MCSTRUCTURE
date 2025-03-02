from os import path, makedirs, listdir, getcwd
from json import load, dump
from shutil import rmtree, move
from zipfile import ZipFile
from subprocess import Popen

try:
    if path.exists("Cache"):
        rmtree("Cache")
    makedirs("Cache")

    with ZipFile("Asset/update/package.zip", "r") as io:
        io.extractall("Cache")
    rmtree("Asset/update")

    with open("Asset/text/setting.json", "r") as io:
        old_setting = load(io)
    with open("Cache/Asset/text/setting.json", "r") as io:
        new_setting = load(io)
    for k in list(old_setting["setting"].keys()):
        if k in new_setting["setting"] and k != "version":
            new_setting["setting"][k] = old_setting["setting"][k]
    with open("Cache/Asset/text/setting.json", "w") as io:
        dump(new_setting, io)

    for i in listdir("Cache"):
        n = path.splitext(i)
        if n[1] == ".exe" and n[0] != "updater":
            move("Cache/" + i, "MIDI-MCSTRUCTURE.exe")
        elif path.isdir("Cache/" + i):
            try:
                rmtree(i)
            finally:
                move("Cache/" + i, i)
finally:
    Popen(getcwd() + "\\MIDI-MCSTRUCTURE.exe")