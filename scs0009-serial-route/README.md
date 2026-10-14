# 路线 D：SCS0009 串行舵机机身（国产串行总线 · 免打板也能玩）

> **Feetech SCS0009 串行舵机 ×2 + 官方专用机身 + M5Stack 主机**。这是官方仓库认可的"国产串行舵机"路线：
> 舵机深圳飞特（Feetech）出品、淘宝直购，能读角度、限流限速、有全状态反馈，比 SG90 高一个档次，比 XL330 便宜且好买。
> 附 **RS30X（Futaba）变体**（日规串行舵机，同思路）。
> 预算约 **¥350–550**（含主机），工期 1 个周末。

## 0. 本路线一览

| 项 | 内容 |
|---|---|
| 主机 | M5Stack CoreS3 / Core2 / Core Basic（配官方底板串行模式） |
| 舵机 | Feetech SCS0009 ×2（串行 TTL，半双工） |
| 驱动方式 | 官方底板串行模式（R13/R14），或二极管半双工直连（免板） |
| 打印件 | `stl/scs0009/`（4 件，官方专用机身） |
| 固件驱动 | `scservo`（panId/tiltId） |
| 参考角（正前） | **100°**，可动 0–200° |
| 难度 | ★★★ |

**为什么选它**：串行总线架构（和官方 K151 整机同款舵机型号）、官方全套专用打印件、舵机国产好买。代价：改 ID 要 URT-1 调试器（一次性 ¥100 上下）；SCS0009 出厂默认 1Mbps 与官方固件 scservo 驱动匹配需核对。

---

## 1. 物料清单（BOM）

