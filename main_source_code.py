from gc import collect
from os import listdir, path, makedirs, _exit
from PIL import Image, ImageFilter
from time import sleep
from json import loads as load_bytes, dumps as dump_bytes
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
        with open("Asset/text/manifest.json", "r") as io:
            asset_list["manifest"] = dumps(load_bytes(io.read()))
        with open("Asset/text/setting.json", "r") as io:
            asset_list["setting"] = load_bytes(io.read())
        asset_list["fps"] = asset_list["setting"]["setting"]["fps"]
        state[3][0] = int(asset_list["setting"]["setting"]["auto_gain"])
        state[3][2] = int(asset_list["setting"]["setting"]["speed"])
        state[3][3] = bool(asset_list["setting"]["setting"]["skip"])
        state[3][4] = bool(asset_list["setting"]["setting"]["enable_percussion"])
        state[3][5] = int(asset_list["setting"]["setting"]["mode"])
        state[3][6] = bool(asset_list["setting"]["setting"]["append_number"])
        state[3][7] = int(asset_list["setting"]["setting"]["file_type"])
        state[3][9] = int(asset_list["setting"]["setting"]["range_limit"])
        state[3][10] = bool(asset_list["setting"]["setting"]["adjust_instrument"])
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
        collect()

def structure_load(n):
    with open("Asset/mcstructure/" + n, "rb") as structure:
        structure = NBTFile(structure, little_endian=True)
    i = [dumps(structure),
         str(structure["size"][0].value) +
         "*" + str(structure["size"][2].value) +
         "*" + str(structure["size"][1].value) +
         "  " + path.splitext(n)[0]]
    if "推荐" in path.splitext(n)[0]:
        asset_list["structure_file"].insert(0, i)
    else:
        asset_list["structure_file"].append(i)
    del i
    del structure
    collect()

