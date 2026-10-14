# 自制机固件：固定版本、接线与验收

本流程针对社区固件 **v1.1.0**，不是 M5Stack 出厂固件。配置及驱动经过静态检查和模拟协议测试；本仓库尚未完成实物整机验证。官方 K151 使用专用 `m5stackchan_cores3` 目标，自制 CoreS3 使用通用 `m5stack_cores3` 目标，两者不可按“芯片相同”互换。

## 1. 台架接线

先不装摇臂、不合外壳。主机经 USB 供电；舵机使用独立稳压 5V 电源并与主机共地。XL330 双舵机建议预留至少 3A，SCS0009/SG90 按所购型号的启动、堵转电流和实际压降选电源；首次用限流电源逐只试机。**独立电源的 +5V 不与主机 +5V 直接并接**，也不把舵机接到 3V3。使用 m5-pantilt 的 J7 供电则遵守其电源路径，不另接一条并联电源。

| 主机/接法 | TX 或 pan | RX 或 tilt | 配置文件 |
|---|---|---|---|
| CoreS3 + 外置 UART→TTL 半双工转换器 + SCS0009 | GPIO6 TX | GPIO7 RX | `cores3-scs0009.json` |
| CoreS3 + m5-pantilt 串行模式 + XL330 | GPIO17 TX | GPIO18 RX | `cores3-xl330.json` |
| Core Basic/Gray，SG90 直插扩展 Port.C | GPIO16 pan | GPIO17 tilt | `core-sg90-portc.json` |
| Core2，SG90 直插 Port.A | GPIO33 pan | GPIO32 tilt | `core2-sg90-porta.json` |
| Core Basic/Gray + m5-pantilt PWM，R9/R11 | GPIO5 pan | GPIO2 tilt | `core-sg90-board.json` |
| Core2 + m5-pantilt PWM，R10/R12 | GPIO19 pan | GPIO27 tilt | `core2-sg90-board.json` |
| CoreS3 + m5-pantilt PWM，R10/R12 | GPIO7 pan | GPIO6 tilt | `cores3-sg90-board.json` |

