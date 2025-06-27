# MIDI-MCSTRUCTURE_V2
![MMS Icon](MMS_Icon.png)

#### 介绍
MIDI转我的世界基岩版mcstructure，Java版或基岩版mcfunction。

#### 特性
- 支持将MIDI转为mcstructure或mcfunction。
- 支持丰富的功能，例如mcstructure模板，自定义指令和MIDI乐器功能。
- 图形化界面，简洁实用。

### 使用
1. 音量均衡
使音乐中的平均音量与设定值一致，某音符音量大于大于1时将会被调整为1。

2. 播放速度
调整音乐的速度，可用于抵消游戏的卡顿或根据喜好调整。

3. 静音跳过
当音乐开头存在无音符的片段时，自动去除。

4. 禁用和弦（打击乐器）
本意是用于简化音乐，因效果极差已被废弃，最新版已替换为控制打击乐器选项。

5. 播放模式
共有三种模式，分别为命令链延迟(delay)、计分板时钟(clock)和时钟与编号(address)。

| 播放模式  | 实现方式                    | 优点         | 缺点     |
|-------|-------------------------|------------|--------|
| 命令链延迟 | 通过命令方块自带的执行延迟控制播放       | 低卡顿        | 不易控制播放 |
| 计分板时钟 | 通过计分板计时控制播放             | 易控制播放      | 高卡顿    |
| 时钟与编号 | 在计分板时钟基础上，为每次分配一个不重复的ID | 易控制播放，支持多人 | 高卡顿    |