def convertor(midi_path, midi_name, cvt_setting):
    message_id = task_id
    convertor_state = True
    message_list.append(["[--%] 正在加载 " + midi_name[0:-4], message_id])
    try:
        if cvt_setting[5] == 2:
            asset_list["setting"]["setting"]["id"] += 1
            play_id = str(asset_list["setting"]["setting"]["id"])
        else:
            play_id = "0.."
        if cvt_setting[7] == 2:
            output_name = "JE"
        else:
            output_name = "BE"
        output_name += uuid(8).upper()
        mid = MidiFile(midi_path + midi_name, clip=True)
        if cvt_setting[7] == 0:
            try:
                structure = loads(asset_list["structure_file"][cvt_setting[1]][0])
                total = structure["size"][0].value * structure["size"][1].value * structure["size"][2].value
                h = total - 1
            except Exception:
                convertor_state = "无可用模板"
                return
            manifest = {}
            behavior = []
        elif cvt_setting[7] == 1:
            structure = TAG_Compound({})
            manifest = loads(asset_list["manifest"])
            manifest["header"]["name"] = midi_name[0:-4]
            manifest["header"]["uuid"] = uuid(8) + "-" + uuid(4) + "-" + uuid(4) + "-" + uuid(4) + "-" + uuid(12)
            manifest["modules"][0]["uuid"] = uuid(8) + "-" + uuid(4) + "-" + uuid(4) + "-" + uuid(4) + "-" + uuid(12)
            behavior = [{"pack_id": manifest["header"]["uuid"], "version": manifest["header"]["version"]}]
            total = 0
            h = float("INF")
        elif cvt_setting[7] == 2:
            structure = TAG_Compound({})
            manifest = {}
            behavior = {"pack": {"pack_format": 1, "description": "§bby §dMIDI-MCSTRUCTURE"}}
            total = 0
            h = float("INF")
        else:
            structure = TAG_Compound({})
            manifest = {}
            behavior = []
            total = 0
            h = float("INF")
        num = 0
        for track in mid.tracks:
            for msg in track:
                if msg.type == "note_on" and msg.velocity != 0:
                    num += 1
        if cvt_setting[7] == 0:
            total += num * 2
        else:
            total = num * 3
        if len(message_list) == 0:
            message_list.append(["[0%] 正在转换 " + midi_name[0:-4], message_id])
        progress_bar(message_id, midi_name[0:-4], 0, 1)
        progress = 0
        offset_time = -1
        info_list = {}
        velocity_list = []
        pitch_list = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        tempo_list = [(0, 500000), (float("INF"), 0)]
        for track in mid.tracks:
            source_time = 0
            for msg in track:
                source_time += msg.time
                if msg.type == "set_tempo":
                    for n, tmp in enumerate(tempo_list):
                        if tmp[0] > source_time:
                            tempo_list.insert(n, (source_time, msg.tempo))
                            break
                if msg.type == "control_change":
                    channel = msg.channel
                    if channel not in info_list:
                        info_list[channel] = {"volume": [(float("INF"), 1)]}
                    if msg.control == 7:
                        value = int(msg.value / 1.27) / 100
                        for n, vol in enumerate(info_list[channel]["volume"]):
                            if vol[0] >= source_time:
                                info_list[channel]["volume"].insert(n, (source_time, value))
                                break
                    elif msg.control == 121:
                        for n, vol in enumerate(info_list[channel]["volume"]):
                            if vol[0] >= source_time:
                                info_list[channel]["volume"].insert(n, (source_time, 1))
                                break
                if msg.type == "note_on":
                    note = msg.note - 21
                    channel = msg.channel
                    velocity = msg.velocity / 127
                    if velocity != 0:
                        if channel not in info_list:
                            info_list[channel] = {"volume": [(float("INF"), 1)]}
                        if cvt_setting[9] != 0 and channel != 9:
                            volume = 1
                            for vol in info_list[channel]["volume"]:
                                if vol[0] > source_time:
                                    break
                                else:
                                    volume = vol[1]
                            if 0 <= note <= 2:
                                pitch_list[0] += velocity * volume * 0.2
                            elif 3 <= note <= 14:
                                pitch_list[1] += velocity * volume * 0.225
                            elif 15 <= note <= 26:
                                pitch_list[2] += velocity * volume * 0.25
                            elif 27 <= note <= 38:
                                pitch_list[3] += velocity * volume * 0.275
                            elif 39 <= note <= 50:
                                pitch_list[4] += velocity * volume * 0.3
                            elif 51 <= note <= 62:
                                pitch_list[5] += velocity * volume * 0.275
                            elif 63 <= note <= 74:
                                pitch_list[6] += velocity * volume * 0.25
                            elif 75 <= note <= 86:
                                pitch_list[7] += velocity * volume * 0.225
                            elif note == 87:
                                pitch_list[8] += velocity * volume * 0.2
                        if cvt_setting[0] != 0:
                            velocity_list.append((source_time, velocity, channel))
                        if cvt_setting[3]:
                            if (cvt_setting[4] or channel != 9) and (offset_time == -1 or source_time < offset_time):
                                offset_time = source_time
                        else:
                            offset_time = 0
                        progress += 1
                        progress_bar(message_id, "正在转换 " + midi_name[0:-4], progress, total)
        if offset_time:
            tick_time = 0
            for n in range(1, len(tempo_list)):
                if tempo_list[n][0] <= offset_time:
                    tick_time += tick2second(tempo_list[n][0] - tempo_list[n - 1][0], mid.ticks_per_beat, tempo_list[n - 1][1]) * 2000 / cvt_setting[2]
                else:
                    tick_time += tick2second(offset_time - tempo_list[n - 1][0], mid.ticks_per_beat, tempo_list[n - 1][1]) * 2000 / cvt_setting[2]
                    break
            offset_time = tick_time
        if cvt_setting[9] == 2:
            pitch_offset = [0, 0]
            for n, i in enumerate(pitch_list):
                if i >= pitch_offset[1]:
                    pitch_offset = [n, i]
            pitch_offset = (4 - pitch_offset[0]) * 12
        else:
            pitch_offset = 0
        total_vol = 1
        if cvt_setting[0] != 0:
            num = 0
            total_vol = 0
            velocity_list.sort()
            for n in velocity_list[int(round(len(velocity_list) * 0.1)):int(round(len(velocity_list) * 0.9))]:
                num += 1
                volume = 1
                for vol in info_list[n[2]]["volume"]:
                    if vol[0] > n[0]:
                        break
                    else:
                        volume = vol[1]
                total_vol += n[1] * volume
            total_vol /= num
            total_vol = int(cvt_setting[0] / total_vol) / 100
        if cvt_setting[5] == 1:
            append_num = 2
        elif cvt_setting[5] == 2:
            append_num = 2
        else:
            append_num = 0
        num = 0
        note_len = len(asset_list["setting"]["asset"]["note_list"])
        time_list = []
        info_list = {}
        note_buffer = {}
        for track in mid.tracks:
            source_time = 0
            for msg in track:
                source_time += msg.time
                if msg.type == "set_tempo":
                    for n, tmp in enumerate(tempo_list):
                        if tmp[0] > source_time:
                            tempo_list.insert(n, (source_time, msg.tempo))
                            break
                if msg.type == "control_change":
                    channel = msg.channel
                    if channel not in info_list:
                        info_list[channel] = {"program": [(float("INF"), "")], "volume": [(float("INF"), 1)], "balance": [(float("INF"), "")]}
                    if msg.control == 7:
                        value = int(msg.value / 1.27) / 100
                        for n, vol in enumerate(info_list[channel]["volume"]):
                            if vol[0] >= source_time:
                                info_list[channel]["volume"].insert(n, (source_time, value))
                                break
                    elif msg.control == 8 or msg.control == 10:
                        value = msg.value - 64
                        if value > 0:
                            value = value / -63
                        elif value < 0:
                            value = value / -64
                        for n, bal in enumerate(info_list[channel]["balance"]):
                            if bal[0] > source_time:
                                info_list[channel]["balance"].insert(n, (source_time, value))
                                break
                    elif msg.control == 121:
                        for n, bal in enumerate(info_list[channel]["balance"]):
                            if bal[0] > source_time:
                                info_list[channel]["balance"].insert(n, (source_time, 0))
                                break
                        for n, vol in enumerate(info_list[channel]["volume"]):
                            if vol[0] > source_time:
                                info_list[channel]["volume"].insert(n, (source_time, 1))
                                break
                if msg.type == "program_change":
                    program = str(msg.program)
                    channel = msg.channel
                    if channel not in info_list:
                        info_list[channel] = {"program": [(float("INF"), "")], "volume": [(float("INF"), 1)], "balance": [(float("INF"), "")]}
                    if channel != 9:
                        if cvt_setting[7] == 2:
                            if program in asset_list["setting"]["asset"]["java"]["sound_list"]:
                                value = asset_list["setting"]["asset"]["java"]["sound_list"][program]
                            else:
                                value = asset_list["setting"]["asset"]["java"]["sound_list"]["undefined"]
                        else:
                            if program in asset_list["setting"]["asset"]["bedrock"]["sound_list"]:
                                value = asset_list["setting"]["asset"]["bedrock"]["sound_list"][program]
                            else:
                                value = asset_list["setting"]["asset"]["bedrock"]["sound_list"]["undefined"]
                        for n, typ in enumerate(info_list[channel]["program"]):
                            if typ[0] > source_time:
                                info_list[channel]["program"].insert(n, (source_time, value))
                                break
                if msg.type == "note_on":
                    note = msg.note - 21
                    channel = msg.channel
                    velocity = msg.velocity
                    if velocity != 0:
                        volume = 1
                        for vol in info_list[channel]["volume"]:
                            if vol[0] > source_time:
                                break
                            else:
                                volume = vol[1]
                        balance = ""
                        for bal in info_list[channel]["balance"]:
                            if bal[0] > source_time:
                                break
                            else:
                                balance = bal[1]
                        if channel == 9:
                            if cvt_setting[7] == 2:
                                if str(note + 21) in asset_list["setting"]["asset"]["java"]["sound_list"]["percussion"]:
                                    program = asset_list["setting"]["asset"]["java"]["sound_list"]["percussion"][str(note + 21)]
                                else:
                                    program = asset_list["setting"]["asset"]["java"]["sound_list"]["percussion"]["undefined"]
                            else:
                                if str(note + 21) in asset_list["setting"]["asset"]["bedrock"]["sound_list"]["percussion"]:
                                    program = asset_list["setting"]["asset"]["bedrock"]["sound_list"]["percussion"][str(note + 21)]
                                else:
                                    program = asset_list["setting"]["asset"]["bedrock"]["sound_list"]["percussion"]["undefined"]
                        else:
                            if cvt_setting[7] == 2:
                                program = asset_list["setting"]["asset"]["java"]["sound_list"]["default"]
                            else:
                                program = asset_list["setting"]["asset"]["bedrock"]["sound_list"]["default"]
                            for typ in info_list[channel]["program"]:
                                if typ[0] > source_time:
                                    break
                                else:
                                    program = typ[1]
                        if cvt_setting[10]:
                            velocity = int((velocity / 1.27) * volume * total_vol * program[1]) / 100
                        else:
                            velocity = int((velocity / 1.27) * volume * total_vol) / 100
                        if velocity >= 1:
                            velocity = 1
                        if channel == 9:
                            pitch = 1
                        else:
                            if 0 <= note < note_len:
                                pitch = asset_list["setting"]["asset"]["note_list"][note + pitch_offset]
                            else:
                                pitch = None
                        tick_time = 0
                        for n in range(1, len(tempo_list)):
                            if tempo_list[n][0] <= source_time:
                                tick_time += tick2second(tempo_list[n][0] - tempo_list[n - 1][0], mid.ticks_per_beat, tempo_list[n - 1][1]) * 2000 / cvt_setting[2]
                            else:
                                tick_time += tick2second(source_time - tempo_list[n - 1][0], mid.ticks_per_beat, tempo_list[n - 1][1]) * 2000 / cvt_setting[2]
                                break
                        tick_time = int(round(tick_time - offset_time))
                        if (cvt_setting[4] or channel != 9) and ((cvt_setting[5] == 0 or num <= h - append_num) and (channel == 9 or (pitch is not None and (cvt_setting[9] == 0 or 0.5 <= pitch <= 2)))):
                            if state[3][7] == 3:
                                raw_text = "WD " + to_text(note, 2)
                            else:
                                if cvt_setting[7] == 2:
                                    if cvt_setting[5] == 0:
                                        raw_text = asset_list["setting"]["asset"]["java"]["command_delay"]
                                    elif cvt_setting[5] == 1:
                                        raw_text = asset_list["setting"]["asset"]["java"]["command_clock"]
                                    elif cvt_setting[5] == 2:
                                        raw_text = asset_list["setting"]["asset"]["java"]["command_address"]
                                    else:
                                        raw_text = ""
                                else:
                                    if cvt_setting[5] == 0:
                                        raw_text = asset_list["setting"]["asset"]["bedrock"]["command_delay"]
                                    elif cvt_setting[5] == 1:
                                        raw_text = asset_list["setting"]["asset"]["bedrock"]["command_clock"]
                                    elif cvt_setting[5] == 2:
                                        raw_text = asset_list["setting"]["asset"]["bedrock"]["command_address"]
                                    else:
                                        raw_text = ""
                                if cvt_setting[10]:
                                    pitch *= program[2]
                                raw_text = raw_text.replace("{SOUND}", str(program[0])).replace("{BALANCE}", str(balance)).replace("{VOLUME}", str(velocity)).replace("{PITCH}", str(pitch)).replace("{TIME}", str(tick_time)).replace("{ADDRESS}", str(play_id))
                            if tick_time not in note_buffer:
                                note_buffer[tick_time] = []
                            if tick_time not in time_list:
                                time_list.append(tick_time)
                            note_buffer[tick_time].append(raw_text)
                            num += 1
                        else:
                            if cvt_setting[7] != 0:
                                progress += 1
                        progress += 1
                        progress_bar(message_id, "正在转换 " + midi_name[0:-4], progress, total)
        time_list.sort()
        if cvt_setting[7] == 2:
            if cvt_setting[5] == 1:
                note_buffer[time_list[-1]].append("/scoreboard players set @a[scores={MMS_Service="
                                                  + str(time_list[-1])
                                                  + "..}] MMS_Service -1"
                                                  )
                note_buffer[time_list[-1]].append("/scoreboard players add @a[scores={MMS_Service=0..}] MMS_Service 1")
                total += 2
            elif cvt_setting[5] == 2:
                note_buffer[time_list[-1]].append("/scoreboard players set @a[scores={MMS_Service="
                                                  + str(time_list[-1]) + "..,"
                                                  + "MMS_Address=" + str(play_id) + "}] MMS_Service -1"
                                                  )
                note_buffer[time_list[-1]].append("/scoreboard players add @a[scores={MMS_Service=0..,"
                                                  + "MMS_Address=" + str(play_id)
                                                  + "}] MMS_Service 1")
                total += 2
        else:
            if cvt_setting[5] == 1:
                note_buffer[time_list[-1]].append("/scoreboard players set @a[scores={MMS_Service="
                                                  + str(time_list[-1])
                                                  + "..}] MMS_Service -1"
                                                  )
                note_buffer[time_list[-1]].append("/scoreboard players add @a[scores={MMS_Service=0..}] MMS_Service 1")
                if cvt_setting[7] == 1:
                    total += 2
            elif cvt_setting[5] == 2:
                note_buffer[time_list[-1]].append("/scoreboard players set @a[scores={MMS_Service="
                                                  + str(time_list[-1]) + "..,"
                                                  + "MMS_Address=" + str(play_id) + "}] MMS_Service -1"
                                                  )
                note_buffer[time_list[-1]].append("/scoreboard players add @a[scores={MMS_Service=0..,"
                                                  + "MMS_Address=" + str(play_id)
                                                  + "}] MMS_Service 1")
                if cvt_setting[7] == 1:
                    total += 2
        if cvt_setting[7] == 0:
            tick_time = 0
            del_list = []
            s = (structure["size"][0].value,
                 structure["size"][1].value,
                 structure["size"][2].value)
            p = [0, 0, 0]
            for n in structure["structure"]["palette"]["default"]["block_position_data"]:
                i = structure["structure"]["palette"]["default"]["block_position_data"][n]["block_entity_data"]
                if i["CustomName"].value == "start":
                    p[0] = i["x"].value - structure["structure_world_origin"][0].value
                    p[1] = i["y"].value - structure["structure_world_origin"][1].value
                    p[2] = i["z"].value - structure["structure_world_origin"][2].value
                elif i["CustomName"].value == "append":
                    i["Command"] = TAG_String(i["Command"].value.replace("__ADDRESS__", str(play_id)))
                    i["Command"] = TAG_String(i["Command"].value.replace("__NAME__", str(path.splitext(midi_name)[0])))
                    i["Command"] = TAG_String(i["Command"].value.replace("__TOTAL__", str(time_list[-1])))
                    del_list.append(list_position(s, (
                        i["x"].value - structure["structure_world_origin"][0].value,
                        i["y"].value - structure["structure_world_origin"][1].value,
                        i["z"].value - structure["structure_world_origin"][2].value
                    )))
                    progress += 1
                    progress_bar(message_id, "正在转换 " + midi_name[0:-4], progress, total)
                i["CustomName"] = TAG_String("")
            n = 0
            air_palette = -1
            for n, i in enumerate(structure["structure"]["palette"]["default"]["block_palette"]):
                if i["name"].value == "minecraft:air":
                    air_palette = n
                    break
            if air_palette == -1:
                air_palette = n + 1
                structure["structure"]["palette"]["default"]["block_palette"].append(
                    TAG_Compound({
                        "name": TAG_String("minecraft:air"),
                        "states": TAG_Compound(),
                        "val": TAG_Short(0),
                        "version": TAG_Int(18090528)
                    })
                )
            i = 1
            for source_time in time_list:
                for n, cmd in enumerate(note_buffer[source_time]):
                    if structure["structure"]["palette"]["default"]["block_position_data"].get(str(list_position(s, p))) and check(s, p):
                        if cvt_setting[5] != 0 or n != 0:
                            output_time = 0
                        else:
                            output_time = source_time - tick_time
                        structure["structure"]["palette"]["default"]["block_position_data"][str(list_position(s, p))]["block_entity_data"]["Command"] = TAG_String(cmd)
                        structure["structure"]["palette"]["default"]["block_position_data"][str(list_position(s, p))]["block_entity_data"]["TickDelay"] = TAG_Int(output_time)
                        if cvt_setting[6]:
                            if i == 1:
                                structure["structure"]["palette"]["default"]["block_position_data"][str(list_position(s, p))]["block_entity_data"]["CustomName"] = TAG_String(path.splitext(midi_name)[0])
                            else:
                                structure["structure"]["palette"]["default"]["block_position_data"][str(list_position(s, p))]["block_entity_data"]["CustomName"] = TAG_String(str(i) + "/" + str(num))
                        del_list.append(list_position(s, p))
                        direct = structure["structure"]["palette"]["default"]["block_palette"][structure["structure"]["block_indices"][0][list_position(s, p)].value]["states"]["facing_direction"].value
                        if direct == 0:
                            p[1] -= 1
                        elif direct == 1:
                            p[1] += 1
                        elif direct == 2:
                            p[2] -= 1
                        elif direct == 3:
                            p[2] += 1
                        elif direct == 4:
                            p[0] -= 1
                        elif direct == 5:
                            p[0] += 1
                        i += 1
                        progress += 1
                        progress_bar(message_id, "正在转换 " + midi_name[0:-4], progress, total)
                    else:
                        break
                tick_time = source_time
            for n in range(h, -1, -1):
                if n not in del_list:
                    if str(n) in structure["structure"]["palette"]["default"]["block_position_data"]:
                        del structure["structure"]["palette"]["default"]["block_position_data"][str(n)]
                    structure["structure"]["block_indices"][0][n] = TAG_Int(air_palette)
                    structure["structure"]["block_indices"][1][n] = TAG_Int(-1)
                    progress += 1
                    progress_bar(message_id, "正在转换 " + midi_name[0:-4], progress, total)
            with open(output_name + ".mcstructure", "wb") as io:
                structure.save(io, little_endian=True)
        elif cvt_setting[7] == 1:
            if path.exists(output_name):
                rmtree(output_name)
            makedirs(output_name)
            makedirs(output_name + "/functions")
            with open(output_name + "/functions/mms_player.mcfunction", "w", encoding="utf-8") as io:
                for source_time in time_list:
                    for cmd in note_buffer[source_time]:
                        io.write(cmd[1:] + "\n")
                        progress += 1
                        progress_bar(message_id, "正在转换 " + midi_name[0:-4], progress, total)
            with open(output_name + "/world_behavior_packs.json", "w") as io:
                io.write(dump_bytes(behavior))
            with open(output_name + "/manifest.json", "w") as io:
                io.write(dump_bytes(manifest))
        elif cvt_setting[7] == 2:
            if path.exists(output_name):
                rmtree(output_name)
            makedirs(output_name)
            makedirs(output_name + "/data")
            makedirs(output_name + "/data/mms")
            makedirs(output_name + "/data/mms/functions")
            with open(output_name + "/data/mms/functions/player.mcfunction", "w", encoding="utf-8") as io:
                for source_time in time_list:
                    for cmd in note_buffer[source_time]:
                        io.write(cmd[1:] + "\n")
                        progress += 1
                        progress_bar(message_id, "正在转换 " + midi_name[0:-4], progress, total)
            with open(output_name + "/pack.mcmeta", "w") as io:
                io.write(dump_bytes(behavior))
        elif state[3][7] == 3:
            progress_bar(message_id, "正在连接 " + asset_list["serial_list"][state[3][8]][1], progress, total)
            with Serial(asset_list["serial_list"][state[3][8]][0], baudrate=9600, parity=PARITY_EVEN) as device:
                if device.is_open:
                    device.write(b"CR")
                    sleep(0.1)
                    if device.read_all().decode() == "IC":
                        progress_bar(message_id, "已连接 " + device.name, progress, total)
                        tick_time = 0
                        for source_time in time_list:
                            for n, cmd in enumerate(note_buffer[source_time]):
                                if n == 0:
                                    output_time = source_time - tick_time
                                else:
                                    output_time = 0
                                cmd += to_text(output_time, 3)
                                device.write(cmd.encode())
                                i = 0
                                while not device.in_waiting:
                                    if i >= 100:
                                        convertor_state = "连接设备超时"
                                        return
                                    i += 1
                                    sleep(0.001)
                                device.reset_input_buffer()
                                progress += 1
                                progress_bar(message_id, "写入中 " + midi_name[0:-4], progress, total)
                            tick_time = source_time
                    else:
                        convertor_state = "连接设备失败"
                        return
        del mid
        del info_list
        del time_list
        del structure
        del tempo_list
        del note_buffer
        del velocity_list
        collect()
        convertor_state = False
    except Exception:
        save_log(3, "E:", format_exc())
    finally:
        if convertor_state is False:
            message_list.append(("转换完成，文件已保存在程序运行目录下！", task_id))
        else:
            if convertor_state is True:
                convertor_state = "未知错误"
            message_list.append(("因" + convertor_state + "无法转换 " + midi_name[0:-4], task_id))