CoreS3 的外部 Port.C 为 GPIO17/18；GPIO16 是摄像头信号，不能沿用旧 Core 的 17/16 组合。按 [厂家 M5-Bus 观察方向](https://docs.m5stack.com/en/core/CoreS3)，21/22=GPIO6/7、1/3/5=GND、28=5V，**26=GPIO14，不是 GND**。KiCad 排针编号从另一观察方向绘制，应以 GPIO/网络及物理位置核对：插入前断电，测出板上 DI/RO 与主机引出的 TX/RX 连通关系，不能混用两张图的数字。

串行转换器须明确具有 **3.3V UART TX/RX 输入输出、TTL 单线 DATA 侧、发送释放/接收时序**。不能使用 RS-485 A/B 模块代替，也不能短接普通 USB-TTL 的 TX/RX，更不能使用旧版 RX 串二极管的接法。URT-1 / U2D2 是电脑配置工具，不能默认当作主机 UART 转换器。m5-pantilt 使用 R13/R14 串行跳线，R9-R12 全不装；PWM 则反过来。

## 2. 准备固定版本源码

```bash
git clone --branch v1.1.0 --recurse-submodules https://github.com/stack-chan/stack-chan.git stack-chan-firmware
cd stack-chan-firmware/firmware
npm i
npm run setup
npm run setup -- --device=esp32
npm run doctor
```

以下命令都在这个 `firmware` 目录执行。将 `GUIDE_DIR` 换成你本机本指南的绝对路径；包含空格的路径必须保留引号。

```bash
GUIDE_DIR="/absolute/path/to/stackchan-diy-guide"
cp "$GUIDE_DIR/firmware-configs/cores3-xl330.json" host/app/manifest_local.json
```

根据上表替换配置文件名。D/E 路线还必须复制标定驱动：

```bash
cp "$GUIDE_DIR/firmware-configs/cores3-scs0009.json" host/app/manifest_local.json
cp "$GUIDE_DIR/firmware-configs/scservo-calibrated-driver.js" host/app/
```

该 manifest 用 `modules.scservo-driver` 替换上游同名模块。**原版 scservo 不传递 `driver.serial`、不读取 `offsetPan/offsetTilt`，且固定按 200° 换算；本指南的替换驱动明确传递串口、使用 raw 位置和可配置量程。不要只复制 JSON 而漏掉驱动。**

## 3. 市售 SCS0009 标定

配置起点是 ID1/ID2、1Mbps、300°/1024 步、raw 零位 512。它是所附市售规格书的起始假设，不适用于未经确认的 K151 定制舵机或 STS/SMS 系列。

1. 用 URT-1 和飞特软件一次连接一只，确认型号、ID、波特率；第二只写 ID2，掉电重读。不要使用未经确认的 Recovery。
2. 不装摇臂，发 raw=512，确认轴位置；断电装摇臂，使头部正前方水平。不要把 raw=512 当作所有舵机的绝对 90°。
3. 用小 raw 增量量角。例如 300°/1024 规格下，34 步约为 10°。按测量修正 `angleRangeDegrees`，反向则改对应 `panDirection` / `tiltDirection` 为 1。
4. 零位用 `panZeroRaw` / `tiltZeroRaw` 调整，当前默认活动范围 pan ±10°、tilt ±5°。扩大 `panMin/Max`、`tiltMin/Max` 前实测机身干涉；这些是相对装配零位的角度，不能把 K151 整机的绝对 5-85°直接填进来。

本驱动用 raw 命令绕过上游 200° 换算，并对输出限位。它保留串行应答错误，**未增加电流/温度读取或固件堵转保护**；舵机自身保护也不代替机械限位。

CoreS3 若使用 m5-pantilt 串行板带 SCS0009，将配置中的 TX/RX 改为 17/18；旧 Core 通常为 17/16、Core2 为 14/13，但仍须按所用板实测连通性。波特率保持 1Mbps，只有实测需要时才同时修改主机与舵机，不因旧文档的“≤115200”说法单方面降速。

## 4. 构建及烧录

官方 v1.1.0 的默认 `npm run flash` / `deploy` 读取 K151 manifest，不读取上面修改的本地 manifest。此处使用官方 `run-mcconfig.mjs` 包装器，明确指定通用主机及本地配置：

```bash
# CoreS3（B/D/E，或 CoreS3 PWM）
node scripts/run-mcconfig.mjs -m -p esp32/m5stack_cores3 -t build "$PWD/host/app/manifest_local.json"
# Core Basic/Gray（C，二选一，不要全执行）
node scripts/run-mcconfig.mjs -m -p esp32/m5stack -t build "$PWD/host/app/manifest_local.json"
# Core2（C，二选一，不要全执行）
node scripts/run-mcconfig.mjs -m -p esp32/m5stack_core2 -t build "$PWD/host/app/manifest_local.json"
```

以实际主机选择其中一行，构建成功后检查 `dist/bin/esp32/<主机目标>/release/stack-chan-host/` 的三个 bin。先核对唯一串口，按需备份 flash/NVS；将 `PORT` 换成实际串口，例如 Linux `/dev/ttyACM0` 或 macOS `/dev/cu.usbmodem...`。

```bash
# CoreS3 的 ESP32-S3 布局
PORT="/dev/ttyACM0"
OUT="dist/bin/esp32/m5stack_cores3/release/stack-chan-host"
esptool --chip esp32s3 --port "$PORT" write_flash \
  0x0 "$OUT/bootloader.bin" 0x8000 "$OUT/partition-table.bin" 0x10000 "$OUT/xs_esp32.bin"
```

Core Basic/Gray 或 Core2：`--chip esp32`，bootloader 偏移为 `0x1000`，`OUT` 分别改成 `m5stack` 或 `m5stack_core2` 的输出目录，其余两个偏移相同。若更换驱动类型，先通过设置清除/修改旧的持久化 `driver.type`，否则 NVS 设置可能覆盖 manifest；不要为此未经备份就擦除整个 flash。

离线包中的通用 Core/Core2 默认不保证是 PWM，CoreS3 默认 Dynamixel 串口也不是这块板的 17/18。B/C/D/E 推荐按上述自定义配置构建；不要承诺网页选主机型号后舵机自动匹配。K151 专用预编译包只用于官方整机。

## 5. 无按键小范围验收

先保持摇臂拆下或机身运动空间无遮挡，安装本指南的小范围 MOD：

```bash
mkdir -p mods/diy-smoke
cp "$GUIDE_DIR/firmware-configs/diy-smoke/manifest.json" mods/diy-smoke/
cp "$GUIDE_DIR/firmware-configs/diy-smoke/mod.js" mods/diy-smoke/
# ESP32-S3：此命令只编译并写入 MOD，不重新刷 K151 host
npm run mod:m5stackchan_cores3 -- mods/diy-smoke/manifest.json --port "$PORT"
# ESP32 Core/Core2 用同芯片 MOD 目标，替代上一行
# npm run mod:takao_core2_sg90 -- mods/diy-smoke/manifest.json --port "$PORT"
```

MOD 与 host 须使用同一套 Moddable/XS 版本。其代码只用公开 motion API 和 Timer，无 K151/Takao 专用外设；MOD 编译目标只是选择相同芯片的工具链，不改变已烧录的本地 host。若工具提示版本不兼容，停止安装，检查是否混用了另一套 SDK/预编译 host。

重启后执行一次回中、左右各 5°、上下各 3°、回中，随后请求关闭扭矩；串口应出现 `[diy-smoke] complete`，无应答/失败应出现错误。PWM 舵机不能靠该 API 真正断电，装配前必须切断舵机电源。CoreS3 不要求 A/B/C 实体键，也不使用有转头阈值的 `lookAt` 代替小角度 `setPose`。

验收需同时满足：显示正常、ID1/ID2 独立动作且方向正确、串行机可读回位置、无复位/明显压降/异响、线束和外壳在全测试范围内无干涉。仅“会摇头”不足以判断成功。完成台架验收后再装壳，并从小范围重新测试。

## 依据与版本边界

- [v1.1.0 package.json](https://github.com/stack-chan/stack-chan/blob/v1.1.0/firmware/package.json)：通用构建脚本及 MOD 工具。
- [K151 平台](https://github.com/stack-chan/stack-chan/blob/v1.1.0/firmware/host/platforms/m5stackchan_cores3/manifest.json)：锁定驱动、GPIO6/7、PY32 电源及专用零位。
- [上游 SCServo 协议](https://github.com/stack-chan/stack-chan/blob/v1.1.0/firmware/host/modules/motion/protocols/scservo.ts)：raw 命令和应答接口。
- [CoreS3 PinMap](https://docs.m5stack.com/en/core/CoreS3)、[XL330 参数与通信电路](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/)。

升级社区固件后重新核对 manifest 合并顺序、MotionDriver 接口和构建输出；本地标定驱动不是官方上游固件的一部分。