补充：
MIDI-MCSTRUCUTRE支持自定义命令，修改默认配置文件([default.json](https://gitee.com/mrdxhmagic/midi-mcstructure/raw/master/Asset/text/setting.json))的内容或新建一个配置文件即可更改指令。
所有配置文件存储在[Asset/profile](https://gitee.com/mrdxhmagic/midi-mcstructure/tree/master/Asset/profile)文件夹中，可自行修改或增加配置文件。
默认指令（使用基岩版举例）如下：

```
{
"command_delay": "/execute as @a at @s run playsound {SOUND} @s ^{BALANCE}^^ {VOLUME} {PITCH} {VOLUME}", 
"command_clock": "/execute as @a[scores={MMS_Service={TIME}}] at @s run playsound {SOUND} @s ^{BALANCE}^^ {VOLUME} {PITCH} {VOLUME}", 
"command_address": "/execute as @a[scores={MMS_Service={TIME},MMS_Address={ADDRESS}}] at @s run playsound {SOUND} @s ^{BALANCE}^^ {VOLUME} {PITCH} {VOLUME}"
}
```

程序会自动识别命令链方向，依次写入指令。其中{SOUND}用于获取乐器ID；{BALANCE}用于获取左右声道平衡信息（MIDI文件中不存在平衡信息时为空）；{VOLUME}用于获取音量；
{PITCH}用于获取音高；{TIME}用于获取现在的时间（仅限计分板时钟和时钟与编号模式，命令链延迟模式会将间隔写入到执行延迟中）；
{ADDRESS}用于获取一个唯一的编号（每一次转换的文件内该值相同，每个文件之间不同）。在写入指令时以上关键字会被替换为对应的信息。

另外，在计分板时钟或时钟与编号模式下MMS软件会在命令链最后添加两条计时指令。

注意，命令开头务必以/开头。因为mcfunction中不允许以/开头，程序无论指令是否以/开头都会去除指令模板中的第一个字。

6. 添加序号
向第一个命令方块备注中写入音乐名称，其余写入序号。

7. 输出模式
共有四种模式，分别为mcstructure(BE)，mcfunction(BE)，mcfunction(JE)，MMS串口设备。

mcstructure(BE)生成基岩版结构文件；mcfunction(BE)/mcfunction(JE)生成基岩版/Java版函数文件和配置文件，其中基岩版还会生成中国版所需的world_behavior_packs.json，
函数模式下不可使用命令链延迟模式，因为函数不支持执行间隔；MMS串口设备会向已选择的串口设备以特定形式传输音乐数据。

所有文件均输出到程序运行文件夹下，文件是以BE/JE开头加随机的八位十六进制数字的文件或文件夹。

8. 结构模板
通过结构模板功能，可以自定义生成的命令链的形状和排列方式，以及集成适合特定指令系统的指令来实现导入即用的效果。

模板存储在[Asset/mcstructure](https://gitee.com/mrdxhmagic/midi-mcstructure/tree/master/Asset/mcstructure)中，可直接导入至游戏来观察如何制作一个模板。

在模板中，命令方块备注为start代表以该方块为起点开始按命令链方向写入指令，若不备注，将以结构中XYZ坐标最小的方块为起点写入。将命令方块备注为append代表程序将保留该命令方块，
并将命令方块中指令的一些特殊关键字替换：__ADDRESS__替换为为该结构分配的唯一ID（与上文中的{ADDRESS}一致），__TOTAL__替换为总时长（单位为Tick），__NAME__替换为被转换的MIDI文件名（不含.mid后缀）。

9. 音域限制
因Java版不允许播放音调小于0.5或大于2.0，因此转换Java版文件时需调整该选项为限幅或自动。

10. 乐器调整
根据配置文件调整乐这里输入引用文本器的音调和音量，使其效果更自然。如钢琴通常作为主旋律，通过调小钢琴的音量来使伴奏更突出，达到丰富听感的作用。

补充：
所有配置文件存储在[Asset/profile](https://gitee.com/mrdxhmagic/midi-mcstructure/tree/master/Asset/profile)文件夹中，与上文的指令模板在同一个文件中。
大体框架如下：

```
{
  "description": {
    "name": "实例",
    "author": "Project-MMS",
    "feature": [
      "default",
      "java",
      "bedrock"
    ]
  },
  "note_list": [],
  "bedrock": {
    "command": {
      "command_delay": "",
      "command_clock": "",
      "command_address": ""
    },
    "sound_list": {
      "undefined": ["note.harp", 1.0, 1.0],
      "default": ["note.harp", 1.0, 1.0],
      "0": ["note.harp", 0.53, 1.0],
      "percussion": {
        "undefined": ["dig.sand", 1.0, 1.0],
        "31": ["note.hat", 1.0, 1.0]
      }
    }
  },
  "java": {
    "command": {
      "command_delay": "",
      "command_clock": "",
      "command_address": ""
    },
    "sound_list": {
      "undefined": ["block.note_block.harp", 1.0, 1.0],
      "default": ["block.note_block.harp", 1.0, 1.0],
      "0": ["block.note_block.harp", 1.0, 1.0],
      "percussion": {
        "undefined": ["block.sand.break", 1.0, 1.0],
        "31": ["block.note_block.hat", 1.0, 1.0]
      }
    }
  }
}
```

description中是对该文件的描述，其中name是在软件中显示的名称；author是作者名，暂无用处；feature是对文件功能的描述，其中若包含"default"则每次启动软件时都会将该文件作为首选项，包含"old_edition"则启用老版本语法与文件结构，其余字段无用处；note_list是音调，应从首到尾按数字由小到大排序（[默认数据来源](https://b23.tv/mQuuE1T)）；bedrock和java是两个游戏版本的指令和音色配置，其中command具体见上文播放模式，sound_list是音色配置，其中percussion是打击乐器配置，undefined是指定遇到没有配置的乐器时使用的的乐器，default指定每个MIDI通道默认乐器，使用  MIDI乐器编号（字符串）: [游戏音色名称（字符串）, 响度（浮点数）, 音调（浮点数，与原来音调相乘）]  定义乐器。

11. 配置文件
当有多个配置文件时可在软件中选择使用其中的一个配置文件。

### 致谢
排名不分先后！

[孤寡牢宇](https://m.bilibili.com/space/169253838?&unique_k=2333) 指出软件的配置文件中基岩版指令的错误。

[蒙德城的大肥鹅](https://m.bilibili.com/space/1233311179?&unique_k=2333) 指出软件无法处理部分MIDI音乐的问题。

[一只很妙的鸟](https://m.bilibili.com/space/516719165?&unique_k=2333) 建议并帮助软件加入对老版本游戏的支持。

以及任何使用或支持本软件的人！