def progress_bar(mess_id, title, pss, tal):
    try:
        if len(message_list) != 0 and message_list[0][1] == mess_id:
            if pss == tal:
                if len(message_list) > 1 and message_list[1][1] == mess_id:
                    state[8][0] = 3250
                else:
                    state[8][0] = 3000
            else:
                message_list[0][0] ="[" + str(int((pss / tal) * 100)) + "%] " + title
                state[8][0] = 0
        elif len(message_list) == 0:
            message_list.append(["[" + str(int((pss / tal) * 100)) + "%] " + title, mess_id])
    except Exception:
        pass

def save_log(log_pos, log_type, log_info):
    if log[0][1]:
        log[0][0] = True
        log[log_pos].append(log_type)
        for i in log_info.splitlines():
            log[log_pos].append("  " + i)

def save_json():
    try:
        asset_list["setting"]["setting"]["fps"] = asset_list["fps"]
        asset_list["setting"]["setting"]["auto_gain"] = state[3][0]
        asset_list["setting"]["setting"]["speed"] = state[3][2]
        asset_list["setting"]["setting"]["skip"] = int(state[3][3])
        asset_list["setting"]["setting"]["enable_percussion"] = int(state[3][4])
        asset_list["setting"]["setting"]["mode"] = state[3][5]
        asset_list["setting"]["setting"]["append_number"] = int(state[3][6])
        asset_list["setting"]["setting"]["file_type"] = state[3][7]
        asset_list["setting"]["setting"]["range_limit"] = state[3][9]
        asset_list["setting"]["setting"]["adjust_instrument"] = int(state[3][10])
        with open("Asset/text/setting.json", "w") as io:
            io.write(dump_bytes(asset_list["setting"], indent=2))
    except Exception:
        save_log(5, "E:", format_exc())

