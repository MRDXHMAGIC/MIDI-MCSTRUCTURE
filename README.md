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

4. 禁用和弦
本意是用于简化音乐，因效果极差已被废弃。

5. 播放模式
共有三种模式，分别为命令链延迟(delay)、计分板时钟(clock)和时钟与编号(address)。

| 播放模式  | 实现方式                    | 优点         | 缺点     |
|-------|-------------------------|------------|--------|
| 命令链延迟 | 通过命令方块自带的执行延迟控制播放       | 低卡顿        | 不易控制播放 |
| 计分板时钟 | 通过计分板计时控制播放             | 易控制播放      | 高卡顿    |
| 时钟与编号 | 在计分板时钟基础上，为每次分配一个不重复的ID | 易控制播放，支持多人 | 高卡顿    |

补充：
MIDI-MCSTRUCUTRE支持自定义命令，修改配置文件([setting.json](https://gitee.com/mrdxhmagic/midi-mcstructure/raw/master/Asset/text/setting.json))的内容即可更改指令。
默认指令（使用基岩版举例）如下：

```
{
"command_delay": "/execute as @a at @s run playsound {SOUND} @s ^{BALANCE}^^ {VOLUME} {PITCH} {VOLUME}", 
"command_clock": "/execute as @a[scores={MMS_Service={TIME}}] at @s run playsound {SOUND} @s ^{BALANCE}^^ {VOLUME} {PITCH} {VOLUME}", 
"command_address": "/execute as @a[scores={MMS_Service={TIME},MMS_Address={ADDRESS}}] at @s run playsound {SOUND} @s ^{BALANCE}^^ {VOLUME} {PITCH} {VOLUME}"
}
```

程序会自动识别命令链方向，依次写入指令。其中{SOUND}用于获取乐器ID；{BALANCE}用于获取左右声道平衡信息（MIDI文件中不存在平衡信息时为空）；{VOLUME}用于获取音量；
{PITCH}用于获取音高（[数据来源](https://b23.tv/mQuuE1T)）；{TIME}用于获取现在的时间（仅限计分板时钟和时钟与编号模式，命令链延迟模式会将间隔写入到执行延迟中）；
{ADDRESS}用于获取一个唯一的编号（每一次转换的文件内该值相同，每个文件之间不同）。在写入指令时以上关键字会被替换为对应的信息。

命令开头务必以/开头。因为mcfunction中不允许以/开头，程序无论指令是否以/开头都会去除指令模板中的第一个字。

6. 添加序号
向第一个命令方块备注中写入音乐名称，其余写入序号。

7. 输出模式
共有四种模式，分别为mcstructure(BE)，mcfunction(BE)，mcfunction(JE)，MMS串口设备。

mcstructure(BE)生成基岩版结构文件；mcfunction(BE)/mcfunction(JE)生成基岩版/Java版函数文件和配置文件，其中基岩版还会生成中国版所需的world_behavior_packs.json，
函数模式下不可使用命令链延迟模式，因为函数不支持执行间隔；MMS串口设备会向已选择的串口设备以特定形式传输音乐数据。

所有文件均输出到程序运行文件夹下，文件是以BE/JE开头加随机的八位十六进制数字的文件或文件夹。