| 物品 | 数量 | 参考价(¥) | 说明 |
|---|---|---|---|
| SCS0009 舵机 | 2 | 80–120/个 | 飞特淘宝店/代理；金属齿 2.3kg·cm、300° 量程、全反馈 |
| **URT-1 调试器** | 1 | ~100 | 一次性投入：改 ID/波特率用，飞特配套 |
| M5Stack 主机 | 1 | 100–250 | CoreS3 / Core2 / Core Basic 均可 |
| 官方底板 | 1 | 打样 ¥30 | 串行模式（见 §3.1）；或免板直连（§3.2） |
| 电池 + 耗材 | — | 30–50 | 同 [v0 路线 §1.2](../v0-sg90-route/README.md#12-耗材)，3.7V 400–640mAh PH2.0 |
| 舵机延长线 | 2 | — | SCS0009 配套 3P 线，长短按机身走线 |

### 1.1 打印件（本包 `stl/scs0009/`）

shell_SCS0009、feet_SCS0009、bracket_SCS0009_f、bracket_SCS0009_b。

- **强烈建议直接用这套官方专用机身**：SCS0009 圆形安装法兰原生吻合，含齿轮传动件；别拿 SG90 壳硬改。
- 打印参数同通用（PLA、0.2mm、薄壁 3 层周壁，方向见 [v0 路线](../v0-sg90-route/README.md#13-打印件本包-stlv0-sg90)）。
- STEP 源文件在官方仓库 `case/case_SCS0009/`（同名 .step）。

---

## 2. 舵机初始化（关键步骤，装壳前做完）

1. **两颗舵机设不同 ID**：ID1 = 脚/pan（水平），ID2 = 脸/tilt（垂直）。信号线接法：

   ![SCS0009 接线](images/scservo_cable_connection.jpg)

2. 用 **URT-1 调试器 + 飞特官方 GUI（fddebug）** 改 ID 和角度：

   ![ID 设置](images/id.jpg)

3. **注意**：官方提醒**不要用飞特 GUI 的 "Recovery"**（已知会导致舵机工作异常）。
4. 改完 ID 后**一次只连一颗**验证（同 ID 冲突会连不上）。

> SCS0009 规格：300°/1024 步（约 0.293°/步）、330° 传感器、2.3kg·cm、6V、半双工 TTL、出厂默认 1Mbps、ID 范围 0–253、中位 90°（值 511）。完整数据手册：[`../k151-body-route/datasheets/SCS0009_Feetech_Servo.pdf`](../k151-body-route/datasheets/SCS0009_Feetech_Servo.pdf)。

---

## 3. 电气连接（两种玩法）

### 3.1 官方底板串行模式（推荐）

用官方 `m5-pantilt` 底板，**制造文件已生成好**：[`pcb/m5-pantilt-v1.0/manufacture/jlcpcb/`](../pcb/m5-pantilt-v1.0/manufacture/)（Gerber zip + LCSC 号 BOM + 坐标 + 下单说明）。

**串行模式跳线（关键）**：**只装 R13/R14（0Ω）**——R13 把 J3/J8 数据线并成一条半双工总线，R14 接到 MAX3485 收发线（自动换向，CoreS3 的 G17/G16）。**R9–R12 不装**（那是 PWM 模式的 Core 型号选择跳线）。

串行版实拍：

| 端口 | 开关 | 2x15 排座 |
|---|---|---|
| ![serial ports](images/serial_ports.jpg) | ![serial switch](images/serial_switch.jpg) | ![serial 2x15](images/serial_2x15.jpg) |

舵机接 J3/J8（JST EH 3P 口），电池 J5，主机插 J1（背面，注意方向）。

### 3.2 免板直连：二极管半双工（K151 同款思路）

不想打板：TX/RX 各串一个二极管（1N4148）合成半双工总线，详细接线图与原理见 [K151 机身路线 §二极管半双工](../k151-body-route/README.md)（K151 机身用同款舵机，接线完全通用）。固件配置同样用 `scservo` 驱动。

---

## 4. 机械装配

1. 舵机 ID 改好、固件刷好、**两颗舵机停在中位、方向验证正确**之后才动壳（铁律）。
2. 摇臂/齿轮对准**参考角 100°**（SCS0009 正前方）。
3. 其余流程同 [v0 路线 §3](../v0-sg90-route/README.md#3-机械装配官方动图流程)：bracket 卡舵机 → feet/shell 锁螺丝 → 接线留余量 → 底板 M2×4×4 锁机身 → 插主机。
4. 接线理顺、留活动余量，别让线卡住旋转。

---

## 5. 固件

- **刷机**：网页刷机 https://stack-chan.github.io/stack-chan/web/flash/ 选对应主机目标（CoreS3 → `M5Stack CoreS3`，或离线包 `com.m5stack.*` 系列，esptool 用法见 [v0 路线 §4.1](../v0-sg90-route/README.md#41-刷机三选一)）。
- **驱动配置**（`manifest_local.json`）：

```json
{
  "include": ["./manifest.json"],
  "config": {
    "driver": {
      "type": "scservo",
      "panId": 1,
      "tiltId": 2
    }
  }
}
```

- 用官方底板串行模式时若方向收发异常，先核对 R13/R14 焊接；`offsetPan/offsetTilt`（−90~90）可微调机械零位。
- **验收**：A 键随机看、B 键四方看、C 键反色；会摇头 = 驱动 OK。SCS0009 有位置反馈，还可以跑 `calibration` 示例 MOD 做精确校准（见 [firmware-docs/](../firmware-docs/README.md)）。

> ⚠️ 安全须知（官方原文）：**Y 轴（垂直/脖子）舵机角度控制在 5°–85°**，超限可能堵转并造成永久损坏；不确定通电状态时禁止用手硬掰。

---

## 6. 变体：RS30X（Futaba，日规串行舵机）

同一思路的日本品牌版本（Vstone/Best Solution RS30X / RS304MD）：

- 参考角 **0°**（可动 −150~150°），与 SCS0009 的 100° 不同，摇臂对位注意。
- 国内需代购/转运（约 3000 日元+/颗），不推荐国内用户优先选。
- 打印件本包已带：`stl/rs30x/`（shell_RS30X、feet_RS30X、bracket_RS30X）。
- 固件驱动 `rs30x`；官方示例 MOD `setup_rs30x` 可做初始化（见 [firmware-docs/](../firmware-docs/README.md)）。
- 底板同样走串行模式（R13/R14）。

---

## 7. 相关路线

- 同款舵机的"官方整机拆解复刻"路线：[K151 机身路线](../k151-body-route/README.md)（含 K151 机身 + 开源 PCB 混合玩法）
- 更高阶的 Dynamixel 串行路线：[v1.0 + XL330](../v1-xl330-route/README.md)
- 预算优先的 PWM 路线：[v0 + SG90](../v0-sg90-route/README.md)