def to_text(i, n):
    i = str(i)
    if len(i) < n:
        i = "0" * (n - len(i)) + i
    else:
        i = i[-n:]
    return i

def get_update_log():
    try:
        update_log = load_bytes(get("https://gitee.com/mrdxhmagic/midi-mcstructure/raw/master/Update.json").content)
        n = {"version": 0}
        for i in update_log:
            if len(str(i["version"])) == 8 and int(n["version"]) < int(i["version"]):
                n = i
        del update_log
        if n["version"] not in asset_list["setting"]["setting"]["exceptional_version"] and int(n["version"]) > int(asset_list["setting"]["setting"]["version"]):
            state[5] = n
    except Exception:
        save_log(4, "E:", format_exc())
    finally:
        collect()

def download():
    try:
        if path.exists("Asset/update"):
            rmtree("Asset/update")
        makedirs("Asset/update")
        state[6][0] = 0
        if "hash" in state[5]:
            target_hash = state[5]["hash"]
        else:
            target_hash = "disable"
        real_hash = md5()
        response = get(state[5]["download_url"], stream=True)
        state[6][1] = int(response.headers['content-length'])
        with open("Asset/update/package.7z", 'ab') as io:
            for chunk in response.iter_content(chunk_size=1024):
                io.write(chunk)
                real_hash.update(chunk)
                state[6][0] += len(chunk)
        real_hash = str(real_hash.hexdigest())
        if target_hash != "disable" and real_hash != target_hash:
            raise ValueError("The Expected Hash is " + str(target_hash) + ", But the Hash of Downloaded FIle is " + str(real_hash) + ".")
        message_list.append(("下载完成，即将进行更新。", -1))
        state[7] = 2
    except Exception:
        state[6] = [0, 0, True]
        message_list.append(("下载失败，请重试。", -1))
        save_log(4, "E:", format_exc())

