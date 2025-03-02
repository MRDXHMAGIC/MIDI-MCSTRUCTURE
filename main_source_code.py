from gc import collect
from os import listdir, path, makedirs, getcwd
from sys import exit
from json import load, dump, loads as load_bytes
from mido import MidiFile, tick2second
from pynbt import TAG_Int, TAG_String, TAG_Compound, TAG_Short, NBTFile
from shutil import rmtree, move
from pickle import loads, dumps
from random import randint
from pygame import display, time, font, image, transform, event, Surface, QUIT, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYUP, K_TAB, MOUSEBUTTONDOWN, BLEND_RGBA_MULT, SRCALPHA
from requests import get
from win32api import GetLogicalDriveStrings
from threading import Thread
from traceback import format_exc
from subprocess import Popen

def asset_load():
    try:
        font.init()
        asset_list["font"] = font.Font("Asset/font/font.ttf", 28)
        state[2] = "更新程序中"
        if path.isfile("Cache/updater.exe"):
            move("Cache/updater.exe", "updater.exe")
            rmtree("Cache")
        state[2] = "加载图片中"
        asset_list["menu_pic"] = image.load("Asset/image/menu_background.png")
        asset_list["menu_pic"] = transform.smoothscale(asset_list["menu_pic"], DisplaySize).convert_alpha()
        asset_list["file_pic"] = image.load("Asset/image/file.png")
        asset_list["file_pic"] = transform.smoothscale(asset_list["file_pic"], (
        DisplaySize[0] * 0.025, DisplaySize[1] * 0.0625)).convert_alpha()
        asset_list["set_pic"] = image.load("Asset/image/setting_background.png")
        asset_list["set_pic"] = transform.smoothscale(asset_list["set_pic"], (
        DisplaySize[0] * 0.98, DisplaySize[1] * 0.099)).convert_alpha()
        asset_list["msg_pic"] = image.load("Asset/image/message_background.png")
        asset_list["msg_pic"] = transform.smoothscale(asset_list["msg_pic"], (
        DisplaySize[0], DisplaySize[1] * 0.1)).convert_alpha()
        asset_list["setting_pic"] = image.load("Asset/image/setting.png")
        asset_list["setting_pic"] = transform.smoothscale(asset_list["setting_pic"], (
        DisplaySize[0] * 0.025, DisplaySize[1] * 0.0625)).convert_alpha()
        asset_list["start_pic"] = image.load("Asset/image/start.png")
        asset_list["start_pic"] = transform.smoothscale(asset_list["start_pic"], (
        DisplaySize[0] * 0.025, DisplaySize[1] * 0.0625)).convert_alpha()
        asset_list["midi_pic"] = image.load("Asset/image/midi.png")
        asset_list["midi_pic"] = transform.smoothscale(asset_list["midi_pic"], (
        DisplaySize[0] * 0.025, DisplaySize[1] * 0.0625)).convert_alpha()
        asset_list["update_pic"] = image.load("Asset/image/update.png")
        asset_list["update_pic"] = transform.smoothscale(asset_list["update_pic"], (
        DisplaySize[0] * 0.025, DisplaySize[1] * 0.0625)).convert_alpha()
        asset_list["info_pic"] = image.load("Asset/image/information.png")
        asset_list["info_pic"] = transform.smoothscale(asset_list["info_pic"], (
        DisplaySize[0] * 0.025, DisplaySize[1] * 0.0625)).convert_alpha()
        asset_list["err_pic"] = image.load("Asset/image/error.png")
        asset_list["err_pic"] = transform.smoothscale(asset_list["err_pic"], (
        DisplaySize[0] * 0.025, DisplaySize[1] * 0.0625)).convert_alpha()
        asset_list["default_pic"] = image.load("Asset/image/default.png")
        asset_list["default_pic"] = transform.smoothscale(asset_list["default_pic"], (
        DisplaySize[0] * 0.025, DisplaySize[1] * 0.0625)).convert_alpha()
        state[2] = "加载设置中"
        with open("Asset/text/setting.json", "r") as settings:
            asset_list["setting"] = load(settings)
        asset_list["fps"] = asset_list["setting"]["setting"]["fps"]
        state[3][0] = int(asset_list["setting"]["setting"]["auto_gain"])
        state[3][2] = int(asset_list["setting"]["setting"]["speed"])
        state[3][3] = bool(asset_list["setting"]["setting"]["skip"])
        state[3][4] = int(asset_list["setting"]["setting"]["remove_chord"])
        state[3][5] = int(asset_list["setting"]["setting"]["mode"])
        state[3][6] = bool(asset_list["setting"]["setting"]["append_number"])
        state[3][7] = int(asset_list["setting"]["setting"]["file_type"])
        log[0][1] = bool(asset_list["setting"]["setting"]["log_level"])
        with open("Asset/text/manifest.json", "r") as manifest:
            asset_list["manifest"] = dumps(load(manifest))
        state[2] = "加载模板中"
        asset_list["structure_file"] = []
        for n in listdir("Asset/text"):
            if path.splitext(n)[1] == ".mcstructure":
                Thread(target=structure_load, args=[n]).start()
        if asset_list["setting"]["setting"]["id"] == -1:
            asset_list["setting"]["setting"]["id"] = 0
            message_list.append(("使用键盘的TAB键或鼠标的中键查看帮助。", -1))
        else:
            message_list.append(("欢迎使用 MIDI-MCSTRUCTURE " + asset_list["setting"]["setting"]["version"], -1))
        state[2] = "done"
    except Exception:
        save_log(1, "E:", format_exc())
    finally:
        if state[2] != "done":
            state[2] = "  加载失败"
        else:
            state[2] = "加载已完成"
            state[0] = 2

