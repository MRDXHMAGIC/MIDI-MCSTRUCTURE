from gc import collect
from os import listdir, path, makedirs, _exit
from sys import exit
from PIL import Image, ImageFilter
from time import sleep
from json import load, dump, loads as load_bytes
from mido import MidiFile, tick2second
from pynbt import TAG_Int, TAG_String, TAG_Compound, TAG_Short, NBTFile
from serial import Serial
from shutil import rmtree, move
from pickle import loads, dumps
from random import randint
from pygame import display, time, font, image, transform, event, Surface, QUIT, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYUP, K_TAB, mouse, MOUSEBUTTONUP, MOUSEBUTTONDOWN, BLEND_RGBA_MULT, SRCALPHA
from hashlib import md5
from requests import get
from win32api import GetLogicalDriveStrings
from threading import Thread
from traceback import format_exc
from subprocess import Popen
from serial.serialutil import PARITY_EVEN
import serial.tools.list_ports

def asset_load():
    try:
        font.init()
        asset_list["font"] = font.Font("Asset/font/font.ttf", 28)
        state[2] = "完成更新中"
        if path.isdir("Cache/Updater"):
            n = 0
            while n <= 16:
                try:
                    if path.isdir("Updater"):
                        rmtree("Updater")
                    break
                except Exception:
                    n += 1
            move("Cache/Updater", "Updater")
            rmtree("Cache")
        state[2] = "加载配置文件中"
        with open("Asset/text/manifest.json", "r") as manifest:
            asset_list["manifest"] = dumps(load(manifest))
        with open("Asset/text/setting.json", "r") as settings:
            asset_list["setting"] = load(settings)
        asset_list["fps"] = asset_list["setting"]["setting"]["fps"]
        state[3][0] = int(asset_list["setting"]["setting"]["auto_gain"])
        state[3][2] = int(asset_list["setting"]["setting"]["speed"])
        state[3][3] = bool(asset_list["setting"]["setting"]["skip"])
        state[3][4] = bool(asset_list["setting"]["setting"]["enable_percussion"])
        state[3][5] = int(asset_list["setting"]["setting"]["mode"])
        state[3][6] = bool(asset_list["setting"]["setting"]["append_number"])
        state[3][7] = int(asset_list["setting"]["setting"]["file_type"])
        state[3][9] = int(asset_list["setting"]["setting"]["range_limit"])
        log[0][1] = bool(asset_list["setting"]["setting"]["log_level"])
        if bool(asset_list["setting"]["setting"]["check_update"]):
            Thread(target=get_update_log).start()
        state[2] = "加载界面资源中"
        asset_list["menu_pic"] = image.load("Asset/image/menu_background.png")
        asset_list["menu_pic"] = transform.smoothscale(asset_list["menu_pic"], DisplaySize).convert_alpha()
        i = md5(image.tobytes(asset_list["menu_pic"], "RGBA")).hexdigest()
        if i != asset_list["setting"]["setting"]["background_hash"] or "blur_background.png" not in listdir("Asset/image"):
            asset_list["setting"]["setting"]["background_hash"] = i
            Image.open("Asset/image/menu_background.png").filter(ImageFilter.GaussianBlur(radius=16)).save("Asset/image/blur_background.png")
        asset_list["file_pic"] = image.load("Asset/image/file.png")
        asset_list["file_pic"] = transform.smoothscale(asset_list["file_pic"], (20, 28)).convert_alpha()
        asset_list["set_pic"] = image.load("Asset/image/setting_background.png")
        asset_list["set_pic"] = transform.smoothscale(asset_list["set_pic"], (780, 43)).convert_alpha()
        asset_list["msg_pic"] = image.load("Asset/image/message_background.png")
        asset_list["msg_pic"] = transform.smoothscale(asset_list["msg_pic"], (800, 45)).convert_alpha()
        asset_list["blur_pic"] = image.load("Asset/image/blur_background.png")
        asset_list["blur_pic"] = (transform.smoothscale(asset_list["blur_pic"], DisplaySize).convert_alpha(), asset_list["set_pic"].get_size(), asset_list["msg_pic"].get_size())
        asset_list["setting_pic"] = image.load("Asset/image/setting.png")
        asset_list["setting_pic"] = transform.smoothscale(asset_list["setting_pic"], (20, 28)).convert_alpha()
        asset_list["start_pic"] = image.load("Asset/image/start.png")
        asset_list["start_pic"] = transform.smoothscale(asset_list["start_pic"], (20, 28)).convert_alpha()
        asset_list["midi_pic"] = image.load("Asset/image/midi.png")
        asset_list["midi_pic"] = transform.smoothscale(asset_list["midi_pic"], (20, 28)).convert_alpha()
        asset_list["update_pic"] = image.load("Asset/image/update.png")
        asset_list["update_pic"] = transform.smoothscale(asset_list["update_pic"], (20, 28)).convert_alpha()
        asset_list["info_pic"] = image.load("Asset/image/information.png")
        asset_list["info_pic"] = transform.smoothscale(asset_list["info_pic"], (20, 28)).convert_alpha()
        asset_list["err_pic"] = image.load("Asset/image/error.png")
        asset_list["err_pic"] = transform.smoothscale(asset_list["err_pic"], (20, 28)).convert_alpha()
        asset_list["default_pic"] = image.load("Asset/image/default.png")
        asset_list["default_pic"] = transform.smoothscale(asset_list["default_pic"], (20, 28)).convert_alpha()
        asset_list["progress_bar"] = image.load("Asset/image/progress_bar.png")
        asset_list["progress_bar"] = transform.smoothscale(asset_list["progress_bar"], (2, 20)).convert_alpha()
        state[2] = "加载结构模板中"
        asset_list["structure_file"] = []
        for n in listdir("Asset/mcstructure"):
            if path.splitext(n)[1] == ".mcstructure":
                Thread(target=structure_load, args=[n]).start()
        state[2] = "获取开源协议中"
        asset_list["mms_license"] = "skip"
        if bool(asset_list["setting"]["setting"]["license"]):
            asset_list["fontL"] = font.Font("Asset/font/font.ttf", 18)
            asset_list["setting"]["setting"]["license"] = 0
            try:
                asset_list["mms_license"] = get("https://gitee.com/mrdxhmagic/midi-mcstructure/raw/master/LICENSE").text.splitlines()
                asset_list["mms_license"] += ["", "按任意键进入软件"]
                asset_list["mms_license"] = (asset_list["mms_license"], len(asset_list["mms_license"]))
            except Exception:
                asset_list["mms_license"] = (["无法获取版权信息", "按任意键跳过"], 2)
                asset_list["setting"]["setting"]["license"] = 1
        if asset_list["setting"]["setting"]["id"] == -1:
            asset_list["setting"]["setting"]["id"] = 0
            message_list.append(("使用键盘的TAB键或鼠标的中键查看帮助。", -1))
        else:
            message_list.append(("欢迎使用 MIDI-MCSTRUCTURE V" + asset_list["setting"]["setting"]["version"] + "-" + asset_list["setting"]["setting"]["edition"], -1))
        state[2] = "done"
    except Exception:
        save_log(1, "E:", format_exc())
    finally:
        if state[2] != "done":
            state[2] = "加载失败，请重试"
        else:
            state[2] = "加载完成"
            state[0] = 2

def structure_load(n):
    with open("Asset/mcstructure/" + n, "rb") as s