def setting_help():
    if state[0] == 3:
        message_list.append(("按任意键进入软件。", -1))
    if state[0] == 3:
        if state[4]:
            message_list.append(("鼠标左键打开文件，右键返回，滚轮切换。", -1))
        else:
            message_list.append(("键盘右方向键打开文件，左方向键返回，上下方向键切换。", -1))
    elif state[0] == 4:
        if state[1][0] == 0:
            if state[4]:
                message_list.append(("点击鼠标左键应用设置并开始转换。", -1))
            else:
                message_list.append(("点击键盘右方向键应用设置并开始转换。", -1))
        elif state[1][0] == 1:
            message_list.append(("使不同音乐间的音量与设定值一致，统一听感。", -1))
        elif state[1][0] == 2:
            message_list.append(("调整音乐的播放速度，一般用于缓解音频卡顿。", -1))
        elif state[1][0] == 3:
            message_list.append(("跳过音乐开头静音的部分，大部分情况下建议开启。", -1))
        elif state[1][0] == 4:
            message_list.append(("移除所有轨道上的和弦来简化音乐，一般不建议使用。", -1))
        elif state[1][0] == 5:
            message_list.append(("选择控制播放时序的方式，一般选择低卡顿的命令链延迟。", -1))
        elif state[1][0] == 6:
            message_list.append(("决定是否重命名命令方块名称为音符的序号和音乐名称。", -1))
        elif state[1][0] == 7:
            message_list.append(("决定输出文件类型，mcfunction不支持命令链延迟模式。", -1))
        elif state[1][0] == 8:
            message_list.append(("决定命令链排列方式，均为普通结构文件，用户可自制模板。", -1))
        elif state[1][0] == 9:
            message_list.append(("自动升降音调并去除部分音符来适配JE版我的世界的音域。", -1))
        elif state[1][0] == 10:
            message_list.append(("选择一个受支持的串口设备，来向其传输音乐数据。", -1))
    elif state[0] == 5:
        if state[1][0] == 0:
            if state[4]:
                message_list.append(("点击鼠标左键开始下载并应用更新。", -1))
            else:
                message_list.append(("点击键盘右方向键开始下载并应用更新。", -1))
        elif state[1][0] == 1:
            message_list.append(("不再显示该版本更新的提示。", -1))

def list_position(size, pos):
    n = pos[2]
    n += pos[1] * size[2]
    n += pos[0] * (size[1] * size[2])
    return n

def position(size, pos):
    l = [0, 0, 0]
    l[0] = pos // (size[1] * size[2])
    pos = pos % (size[1] * size[2])
    l[1] = pos // size[2]
    pos = pos % size[2]
    l[2] += pos
    return l

def check(size, pos):
    if pos[0] >= size[0] or pos[0] < 0:
        return False
    elif pos[1] >= size[1] or pos[1] < 0:
        return False
    elif pos[2] >= size[2] or pos[2] < 0:
        return False
    else:
        return True