def structure_load(n):
    with open("Asset/text/" + n, "rb") as structure:
        structure = NBTFile(structure, little_endian=True)
    i = [dumps(structure),
         str(structure["size"][0].value) +
         "*" + str(structure["size"][2].value) +
         "*" + str(structure["size"][1].value) +
         "  " + path.splitext(n)[0]]
    if path.splitext(n)[0][-3:-1] == "推荐":
        asset_list["structure_file"].insert(0, i)
    else:
        asset_list["structure_file"].append(i)
    del i
    del structure
    collect()

def convertor(midi_path, midi_name, cvt_setting):
    message_id = task_id
    convertor_state = False
    message_list.append(["[--%] " + midi_name[0:-4] + " 载入文件中", message_id])
    try:
        if cvt_setting[5] == 2:
            asset_list["setting"]["setting"]["id"] += 1
            play_id = str(asset_list["setting"]["setting"]["id"])
        else:
            play_id = "!-1"
        output_name = uuid(8).upper()
        num = 0
        tempo_list = []
        volume_list = []
        channel_type = []
        balance_list = []
        velocity_list = []
        mid = MidiFile(midi_path + midi_name)
        if cvt_setting[7] == 0:
            structure = loads(asset_list["structure_file"][cvt_setting[1]][0])
            manifest = {}
            behavior = []
            total = structure["size"][0].value * structure["size"][1].value * structure["size"][2].value
            h = total - 1
        else:
            structure = TAG_Compound({})
            manifest = loads(asset_list["manifest"])
            manifest["header"]["name"] = midi_name[0:-4]
            manifest["header"]["uuid"] = uuid(8) + "-" + uuid(4) + "-" + uuid(4) + "-" + uuid(4) + "-" + uuid(12)
            manifest["modules"][0]["uuid"] = uuid(8) + "-" + uuid(4) + "-" + uuid(4) + "-" + uuid(4) + "-" + uuid(12)
            behavior = [{"pack_id": manifest["header"]["uuid"], "version": manifest["header"]["version"]}]
            total = 0
            h = float("INF")
        for track in mid.tracks:
            for msg in track:
                if msg.type == "note_on" and msg.velocity != 0:
                    num += 1
        if cvt_setting[7] == 0:
            total += num * 2
        else:
            total = num * 3
        if len(message_list) == 0:
            message_list.append(["[0%] " + midi_name[0:-4] + " 转换正在进行", message_id])
        progress_bar(message_id, midi_name[0:-4], 0, 1)
        progress = 0
        offset_time = -1
        for n, track in enumerate(mid.tracks):
            source_time = 0
            for msg in track:
                tempo = 500000
                for tmp in tempo_list:
                    if tmp[0] <= source_time:
                        tempo = tmp[1]
                        break
                source_time += tick2second(msg.time, mid.ticks_per_beat, tempo) * 2000 / cvt_setting[2]
                if msg.type == "set_tempo":
                    value = msg.tempo
                    tempo_list.insert(0, (source_time, value))
                if msg.type == "control_change":
                    channel = msg.channel
                    if msg.control == 7:
                        value = int(msg.value / 1.27) / 100
                        volume_list.insert(0, [source_time, value, channel])
                    elif msg.control == 8:
                        value = msg.value - 64
                        if value > 0:
                            value = value / -63
                        elif value < 0:
                            value = value / -64
                        balance_list.insert(0, (source_time, value, channel))
                if msg.type == "program_change":
                    program = str(msg.program)
                    channel = msg.channel
                    if asset_list["setting"]["asset"]["sound_list"].get(program):
                        channel_type.insert(0, [source_time, asset_list["setting"]["asset"]["sound_list"][program], channel])
                    else:
                        channel_type.insert(0, [source_time, asset_list["setting"]["asset"]["sound_list"]["default"],channel])
                if msg.type == "note_on":
                    channel = msg.channel
                    velocity = msg.velocity
                    if velocity != 0:
                        if cvt_setting[0] != 0:
                            velocity_list.append((source_time, velocity / 127, channel))
                        if cvt_setting[3]:
                            tick_time = int(round(source_time))
                            if offset_time == -1 or tick_time < offset_time:
                                offset_time = tick_time
                        else:
                            offset_time = 0
                        progress += 1
                        progress_bar(message_id, midi_name[0:-4] + " 转换正在进行", progress, total)
        total_vol = 1
        if cvt_setting[0] != 0:
            num = 0
            total_vol = 0
            velocity_list.sort()
            for n in velocity_list[int(round(len(velocity_list) * 0.1)):int(round(len(velocity_list) * 0.9))]:
                num += 1
                volume = 1
                for vol in volume_list:
                    if vol[0] <= n[0] and vol[2] == n[2]:
                        volume = vol[1]
                        break
                total_vol += n[1] * volume
            total_vol /= num
            total_vol = int(cvt_setting[0] / total_vol) / 100
        num = 0
        time_list = []
        note_buffer = {}
        for n, track in enumerate(mid.tracks):
            note_pitch = 0
            notes_delta = 0
            source_time = 0
            first_note = True
            for msg in track:
                tempo = 500000
                for tmp in tempo_list:
                    if tmp[0] <= source_time:
                        tempo = tmp[1]
                        break
                delta_time = tick2second(msg.time, mid.ticks_per_beat, tempo) * 2000 / cvt_setting[2]
                notes_delta += delta_time
                source_time += delta_time
                if msg.type == "note_on":
                    if notes_delta >= cvt_setting[4]:
                        first_note = True
                        notes_delta = 0
                        note_pitch = 0
                    channel = msg.channel
                    velocity = msg.velocity
                    if velocity != 0:
                        volume = 1
                        for vol in volume_list:
                            if vol[0] <= source_time and vol[2] == channel:
                                volume = vol[1]
                                break
                        balance = ""
                        for bal in balance_list:
                            if bal[0] <= source_time and bal[2] == channel:
                                balance = bal[1]
                                break
                        program = asset_list["setting"]["asset"]["sound_list"]["undefined"]
                        for typ in channel_type:
                            if typ[0] <= source_time and typ[2] == channel:
                                program = typ[1]
                                break
                        velocity = int((velocity / 1.27) * volume * total_vol) / 100
                        note = msg.note - 21
                        tick_time = int(round(source_time)) - offset_time
                        if cvt_setting[5] == 1:
                            append_num = 2
                        elif cvt_setting[5] == 2:
                            append_num = 2
                        else:
                            append_num = 0
                        if cvt_setting[5] == 0 or num <= h - append_num:
                            if first_note and note >= note_pitch:
                                first_note = False
                                if not note_buffer.get(tick_time):
                                    note_buffer[tick_time] = []
                                if cvt_setting[5] == 0:
                                    raw_text = asset_list["setting"]["asset"]["command_delay"]
                                elif cvt_setting[5] == 1:
                                    raw_text = asset_list["setting"]["asset"]["command_clock"]
                                elif cvt_setting[5] == 2:
                                    raw_text = asset_list["setting"]["asset"]["command_address"]
                                else:
                                    raw_text = ""
                                raw_text = raw_text.replace("{SOUND}", str(program)).replace("{BALANCE}", str(balance)).replace("{VOLUME}", str(velocity)).replace("{PITCH}", str(asset_list["setting"]["asset"]["note_list"][note])).replace("{TIME}", str(tick_time)).replace("{ADDRESS}", str(play_id))
                                note_buffer[tick_time].append(raw_text)
                                if tick_time not in time_list:
                                    time_list.append(tick_time)
                        num += 1
                        progress += 1
                        progress_bar(message_id, midi_name[0:-4] + " 转换正在进行", progress, total)
        time_list.sort()
        if cvt_setting[5] == 1:
            note_buffer[time_list[-1]].append("/scoreboard players set @a[scores={MMS_Service="
                                              + str(time_list[-1])
                                              + "..}] MMS_Service -1"
                                              )
            note_buffer[time_list[-1]].append("/scoreboard players add @a[scores={MMS_Service=!-1}] MMS_Service 1")
            if cvt_setting[7] == 1:
                total += 2
        elif cvt_setting[5] == 2:
            note_buffer[time_list[-1]].append("/scoreboard players set @a[scores={MMS_Service="
                                              + str(time_list[-1]) + "..,"
                                              + "MMS_Address=" + str(play_id) + "}] MMS_Service -1"
                                              )
            note_buffer[time_list[-1]].append("/scoreboard players add @a[scores={MMS_Service=!-1,"
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
                    progress_bar(message_id, midi_name[0:-4] + " 转换正在进行", progress, total)
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
                        progress_bar(message_id, midi_name[0:-4] + " 转换正在进行", progress, total)
                    else:
                        break
                tick_time = source_time
            for n in range(h, -1, -1):
                if n not in del_list:
                    if structure["structure"]["palette"]["default"]["block_position_data"].get(str(n)):
                        del structure["structure"]["palette"]["default"]["block_position_data"][str(n)]
                    structure["structure"]["block_indices"][0][n] = TAG_Int(air_palette)
                    structure["structure"]["block_indices"][1][n] = TAG_Int(-1)
                    progress += 1
                    progress_bar(message_id, midi_name[0:-4] + " 转换正在进行", progress, total)
            with open(output_name + ".mcstructure", "wb") as io:
                structure.save(io, little_endian=True)
        else:
            if not path.exists(output_name):
                makedirs(output_name)
            if not path.exists(output_name + "/functions"):
                makedirs(output_name + "/functions")
            with open(output_name + "/functions/MMS_Player.mcfunction", "w", encoding="utf-8") as io:
                for source_time in time_list:
                    for cmd in note_buffer[source_time]:
                        io.write(cmd[1:] + "\n")
                        progress += 1
                        progress_bar(message_id, midi_name[0:-4] + " 转换正在进行", progress, total)
            with open(output_name + "/world_behavior_packs.json", "w") as io:
                dump(behavior, io)
            with open(output_name + "/manifest.json", "w") as io:
                dump(manifest, io)
        del mid
        del time_list
        del structure
        del tempo_list
        del volume_list
        del note_buffer
        del channel_type
        del balance_list
        del velocity_list
        collect()
        convertor_state = True
    except Exception:
        save_log(3, "E:", format_exc())
    finally:
        if convertor_state:
            message_list.append((midi_name[0:-4] + " 转换完成", task_id))
        else:
            message_list.append((midi_name[0:-4] + " 转换失败", task_id))

def progress_bar(mess_id, title, pss, tal):
    global message_time
    if len(message_list) != 0 and message_list[0][1] == mess_id:
        if pss == tal:
            if len(message_list) > 1 and message_list[1][1] == mess_id:
                message_time = 3250
            else:
                message_time = 3000
        else:
            message_list[0][0] ="[" + str(int((pss / tal) * 100)) + "%] " + title
            message_time = 0

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
        asset_list["setting"]["setting"]["remove_chord"] = state[3][4]
        asset_list["setting"]["setting"]["mode"] = state[3][5]
        asset_list["setting"]["setting"]["append_number"] = int(state[3][6])
        asset_list["setting"]["setting"]["file_type"] = state[3][7]
        with open("Asset/text/setting.json", "w") as settings:
            dump(asset_list["setting"], settings)
    except Exception:
        save_log(5, "E:", format_exc())

def get_update_log():
    try:
        update_log = load_bytes(get("https://gitee.com/mrdxhmagic/midi-mcstructure/raw/master/Update.json").content)
        n = {"version": 0}
        for i in update_log:
            if int(n["version"]) < int(i["version"]):
                n = i
        del update_log
        if int(n["version"]) > int(asset_list["setting"]["setting"]["version"]):
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
        response = get(state[5]["download_url"], stream=True)
        state[6][1] = int(response.headers['content-length'])
        with open("Asset/update/package.zip", 'ab') as io:
            for chunk in response.iter_content(chunk_size=1024):
                io.write(chunk)
                state[6][0] += len(chunk)
        message_list.append(("下载完成，即将进行更新。", -1))
        state[7] = True
    except Exception:
        state[6] = [0, 0, True]
        message_list.append(("下载失败，请重试。", -1))
        save_log(4, "E:", format_exc())

def setting_help():
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
            message_list.append(("移除所有轨道上的和弦来简化音乐，不建议使用。", -1))
        elif state[1][0] == 5:
            message_list.append(("选择控制播放时序的方式，一般选择低卡顿的命令链延迟。", -1))
        elif state[1][0] == 6:
            message_list.append(("决定是否重命名命令方块名称为音符的序号和音乐名称。", -1))
        elif state[1][0] == 7:
            message_list.append(("决定输出文件类型，mcfunction不支持命令链延迟模式。", -1))
        elif state[1][0] == 8:
            message_list.append(("决定命令链排列方式，均为普通结构文件，用户可自制模板。", -1))

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
            if state[3][4] == 0:
                state[3][4] = 1
            elif state[3][4] == 1:
                state[3][4] = 2
            elif state[3][4] == 2:
                state[3][4] = 3
            elif state[3][4] >= 3:
                state[3][4] = 0
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
            if state[3][7] >= 2:
                state[3][7] = 0
        elif asset_list.get("structure_file") and state[1][0] == 8:
            state[3][1] += 1
            if state[3][1] >= len(asset_list["structure_file"]):
                state[3][1] = 0
    elif state[0] == 5:
        if state[6][2] and state[1][0] == 0:
            Thread(target=download).start()
            state[6][2] = False

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

def to_alpha(origin_surf, color_value):
    alpha_surf = Surface(origin_surf.get_size(), SRCALPHA)
    alpha_surf.fill(color_value)
    origin_surf.blit(alpha_surf, (0, 0), special_flags=BLEND_RGBA_MULT)
    return origin_surf

def uuid(n):
    cmd = ""
    while not n == 0:
        cmd += str(hex(randint(0, 15)))[2:]
        n -= 1
    return cmd

def setting_blit(setting):
    global real_position
    color = [[0, 0, 0, 0], asset_list["setting"]["setting"]["color"][0], asset_list["setting"]["setting"]["color"][1]]
    file_offset = 0
    setting_num = len(setting)
    if setting_num == 0:
        state[1] = [0, 0, -1]
        setting.append(("无可选文件或选项", 4))
    else:
        if state[1][0] >= setting_num:
            if state[4]:
                state[1] = [setting_num - 1, 10, state[1][2]]
            else:
                state[1] = [0, 0, state[1][2]]
        elif state[1][0] < 0:
            if state[4]:
                state[1] = [0, 0, state[1][2]]
            else:
                state[1] = [setting_num - 1, 10, state[1][2]]
        if state[1][0] >= state[1][1]:
            file_offset = state[1][0] - state[1][1]
    file_position = int(DisplaySize[1] * 0.023 + (state[1][0] - file_offset) * 39)
    real_position -= (real_position - file_position) * speed
    window.blit(asset_list["set_pic"], (DisplaySize[0] * 0.01, real_position))
    delta_position = int(abs(file_position - real_position)) / int(DisplaySize[1] * 0.0625)
    for a, b in enumerate(setting[(0 + file_offset):(11 + file_offset)]):
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
            if delta_position <= 1:
                color[0] = (color[1][0] - (color[1][0] - color[2][0]) * delta_position,
                            color[1][1] - (color[1][1] - color[2][1]) * delta_position,
                            color[1][2] - (color[1][2] - color[2][2]) * delta_position,
                            color[1][3] - (color[1][3] - color[2][3]) * delta_position)
            else:
                color[0] = color[2]
        else:
            if a == state[1][2] - file_offset:
                if delta_position <= 1:
                    color[0] = (color[2][0] + (color[1][0] - color[2][0]) * delta_position,
                                color[2][1] + (color[1][1] - color[2][1]) * delta_position,
                                color[2][2] + (color[1][2] - color[2][2]) * delta_position,
                                color[2][3] + (color[1][3] - color[2][3]) * delta_position)
                else:
                    color[0] = color[1]
            else:
                color[0] = color[2]
        window.blit(to_alpha(origin_surface, color[0]), (DisplaySize[0] * 0.025, a * 39 + DisplaySize[1] * 0.039))
        window.blit(to_alpha(asset_list["font"].render(b[0], True, (255, 255, 255)), color[0]), (DisplaySize[0] * 0.065, a * 39 + DisplaySize[1] * 0.044))

log = [[False, True], ["Loading:"], ["Main:"], ["Convertor:"], ["Updater:"], ["Other:"]]

try:
    display.init()
    DisplaySize = (800, 450)
    display.set_icon(image.load("Asset/image/icon.png"))
    window = display.set_mode(DisplaySize)
    display.set_caption("MIDI-MCSTRUCTURE GUI")

    page = []
    file_path = []
    real_path = []
    midi_file = []
    asset_list = {"fps": 60}
    message_list = []
    message_position = DisplaySize[1]
    task_id = 0
    press_time = 0
    message_time = 0
    real_position = 0
    state = [0, [0, 0, -1], "init", [0, 0, 100, True, 0, 0, False, 0], False, None, [0, 0, True], False]

    clock = time.Clock()

    while True:
        for env in event.get():
            if env.type == QUIT:
                exit()
            if env.type == MOUSEBUTTONDOWN:
                state[4] = True
                if env.button == 1:
                    next_page()
                if env.button == 2:
                    setting_help()
                if env.button == 3:
                    last_page()
                if env.button == 4:
                    state[1][2] = state[1][0]
                    state[1][0] -= 1
                    if state[1][1] > 0:
                        state[1][1] -= 1
                if env.button == 5:
                    state[1][2] = state[1][0]
                    state[1][0] += 1
                    if state[1][1] < 10:
                        state[1][1] += 1
            if env.type == KEYUP:
                state[4] = False
                if env.key == K_ESCAPE:
                    exit()
                if env.key == K_TAB:
                    setting_help()
                if env.key == K_DOWN:
                    state[1][2] = state[1][0]
                    state[1][0] += 1
                    if state[1][1] < 10:
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
        if state[7] and len(message_list) == 0:
            Popen(getcwd() + "\\updater.exe")
            exit()
        speed = clock.get_fps()
        if speed > 10:
            speed = 10 / speed
        else:
            speed = 1
        if state[0] == 0:
            Thread(target=asset_load).start()
            Thread(target=get_update_log).start()
            asset_list["load_pic"] = image.load("Asset/image/loading.png")
            asset_list["load_pic"] = transform.scale(asset_list["load_pic"], DisplaySize).convert_alpha()
            state[0] = 1
        elif state[0] == 1:
            window.blit(asset_list["load_pic"], (0, 0))
            if state[2] != "init":
                window.blit(asset_list["font"].render(state[2], True, (63, 63, 63)), (DisplaySize[0] * 0.415, DisplaySize[1] * 0.75))
        elif state[0] == 2:
            file_path = []
            for c in GetLogicalDriveStrings().split("\000")[:-1]:
                file_path.append(c[0:-2] + ":/")
            for c in listdir():
                if path.splitext(c)[1] == ".mid":
                    file_path.append(c)
            state[0] = 3
        elif state[0] == 3:
            window.blit(asset_list["menu_pic"], (0, 0))
            setting_text = []
            for c in file_path:
                if path.splitext(c)[1] == ".mid":
                    setting_text.append((c, 3))
                else:
                    setting_text.append((c, 0))
            if len(page) == 0 and not state[5] is None:
                setting_text.append(["发现新版本 V" + str(state[5]["version"])[:-1], 6])
                if str(state[5]["version"])[-1] == "1":
                    setting_text[-1][0] += "REL"
                else:
                    setting_text[-1][0] += "DEV"
            setting_blit(setting_text)
        elif state[0] == 4:
            window.blit(asset_list["menu_pic"], (0, 0))
            setting_text = ([["开始转换  ", 2], ["音量均衡  ", 1], ["播放速度  ", 1], ["静音跳过  ", 1],
                             ["禁用和弦  ", 1], ["播放模式  ", 1], ["添加序号  ", 1], ["输出模式  ", 1],
                             ["结构模板  ", 1]])
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
            if state[3][4] == 0:
                setting_text[4][0] += "关"
            elif state[3][4] == 1:
                setting_text[4][0] += "弱"
            elif state[3][4] == 2:
                setting_text[4][0] += "中"
            elif state[3][4] == 3:
                setting_text[4][0] += "强"
            else:
                setting_text[4][0] += str(state[3][4]) + "tick"
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
                setting_text[7][0] += ".mcfunction"
                if state[3][5] == 0:
                    setting_text[5][1] = 4
            if asset_list.get("structure_file"):
                setting_text[8][0] += asset_list["structure_file"][state[3][1]][1]
            setting_blit(setting_text)
        elif state[0] == 5:
            window.blit(asset_list["menu_pic"], (0, 0))
            if state[6][1] == 0:
                setting_text = [["立即更新  V", 2]]
            else:
                setting_text = [["正在下载  V", 2]]
            setting_text[0][0] += str(state[5]["version"])[:-1]
            if str(state[5]["version"])[-1] == "1":
                setting_text[0][0] += "REL"
            else:
                setting_text[0][0] += "DEV"
            if state[6][1] != 0:
                setting_text[0][0] += "  [" + str(round(state[6][0] / 1048576, 2)) + "/" + str(round(state[6][1] / 1048576, 2)) + "MB]"
            setting_text += state[5]["feature"]
            setting_blit(setting_text)
        if state[0] != 0:
            if len(message_list) != 0:
                message_time += clock.get_time()
                if message_time >= 3000:
                    message_position -= (message_position - int(DisplaySize[1])) * speed
                else:
                    message_position -= (message_position - int(DisplaySize[1] * 0.9)) * speed
                window.blit(asset_list["msg_pic"], (0, message_position))
                window.blit(asset_list["font"].render(message_list[0][0], True, (255, 255, 255)), (DisplaySize[0] * 0.01, message_position + 8))
                if message_time >= 3250:
                    message_time = 0
                    message_position = DisplaySize[1]
                    del message_list[0]
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
