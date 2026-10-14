# Stack-chan（スタックチャン）手挫指南 · 国内版

> 基于开源仓库 [stack-chan/stack-chan](https://github.com/stack-chan/stack-chan)（main 分支，固件 v1.1.0）与 M5Stack 官方 K151 产品文档（[中文](https://docs.m5stack.com/zh_CN/StackChan)）整理。
> 图片、外壳 STL、KiCad 底板工程与制造文件、离线固件包、官方进阶文档均已入库存档（附录 A），可离线使用。

---

## 1. 项目背景

**Stack-chan** 是石川知也（meganetaaan）发起的开源"超可爱"桌面机器人：M5Stack 屏幕当脸（Avatar 表情库），两颗舵机做俯仰/偏航"脖子"，会点头、摇头、东张西望、说话。硬件（外壳 STL、底板 KiCad 工程）与固件（Moddable SDK 上的 JavaScript/TypeScript，host + MOD 热装架构）全部开源（Apache-2.0）。

![整机外观](images/case.jpg)

2024 年起 M5Stack 推出官方整机 **StackChan（K151）**，淘宝可直购；与此同时开源社区路线（自制外壳 + 底板 + 舵机）依然活跃，两者固件生态互通。

**本仓库**把这些散落在官方仓库各处（case/、schematics/、firmware/docs/）、日本代购渠道、英文/日文文档里的资料，整理成**面向国内玩家的完整自制方案包**：每条路线一个独立目录、自带 BOM/打印件/装配/接线/固件全流程，素材本地化（淘宝采购、嘉立创打样打板、jsdelivr 镜像下载）。

> **零成本预研**：不买任何硬件，先用官方网页工具体验——模拟器 / 积木编辑器 / MOD Gallery（简体中文界面）：https://stack-chan.github.io/stack-chan/web/

---

## 2. 方案总览

按投入从低到高排列；**每个方案目录自带完整流程（选型 → 采购 → 打印 → 装配 → 接线 → 固件 → 验收）**，点进去照做即可。

| 方案 | 名称 | 主机 | 舵机 | 底板 | 预算（含主机） | 难度 | 入口 |
|---|---|---|---|---|---|---|---|
| **A** | K151 官方整机 | CoreS3（整机） | SCS0009 ×2（内置） | 不需要 | ~¥700 | ★ | [`k151-kit-route/`](k151-kit-route/README.md) |
| **B** | v1.0 + XL330 | CoreS3 | Dynamixel XL330-M288 ×2 | 官方板（打样） | ¥600–900 | ★★★★ | [`v1-xl330-route/`](v1-xl330-route/README.md) |
| **C** | v0 + SG90（经典） | Core Basic/Gray/Core2 | SG90/MG90S ×2 | 可选（有零 PCB 变体） | ¥300–500 | ★★★（丐版 ★） | [`v0-sg90-route/`](v0-sg90-route/README.md) |
| **D** | SCS0009 串行机身 | CoreS3/Core2/Core | Feetech SCS0009 ×2 | 可选（有免板变体） | ¥350–550 | ★★★ | [`scs0009-serial-route/`](scs0009-serial-route/README.md) |
| **E** | K151 机身复刻 | CoreS3 | SCS0009 ×2 | 免板（二极管半双工） | ¥450–650 | ★★ | [`k151-body-route/`](k151-body-route/README.md) |
| **F** | 零元体验 | —（网页模拟器） | — | — | ¥0 | — | https://stack-chan.github.io/stack-chan/web/ |

### 方案简介

**A · K151 官方整机** —— 不手挫，淘宝直购官方整机，到手开机即用：550mAh 电池、双反馈舵机、12×RGB、红外、三区触摸、NFC、双 USB-C。配官方 StackChan World App（AI 对话、远程化身）；出厂固件、遥控手柄、App、服务端全开源，随时可刷社区固件再刷回来。适合只想玩/送礼/给自制路线当参考机。

**B · v1.0 + XL330** —— 官方最新一代自制规格：v1.0 外壳 + Dynamixel XL330 串行舵机（速度/扭矩/温度全反馈，1Mbps 总线）。需要 U2D2 调试器给舵机改 ID（一次性投入）。性能天花板，也是官方文档最完善的一条。**最适合"完整手挫"的进阶玩家。**

**C · v0 + SG90** —— 经典中的经典（纸书封面同款造型）：v0 外壳 + 白菜价 SG90 PWM 舵机。含 **丐版直插变体**（已有主机 + 杜邦线，+¥30 半天玩起来）和 **M5GO Bottom 变体**（mongonta 方案）。性价比首选，代价是舵机无反馈、涌流可能拉掉主机电源。

**D · SCS0009 串行机身** —— 官方认可的国产串行舵机路线：飞特 SCS0009（与 K151 整机同款舵机）+ 官方专用打印件，能读角度、限流限速。改 ID 需要 URT-1 调试器。另附 **RS30X（Futaba）日规变体**。串行总线体验的国内友好版。

**E · K151 机身复刻** —— 用 M5Stack 官方开源的 10 件结构 STL 复刻 K151 机身：CoreS3 + 2×SCS0009 二极管半双工直连，免打板。含完整硬件逆向（原理框图/接线/舵机协议）与 **G 混合玩法**（官方机身 + 开源 m5-pantilt 底板）。

**F · 零元体验** —— 官方网页工具（简体中文）：WASM 模拟器跑整机行为、积木编辑器零代码写 MOD、MOD Gallery 现成应用试玩。买硬件前先来这里找感觉。

---

## 3. 方案对比

### 3.1 硬件维度

| 维度 | A 整机 | B v1.0+XL330 | C v0+SG90 | D SCS0009 | E K151 复刻 |
|---|---|---|---|---|---|
| 舵机类型 | 串行（内置） | Dynamixel 串行 | PWM | 串行 TTL | 串行 TTL |
| 位置/状态反馈 | ✅ | ✅ 最强 | ❌ | ✅ | ✅ |
| 免打板 | ✅ | ❌ 需打样 | ✅（丐版） | ✅（直连变体） | ✅ |
| 电池 | ✅ 550mAh 内置 | 背包锂电（可充电） | 背包锂电 / Core2 内置 | 背包锂电 | 机身电池仓 |
| 官方 App 支持 | ✅ 只认官方核心 | ❌ | ❌ | ❌ | ❌ |
| 机身外观 | 官方 K151 | 官方 v1.0 | 官方 v0 经典 | 官方专用件 | 官方 K151 复刻 |
| 魔改自由度 | 低 | 高 | 高 | 高 | 最高（10 件结构件） |

### 3.2 投入维度

| 维度 | A | B | C | D | E |
|---|---|---|---|---|---|
| 预算（含主机） | ~¥700 | ¥600–900 | ¥300–500（丐版 +¥30） | ¥350–550 | ¥450–650 |
| 工期 | 当天 | 1–2 个周末 | 1 个周末（丐版半天） | 1 个周末 | 1 个周末 |
| 需要焊接 | 否 | 少量（贴片/插件） | 丐版无 | 直连变体无 | 二极管直连少量 |
| 一次性工具投入 | 无 | U2D2 ¥200–300 | 无 | URT-1 ~¥100 | 无 |
| 3D 打印 | 不需要 | 需要 | 需要 | 需要 | 需要 |

### 3.3 选型建议

- **只想玩 / 送人 / 预算 ¥700 左右** → **A**
- **第一次手挫、预算敏感** → **C**（先用丐版直插验证兴趣，再补壳）
- **想体验串行总线 + 国产好买** → **D**
- **完整手挫、要最强性能、预算充足** → **B**
- **要官方 K151 造型但想自己造** → **E**（顺带看它的 G 混合玩法）
- **还在犹豫** → **F** 网页模拟器，10 分钟找到感觉

> ⚠️ **通用安全须知（官方原文）**：Y 轴（垂直/脖子）舵机角度控制在 **5°–85°**，超限可能堵转并造成**永久损坏**；X 轴无限制；不确定通电状态时**禁止用手硬掰**任何活动部件。
>
> **通用装配铁律**：① 先刷固件、验证舵机方向正确，再固定进壳；② 摇臂对准各舵机参考角（SG90=90°，SCS0009=100°，RS30X=0°，XL330=设 ID 后正前方）；③ 接线留活动余量。

---

## 4. 通用资源速查

以下内容各方案共用，路线文档里已按需引用/内联，这里做总索引。

### 4.1 采购渠道

| 商品 | 渠道 |
|---|---|
| StackChan 整机（K151）/ 遥控版（K151-R） | 淘宝直链 https://item.taobao.com/item.htm?id=1042238294510 ；官方商城 https://shop.m5stack.com |
| M5Stack 主机（CoreS3 / Core2 / Core） | 官方淘宝店 https://m5stack.taobao.com （现货充足、可开票） |
| SG90/MG90S、杜邦线、螺丝包、PH2.0 线 | 淘宝任意 |
| SCS0009 + URT-1 调试器 | 飞特（Feetech）淘宝店/代理 |
| XL330-M288-T + U2D2 | Robotis 韩国品牌，淘宝代理店 |
| 锂电池 3.7V 400–640mAh（401230/501235，PH2.0-2P） | 淘宝 ¥10–20 |
| PCB 打样 + SMT + 3D 打印 | 嘉立创 https://www.jlc.com ＋ 三维猴 https://3d.jlcpcb.com |

### 4.2 3D 打印

- 打印件清单按路线看各方案 §"打印件"（`stl/` 全目录见附录 A）。
- 通用参数：PLA 即可（PETG 更韧），层高 0.2mm，薄壁件 3 层周壁，约 30–50g。
- **官方推荐打印方向**（摆错强度差很多）：![打印方向](images/print_orientation.jpg)
- 没有打印机：三维猴传 STL 即可 / 淘宝代打按克计费。
- STEP 源文件在官方仓库 `case/` 各目录（与本包 STL 同名）；国内直连不稳可用 jsdelivr，如 `https://cdn.jsdelivr.net/gh/stack-chan/stack-chan@main/case/v1/shell.step`。

### 4.3 官方底板（m5-pantilt）

自制路线 B/C/D 共用的舵机驱动板，**一块板按跳线分 PWM / 串行两种模式**：

| 模式 | 舵机 | 跳线 | 用途 |
|---|---|---|---|
| PWM | SG90 | 装 R9/R11（CoreS3、Core）或 R10/R12（Core2） | 路线 C |
| 串行 | SCS0009/RS30X/XL330 | **只装 R13/R14**（R9–R12 不装） | 路线 B/D |

- 完整 KiCad 工程：`pcb/m5-pantilt-v1.0/`（原理图 PDF + 自定义封装库）。
- **制造文件已生成好**（Gerber zip + 带 LCSC 号 BOM + 贴片坐标 + 下单说明，无需装 KiCad）：[`pcb/m5-pantilt-v1.0/manufacture/`](pcb/m5-pantilt-v1.0/manufacture/README.md) 。
- 核心元件：U1=MAX3485（半双工收发）、Q1=IRLML6402（电源软开关）、Q2=BC857（方向控制）、D1=SS54、D2=PMEG3030EP；J1 在**背面**。
- 电池接 J5（PH2.0），可经 M5Stack 充电；外部 5V 接 J7。
- 老规格（v0.2.1 时代）图纸在官方仓库 tag `v0.2.1`。

### 4.4 固件刷法（四选一）

| 方式 | 门槛 | 适合 |
|---|---|---|
| [网页刷机 WebSerial](https://stack-chan.github.io/stack-chan/web/flash/) | 零环境 | 99% 的人，首选 |
| 离线 zip + esptool（本包 [`firmware/stack-chan-firmware-v1.1.0.zip`](firmware/stack-chan-firmware-v1.1.0.zip)，SHA-256 已验） | 低 | 网页抽风/脚本化 |
| npm 本地构建 | 中 | 改代码、MOD 开发 |
| M5Burner v3 | 低 | K151 出厂固件安装/恢复（仅方案 A） |

- 离线包含 4 目标：`m5stackchan_cores3`（K151）/ `com.m5stack.cores3` / `com.m5stack.core2` / `com.m5stack`；每目标 esptool 三件套（S3：bootloader@0x0、pt@0x8000、app@0x10000；ESP32：bootloader@0x1000）。Stack-chan RT 与 Takao 目标需源码构建。
- npm 路线：`npm i && npm run setup && npm run setup -- --device=esp32 && npm run doctor && npm run flash`（Ubuntu 24.04 + Node 22 实测；Windows 用 WSL 或官方 Docker/devcontainer）。各目标 `npm run flash[:stackchan_rt|:takao_core2_sg90]`；单刷 MOD：`npm run mod -- mods/examples/xxx/manifest.json`。
- 驱动配置（自制接线必改 `manifest_local.json`）：`driver.type` = `m5stackchan` / `scservo` / `rs30x` / `pwm` / `dynamixel` / `none`；`panId/tiltId`（串行 ID）、`pwmPan/pwmTilt`（PWM 引脚）、`offsetPan/offsetTilt`（零位微调）；`tts.*`（语音合成）。**验收标准：A 键随机看、B 键四方看、C 键反色；会摇头 = 成功。**

### 4.5 进阶玩法（装好之后）

- **MOD 生态**：[MOD Gallery](https://stack-chan.github.io/stack-chan/web/mod-gallery/) 现成应用商店 / [积木编辑器](https://stack-chan.github.io/stack-chan/web/editor/) 零代码 / [模拟器](https://stack-chan.github.io/stack-chan/web/simulator/)。
- **官方进阶文档存档 + 中文导读**（API / 换音色唱歌 / 外接 TTS / 多机互联 / 网页改设置 / 迷你应用 / 31 个示例 MOD 索引）：[`firmware-docs/`](firmware-docs/README.md)。
- **接入 Hermes 智能体当大脑**（Stack-chan 出眼耳口身、HermesAgent 出脑；两个开源案例的架构与上手）：[`hermes-integration/`](hermes-integration/README.md)。
- 刷社区固件会覆盖 K151 出厂固件（两套独立实现），恢复用 M5Burner。

---

## 附录 A：本仓库文件清单

```
stackchan-diy-guide/  （本仓库）
├── README.md                       ← 本文档（项目门户 + 通用速查）
├── images/                           ← 49 张官方装配图/动图/板子实拍（正文已引用）
├── k151-kit-route/                   ← 方案 A：K151 整机（购买/App/固件切换）
├── v1-xl330-route/                   ← 方案 B：v1.0 + XL330（专篇：BOM/打样/10 步装配/固件）
│   ├── README.md  ├── images/（27 张）  └── reference/（官方装配指南 EN/JA 原文）
├── v0-sg90-route/                    ← 方案 C：v0 + SG90（含丐版直插/M5GO 变体）
│   ├── README.md  └── images/（25 张：动图/装配/M5GO 全套）
├── scs0009-serial-route/             ← 方案 D：SCS0009 串行机身（含 RS30X 变体）
│   └── README.md  + images/（9 张）
├── k151-body-route/                  ← 方案 E：K151 机身复刻（含 G 混合玩法 §11）
│   ├── README.md  ├── images/（20 张）  └── datasheets/（7 份 PDF）
├── stl/
│   ├── v1-xl330/    （8 件：v1.0 外壳全家桶）
│   ├── v0-sg90/     （5 件：v0 SG90 外壳 + 400mAh 电池背包）
│   ├── scs0009/     （4 件：SCS0009 官方专用机身）
│   ├── rs30x/       （3 件：Futaba RS30X 官方机身）
│   ├── k151-body/   （10 件：K151 官方机身结构，魔改参考）
│   └── backpack/    （4 件：官方电池背包 400mAh / 640mAh / AAA / 卡西欧电池规格）
├── pcb/
│   └── m5-pantilt-v1.0/  （KiCad 完整工程 + 原理图 PDF + kibot 配置 + 丝印/钻孔）
│       └── manufacture/  （已生成的嘉立创制造文件：Gerber zip + BOM(含LCSC号) + CPL + BOM.md + 下单说明）
├── firmware/
│   ├── stack-chan-firmware-v1.1.0.zip        （官方预编译固件，4 目标 ×3 件，SHA-256 已验）
│   └── stack-chan-firmware-v1.1.0.zip.sha256
├── firmware-docs/                    ← 官方进阶固件文档存档 + 中文导读
│   ├── README.md      （导读 + 31 个示例 MOD 索引）
│   ├── api.md / mods-README.md / firmware-README.md
│   ├── stackchan-voice.md / text-to-speech.md
│   └── local-peer-communication.md / setting-preferences-web.md / mini-apps_ja.md
└── hermes-integration/               ← Stack-chan × Hermes 联动（两个开源案例的架构/对比/上手）
```

## 附录 B：链接汇总

**开源项目**

- 主仓库（固件/外壳/底板/文档）：https://github.com/stack-chan/stack-chan
- 网页工具全家桶（刷机/设置/Gallery/编辑器/模拟器，中文）：https://stack-chan.github.io/stack-chan/web/
- 离线固件 release：https://github.com/stack-chan/stack-chan/releases
- K151 出厂固件 + App（M5Stack 官方）：https://github.com/m5stack/StackChan
- K151 板级支持包：https://github.com/m5stack/StackChan-BSP
- K151 官方机身结构：https://github.com/m5stack/M5_Hardware/tree/master/Products/K151_StackChan/Structures
- AI Stack-chan（Arduino）：https://github.com/robo8080/AI_StackChan2
- PWM 测试固件（Arduino）：https://github.com/mongonta0716/stack-chan-tester
- mongonta 套件（日本）：https://mongonta.booth.pm/

**购物**

- M5Stack 官方淘宝店：https://m5stack.taobao.com
- StackChan 整机淘宝直链：https://item.taobao.com/item.htm?id=1042238294510
- 官方商城（$99/$125）：https://shop.m5stack.com/products/stackchan-kawaii-co-created-open-source-ai-desktop-robot
- 嘉立创 PCB：https://www.jlc.com ｜ 三维猴 3D 打印：https://3d.jlcpcb.com

**文档**

- M5Stack 中文产品文档：https://docs.m5stack.com/zh_CN/StackChan
- 固件开发文档（克隆仓库后看 `firmware/docs/`）：getting-started / flashing-firmware / api / mods
- Dynamixel Wizard 2：https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/
- Moddable SDK：https://github.com/Moddable-OpenSource/moddable
- 社区 Discord：https://discord.gg/eGhd9adnBm
- 纸书（日文，手挫圣经）：《つくれる！スーパーカワイイ ロボット スタックチャン》O'Reilly Japan, 2022

## 附录 C：来源与致谢

| 内容 | 来源 | 许可 |
|---|---|---|
| 外壳 STL、底板 KiCad 工程、装配图/动图、预编译固件 v1.1.0、进阶固件文档 | https://github.com/stack-chan/stack-chan | Apache-2.0 |
| K151 官方机身结构 STL（10 件） | https://github.com/m5stack/M5_Hardware（版权归 M5Stack） | 见原仓库 |
| K151 规格与安全须知、M5Burner / App 下载渠道 | https://docs.m5stack.com/zh_CN/StackChan | 官方文档 |
| M5GO Bottom 版装配图 | mongonta（Takao Akaki），经 stack-chan 仓库 contributed 目录收录 | 见原仓库 |

- 本仓库（教程文字部分除外）均为上述开源资料的转存汇总，供个人复刻学习使用；商用或二次分发前请确认上游许可。
- 教程文字由 Ekko Agent 受仓库主人委托整理，欢迎纠错 PR。

*装配口诀：先刷固件、对准零位、再锁螺丝。*