def next_page():
    global midi_file
    global task_id
    if state[0] == 3:
        if (not state[5] is None) and (len(page) == 0 and state[1][0] == len(file_path)):
            page.append([state[1][0], state[1][1], -1])
            state[1] = [0, 0, -1]
            state[0] = 5
        elif len(file_path) > state[1][0] and path.splitext(file_path[state[1][0]])[1] == ".mid":
            page.append([state[1][0], state[1][1], -1])
            j = ""
            for k in real_path:
                j += k
            if not j == "":
                j += "/"
            midi_file = (j, file_path[state[1][0]])
            state[1] = [0, 0, -1]
            state[0] = 4
            asset_list["serial_list"] = []
            for n, i in enumerate(list(serial.tools.list_ports.comports())):
                i = list(i)
                if "Arduino Leonardo" in i[1]:
                    asset_list["serial_list"].insert(0, i)
                else:
                    asset_list["serial_list"].append(i)
        else:
            Thread(target=open_file).start()
    elif state[0] == 4:
        if state[1][0] == 0:
            Thread(target=convertor, args=(midi_file[0], midi_file[1], state[3])).start()
            task_id += 1
        elif state[1][0] == 1:
            state[3][0] += 10
            if state[3][0] >= 110:
                state[3][0] = 0
        elif state[1][0] == 2:
            state[3][2] += 5
            if state[3][2] >= 130:
                state[3][2] = 75
        elif state[1][0] == 3:
            if state[3][3]:
                state[3][3] = False
            else:
                state[3][3] = True
        elif state[1][0] == 4:
            if state[3][4]:
                state[3][4] = False
            else:
                state[3][4] = True
        elif state[1][0] == 5:
            state[3][5] += 1
            if state[3][5] >= 3:
                state[3][5] = 0
        elif state[1][0] == 6:
            if state[3][6]:
                state[3][6] = False
            else:
                state[3][6] = True
        elif state[1][0] == 7:
            state[3][7] += 1
            if state[3][7] >= 4:
                state[3][7] = 0
        elif asset_list.get("structure_file") and state[1][0] == 8:
            state[3][1] += 1
            if state[3][1] >= len(asset_list["structure_file"]):
                state[3][1] = 0
        elif state[1][0] == 9:
            state[3][9] += 1
            if state[3][9] >= 3:
                state[3][9] = 0
        elif state[1][0] == 10:
            if state[3][10]:
                state[3][10] = False
            else:
                state[3][10] = True
        elif len(asset_list["serial_list"]) != 0 and state[1][0] == 11:
            state[3][8] += 1
            if state[3][8] >= len(asset_list["serial_list"]):
                state[3][8] = 0
    elif state[0] == 5:
        if state[6][2] and state[1][0] == 0:
            Thread(target=download).start()
            state[6][2] = False
        elif state[1][0] == 1:
            asset_list["setting"]["setting"]["exceptional_version"].append(state[5]["version"])
            state[0] = 3
            state[1] = page[-1]
            del page[-1]
            state[5] = None
            message_list.append(("已忽略此次更新。", -1))

def last_page():
    if state[0] == 3:
        Thread(target=close_file).start()
    elif state[0] == 4:
        state[0] = 3
        state[1] = page[-1]
        del page[-1]
    elif state[0] == 5:
        state[0] = 3
        state[1] = page[-1]
        del page[-1]

def open_file():
    global file_path
    if 0 <= state[1][0] < len(file_path):
        real_path.append(file_path[state[1][0]] + "/")
        e = ""
        for f in real_path:
            e += f
        if path.isdir(e):
            file_path = []
            page.append([state[1][0], state[1][1], -1])
            state[1] = [0, 0, -1]
            for f in listdir(e):
                if path.isdir(e + f) or path.splitext(e + f)[1] == ".mid":
                    if f[0] != ".":
                        file_path.append(f)
        else:
            del real_path[-1]

def close_file():
    global file_path
    if 0 < len(real_path):
        del real_path[-1]
        if len(real_path) == 0:
            file_path = []
            for e in GetLogicalDriveStrings().split("\000")[:-1]:
                file_path.append(e[0:-2] + ":/")
            for e in listdir():
                if path.splitext(e)[1] == ".mid":
                    if e[0] != ".":
                        file_path.append(e)
        else:
            f = ""
            for e in real_path:
                f += e
            file_path = []
            for e in listdir(f):
                if path.isdir(f + e) or path.splitext(f + e)[1] == ".mid":
                    if e[0] != ".":
                        file_path.append(e)
        state[1] = page[-1]
        del page[-1]

def to_alpha(origin_surf, color_value, surf_size=None, surf_position=(0, 0)):
    if surf_size is None:
        surf_size = origin_surf.get_size()
    else:
        alpha_surf = Surface(origin_surf.get_size(), SRCALPHA)
        alpha_surf.fill((255, 255, 255, 255))
        origin_surf.blit(alpha_surf, (0, 0), special_flags=BLEND_RGBA_MULT)
    alpha_surf = Surface(surf_size, SRCALPHA)
    alpha_surf.fill(color_value)
    origin_surf.blit(alpha_surf, surf_position, special_flags=BLEND_RGBA_MULT)
    return origin_surf

def uuid(n):
    cmd = ""
    while not n == 0:
        cmd += str(hex(randint(0, 15)))[2:]
        n -= 1
    return cmd

def setting_blit(setting):
    global real_position
    global progress_bar_position
    title_alpha = 0
    if len(message_list) != 0:
        state[8][0] += clock.get_time()
        if state[8][0] >= 3000:
            state[8][1] -= (state[8][1] - 450) * speed
        else:
            state[8][1] -= (state[8][1] - 405) * speed
        if state[8][1] < 450:
            title_alpha = (450 - state[8][1]) / 45
        blur_surface = to_alpha(asset_list["menu_pic"].copy(), (255, 255, 255, 0), asset_list["blur_pic"][2], (0, state[8][1]))
    else:
        blur_surface = asset_list["menu_pic"].copy()
    color = [[0, 0, 0, 0], asset_list["setting"]["setting"]["color"][0], asset_list["setting"]["setting"]["color"][1]]
    file_offset = 0
    setting_num = len(setting)
    if setting_num >= 10:
        if state[9] != -1 and state[1][0] > round((setting_num - 1) * state[9]):
            state[1][2] = state[1][0]
            state[1][0] -= 1
            if state[1][1] > 0:
                state[1][1] -= 1
        elif state[9] != -1 and state[1][0] < round((setting_num - 1) * state[9]):
            state[1][2] = state[1][0]
            state[1][0] += 1
            if state[1][1] < 9:
                state[1][1] += 1
        expect_position = int((state[1][0] / (setting_num - 1)) * 430)
        if progress_bar_position < -25 and expect_position > 215:
            progress_bar_position = 480
        progress_bar_position -= (progress_bar_position - expect_position) * speed
    else:
        if progress_bar_position > 215:
            progress_bar_position -= (progress_bar_position - 480) * speed
            if progress_bar_position > 475:
                progress_bar_position = -30
        else:
            progress_bar_position -= (progress_bar_position + 30) * speed
    blur_surface = to_alpha(blur_surface, (255, 255, 255, 0), (2, 20), (0, progress_bar_position))
    if setting_num == 0:
        state[1] = [0, 0, -1]
        setting.append(("无可选文件或选项", 4))
    else:
        if state[1][0] >= setting_num:
            if state[4]:
                state[1] = [setting_num - 1, 9, state[1][2]]
            else:
                state[1] = [0, 0, state[1][2]]
        elif state[1][0] < 0:
            if state[4]:
                state[1] = [0, 0, state[1][2]]
            else:
                state[1] = [setting_num - 1, 9, state[1][2]]
        if state[1][0] >= state[1][1]:
            file_offset = state[1][0] - state[1][1]
    file_position = int(10 + (state[1][0] - file_offset) * 43)
    real_position -= (real_position - file_position) * speed
    window.blit(to_alpha(blur_surface, (0, 0, 0, 0), asset_list["blur_pic"][1], (10, real_position)), (0, 0))
    window.blit(asset_list["set_pic"], (10, real_position))
    delta_position = abs(file_position - real_position) / 28
    for a, b in enumerate(setting[file_offset:(10 + file_offset)]):
        icon_type = int(b[1])
        if icon_type == 0:
            origin_surface = asset_list["file_pic"].copy()
        elif icon_type == 1:
            origin_surface = asset_list["setting_pic"].copy()
        elif icon_type == 2:
            origin_surface = asset_list["start_pic"].copy()
        elif icon_type == 3:
            origin_surface = asset_list["midi_pic"].copy()
        elif icon_type == 4:
            origin_surface = asset_list["err_pic"].copy()
        elif icon_type == 5:
            origin_surface = asset_list["info_pic"].copy()
        elif icon_type == 6:
            origin_surface = asset_list["update_pic"].copy()
        else:
            origin_surface = asset_list["default_pic"].copy()
        if a == state[1][0] - file_offset:
            if a == 9 and len(message_list) != 0:
                text_alpha = title_alpha
            else:
                text_alpha = delta_position
            if text_alpha <= 1:
                color[0] = (color[1][0] - (color[1][0] - color[2][0]) * text_alpha,
                            color[1][1] - (color[1][1] - color[2][1]) * text_alpha,
                            color[1][2] - (color[1][2] - color[2][2]) * text_alpha,
                            color[1][3] - (color[1][3] - color[2][3]) * text_alpha)
            else:
                color[0] = color[2]
        else:
            if a == state[1][2] - file_offset and not (a == 9 and len(message_list) != 0):
                if delta_position <= 1:
                    color[0] = (color[2][0] + (color[1][0] - color[2][0]) * delta_position,
                                color[2][1] + (color[1][1] - color[2][1]) * delta_position,
                                color[2][2] + (color[1][2] - color[2][2]) * delta_position,
                                color[2][3] + (color[1][3] - color[2][3]) * delta_position)
                else:
                    color[0] = color[1]
            else:
                color[0] = color[2]
        window.blit(to_alpha(origin_surface, color[0]), (22, a * 43 + 18))
        window.blit(to_alpha(asset_list["font"].render(b[0], True, (255, 255, 255)), color[0]), (54, a * 43 + 18))
    window.blit(asset_list["progress_bar"], (0, progress_bar_position))
    if len(message_list) != 0:
        window.blit(asset_list["msg_pic"], (0, state[8][1]))
        window.blit(to_alpha(asset_list["font"].render(message_list[0][0], True, (255, 255, 255)), (255, 255, 255, title_alpha * 255)), (10, state[8][1] + 8))
        if state[8][0] >= 3250:
            state[8][0] = 0
            state[8][1] = 450
            del message_list[0]

log = [[False, True], ["Loading:"], ["Main:"], ["Convertor:"], ["Updater:"], ["Other:"]]
state = [0, [0, 0, -1], "init", [0, 0, 100, True, 0, 0, False, 0, 0, 0, 0], False, None, [0, 0, True], 0, [0, 0], -1]

try:
    display.init()
    DisplaySize = (800, 450)
    display.set_icon(image.load("Asset/image/icon.png"))
    window = display.set_mode(DisplaySize)
    display.set_caption("MIDI-MCSTRUCTURE GUI")

    page = []
    state[8][1] = DisplaySize[1]
    file_path = []
    real_path = []
    midi_file = []
    asset_list = {"fps": 60}
    message_list = []
    task_id = 0
    press_time = 0
    real_position = 0
    mouse_inputting = False
    progress_bar_position = 0

    clock = time.Clock()

    while True:
        if state[7] and (state[7] == 1 or len(message_list) == 0):
            break
        for env in event.get():
            if env.type == QUIT:
                state[7] = 1
            if env.type == MOUSEBUTTONDOWN:
                if state[0] != 2:
                    if env.button == 1:
                        if mouse.get_pos()[0] <= 10:
                            mouse_inputting = True
            if env.type == MOUSEBUTTONUP:
                state[4] = True
                if env.button == 1:
                    if state[0] != 2:
                        if not mouse_inputting:
                            next_page()
                        else:
                            mouse_inputting = False
                    else:
                        state[0] = 3
                if env.button == 2:
                    if state[0] != 2:
                        setting_help()
                if env.button == 3:
                    if state[0] != 2:
                        last_page()
                    else:
                        state[0] = 3
                if env.button == 4:
                    if state[0] != 2:
                        state[1][2] = state[1][0]
                        state[1][0] -= 1
                        if state[1][1] > 0:
                            state[1][1] -= 1
                if env.button == 5:
                    if state[0] != 2:
                        state[1][2] = state[1][0]
                        state[1][0] += 1
                        if state[1][1] < 9:
                            state[1][1] += 1
            if env.type == KEYUP:
                state[4] = False
                if env.key == K_ESCAPE:
                    exit()
                if state[0] != 2:
                    if env.key == K_TAB:
                        setting_help()
                    if env.key == K_DOWN:
                        state[1][2] = state[1][0]
                        state[1][0] += 1
                        if state[1][1] < 9:
                            state[1][1] += 1
                    if env.key == K_UP:
                        state[1][2] = state[1][0]
                        state[1][0] -= 1
                        if state[1][1] > 0:
                            state[1][1] -= 1
                    if env.key == K_LEFT:
                        last_page()
                    if env.key == K_RIGHT:
                        next_page()
                else:
                    state[0] = 3
        if mouse_inputting:
            state[9] = mouse.get_pos()[1] / 450
            if state[9] > 1:
                state[9] = 1
            elif state[9] < 0:
                state[9] = 0
        else:
            state[9] = -1
        speed = clock.get_fps()
        if speed > 10:
            speed = 10 / speed
        else:
            speed = 1
        if state[0] == 0:
            Thread(target=asset_load).start()
            asset_list["load_pic"] = image.load("Asset/image/loading.png")
            asset_list["load_pic"] = transform.scale(asset_list["load_pic"], DisplaySize).convert_alpha()
            file_path = []
            for c in GetLogicalDriveStrings().split("\000")[:-1]:
                file_path.append(c[0:-2] + ":/")
            for c in listdir():
                if path.splitext(c)[1] == ".mid":
                    file_path.append(c)
            state[0] = 1
        elif state[0] == 1:
            window.blit(asset_list["load_pic"], (0, 0))
            if state[2] != "init":
                text_surf = asset_list["font"].render(state[2], True, (63, 63, 63))
                window.blit(text_surf, (400 - text_surf.get_size()[0] * 0.5, 340))
        elif state[0] == 2:
            if asset_list["mms_license"] != "skip":
                window.blit(asset_list["blur_pic"][0], (0, 0))
                for num_line, line in enumerate(asset_list["mms_license"][0]):
                    text_surface = asset_list["fontL"].render(line, True, (255, 255, 255))
                    window.blit(text_surface, (round((800 - text_surface.get_size()[0]) / 2), round((450 - asset_list["mms_license"][1] * 22) / 2 + num_line * 22)))
            else:
                state[0] = 3
        elif state[0] == 3:
            window.blit(asset_list["blur_pic"][0], (0, 0))
            setting_text = []
            for c in file_path:
                if path.splitext(c)[1] == ".mid":
                    setting_text.append((c, 3))
                else:
                    setting_text.append((c, 0))
            if len(page) == 0 and not state[5] is None:
                if state[6][0] == 0:
                    setting_text.append(["发现更新 V" + str(state[5]["version"]) + "-" + str(state[5]["edition"]), 6])
                else:
                    setting_text.append(["正在下载 V" + str(state[5]["version"]) + "-" + str(state[5]["edition"]), 6])
            setting_blit(setting_text)
        elif state[0] == 4:
            window.blit(asset_list["blur_pic"][0], (0, 0))
            setting_text = ([["开始转换  ", 2], ["音量均衡  ", 1], ["播放速度  ", 1], ["静音跳过  ", 1],
                             ["打击乐器  ", 1], ["播放模式  ", 1], ["添加序号  ", 1], ["输出模式  ", 1],
                             ["结构模板  ", 1], ["音域调整  ", 1], ["乐器调整  ", 1], ["串口设备  ", 1]])
            setting_text[0][0] += midi_file[1][0:-4]
            if state[3][0] == 0:
                setting_text[1][0] += "关"
            else:
                setting_text[1][0] += str(state[3][0]) + "%"
            setting_text[2][0] += str(state[3][2] / 100)
            if state[3][2] % 10 == 0:
                setting_text[2][0] += "0"
            setting_text[2][0] += "倍"
            if state[3][3]:
                setting_text[3][0] += "开"
            else:
                setting_text[3][0] += "关"
            if state[3][4]:
                setting_text[4][0] += "正常"
            else:
                setting_text[4][0] += "忽略"
            if state[3][5] == 0:
                setting_text[5][0] += "命令链延迟"
            elif state[3][5] == 1:
                setting_text[5][0] += "计分板时钟"
            elif state[3][5] == 2:
                setting_text[5][0] += "时钟与编号"
            if state[3][6]:
                setting_text[6][0] += "开"
            else:
                setting_text[6][0] += "关"
            if state[3][7] == 0:
                setting_text[7][0] += ".mcstructure"
            elif state[3][7] == 1:
                setting_text[7][0] += ".mcfunction (BE)"
                if state[3][5] == 0:
                    setting_text[5][1] = 4
            elif state[3][7] == 2:
                setting_text[7][0] += ".mcfunction (JE)"
                if state[3][5] == 0:
                    setting_text[5][1] = 4
                if state[3][9] == 0:
                    setting_text[9][1] = 4
            elif state[3][7] == 3:
                setting_text[7][0] += "串口设备"
            if asset_list.get("structure_file"):
                setting_text[8][0] += asset_list["structure_file"][state[3][1]][1]
            if state[3][9] == 0:
                setting_text[9][0] += "直出 (BE)"
            elif state[3][9] == 1:
                setting_text[9][0] += "限幅 (JE)"
            elif state[3][9] == 2:
                setting_text[9][0] += "自动 (JE)"
            if state[3][10]:
                setting_text[10][0] += "开"
            else:
                setting_text[10][0] += "关"
            if len(asset_list["serial_list"]) != 0:
                setting_text[11][0] += asset_list["serial_list"][state[3][8]][1]
            setting_blit(setting_text)
        elif state[0] == 5:
            window.blit(asset_list["blur_pic"][0], (0, 0))
            if state[6][1] == 0:
                setting_text = [["立即更新  V", 2]]
            elif state[6][0] == state[6][1]:
                setting_text = [["即将更新  V", 2]]
            else:
                setting_text = [["正在下载  V", 2]]
            setting_text.append(["忽略更新", 1])
            setting_text[0][0] += str(state[5]["version"]) + "-" + str(state[5]["edition"])
            if state[6][0] != state[6][1]:
                setting_text[0][0] += "   " + str(round(state[6][0] / 1048576, 2)) + "/" + str(round(state[6][1] / 1048576, 2)) + "MB"
            setting_text += state[5]["feature"]
            setting_blit(setting_text)
        display.flip()
        clock.tick(asset_list["fps"])
except Exception:
        save_log(2, "E:", format_exc())
finally:
    if not log[0][0]:
        save_json()
    if log[0][0] and log[0][1]:
        with open("log.txt", "a") as file:
            for texts in log[1:]:
                if len(texts) == 1:
                    texts.append("None")
                for m, text in enumerate(texts):
                    if m != 0:
                        text = "  " + text
                    file.write(str(text) + "\n")
    if state[7] == 2:
        sleep(1)
        Popen("Updater/updater.exe")
    _exit(0)