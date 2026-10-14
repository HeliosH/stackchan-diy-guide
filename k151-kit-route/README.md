# 路线 A：K151 官方整机（买现成，到手即玩）

> **不手挫，直接买 M5Stack 官方 StackChan 整机（K151）**。到手开机即用，配官方 App、AI 语音、出厂固件生态全开源。
> 预算 **¥700 上下**（淘宝直购；官方商城 $99，遥控版 K151-R $125），当天上手。

![K151 整机](../k151-body-route/images/K151_stack_chan_main_pictures_01.webp)

## 0. 本路线一览

| 项 | 内容 |
|---|---|
| 商品 | M5Stack StackChan 整机（K151） |
| 购买 | 淘宝官方店直购（见 §1） |
| 组成 | CoreS3 主机 + 官方机身 + 2×SCS0009 反馈舵机 + 550mAh 电池 |
| 内置 | 12×RGB、红外收发、顶部三区触摸、全功能 NFC、双 USB-C |
| 适合 | 只想玩、要 App/AI 功能、送礼、给自制路线当"参考机" |
| 难度 | ★（开箱 + 装 App） |

**为什么选它**：零手挫成本、官方保修、StackChan World App 只认官方核心；且出厂固件、遥控手柄固件、App、服务端[全部开源](https://github.com/m5stack/StackChan)，想折腾随时可以。机身结构和自制路线同源（复刻/魔改见 [K151 机身路线](../k151-body-route/README.md)）。

---

## 1. 购买

| 渠道 | 链接/说明 |
|---|---|
| **淘宝官方直链** | https://item.taobao.com/item.htm?id=1042238294510 （约 ¥700 上下，可开发票） |
| M5Stack 官方淘宝店 | https://m5stack.taobao.com 搜 "StackChan" |
| 官方商城（国际） | https://shop.m5stack.com/products/stackchan-kawaii-co-created-open-source-ai-desktop-robot （$99，深圳发货） |
| 遥控套件版 K151-R | https://shop.m5stack.com/products/m5stackchan-ai-desktop-robot-kit-with-remote-control-esp32-s3 （$125，多 JoyC + StickC-Plus 手柄，ESP-NOW 遥控） |
| 中文产品文档 | https://docs.m5stack.com/zh_CN/StackChan |

## 2. 开箱验收

1. 包装内：整机 ×1、Type-C 线、说明书（以实际清单为准）。
2. 开机：长按电源键，屏幕出脸即正常。
3. 硬件自检要点：脖子两个方向能转到头不顶壳；触摸头顶三区有反应；12 颗 RGB 灯正常。
4. **安全须知（官方原文警告）**：
   - **Y 轴（垂直）舵机角度控制在 5°–85°**，超限可能堵转并造成**永久损坏**；
   - X 轴无限制；**不确定通电状态时禁止用手硬掰**任何活动部件。
5. 两个 USB-C 口都支持数据，**推荐用底部那个**。

## 3. App 与玩法

- **StackChan World App**（iOS/Android）：视频查看、远程化身控制、App Center、AI 对话。
  ⚠️ **App 只能连接官方核心**（K151 整机 / 遥控套件 / 官方替换核心），**不能**连接第三方 CoreS3 / CoreS3-SE / CoreS3-Lite。
- 出厂固件 v1.1.0 新玩法：**Stackchan Dock**（安卓手机 USB 直连语音对话）、MCP Server MOD、MediaPipe BLE 面部/手势跟踪、XiaoZhi v1 兼容 ChatService。
- App 下载与使用教程：https://docs.m5stack.com/zh_CN/StackChan

## 4. 固件：出厂版 vs 开源社区版

K151 有**两套固件生态**，可以来回切：

| | 出厂固件（M5Stack） | 社区固件（stack-chan 仓库） |
|---|---|---|
| 来源 | https://github.com/m5stack/StackChan | https://github.com/stack-chan/stack-chan |
| 刷入/恢复 | **M5Burner v3**（见下） | 网页刷机 / esptool / npm |
| 特点 | 配套官方 App、遥控手柄 | MOD 热装、积木编辑器、模拟器生态 |
| 关系 | 刷社区固件会**覆盖**出厂固件 | 想回去用 M5Burner 恢复 |

**M5Burner 恢复/更新出厂固件**：

1. 下载 M5Burner v3：[Windows](https://m5burner-cdn.m5stack.com/app/M5Burner-v3-beta-win-x64.zip) · [macOS](https://m5burner-cdn.m5stack.com/app/M5Burner-v3-mac-x64.dmg) · [Linux](https://m5burner-cdn.m5stack.com/app/M5Burner-v3-beta-linux-x64.zip)
2. 打开 M5Burner → 搜索 **StackChan** → 勾选 **Only Official** → Download。
3. USB-C 连接（建议底部口）→ 烧录。

**刷社区固件**：Chrome/Edge 打开 https://stack-chan.github.io/stack-chan/web/flash/ 选 `M5StackChan CoreS3`；或用本仓库离线包 [`firmware/stack-chan-firmware-v1.1.0.zip`](../firmware/stack-chan-firmware-v1.1.0.zip) 的 `m5stackchan_cores3` 目标（esptool 用法与 SHA-256 校验见主指南）。刷社区固件前建议先用 M5Burner 备份。

## 5. 硬件规格速查（复刻/魔改参考）

| 项 | 规格 |
|---|---|
| 主机 | M5Stack CoreS3（ESP32-S3） |
| 舵机 | Feetech SCS0009 ×2（串行半双工，全状态反馈） |
| 电池 | 550mAh 锂电 |
| 触摸 | Si12T 顶部三区 |
| NFC | ST25R3916 全功能 |
| 红外 | IRM56384 收发 |
| 扩展 | AW9523B IO 扩展、INA226 电池监测、PY32L020 协处理器 |

完整硬件逆向（原理框图、接线、舵机协议、机身结构 STL）见姊妹篇：**[K151 机身复刻路线](../k151-body-route/README.md)**——自制玩家强烈推荐配合阅读（含"K151 机身 + 开源 PCB"混合路线）。

## 6. 常见问题

| 问题 | 处理 |
|---|---|
| App 连不上 | 确认是官方整机（非自购 CoreS3 自制）；蓝牙/本地网络权限开启 |
| 刷了社区固件想回官方 | M5Burner → StackChan → Only Official → 烧录（§4） |
| 脖子异响/顶壳 | 断电检查；Y 轴角度必须在 5°–85° 内（§2 安全须知） |
| 想加装/魔改 | 见 [K151 机身路线](../k151-body-route/README.md)（10 件官方结构 STL 已附带） |
| 想自己写玩法 | 社区固件 + MOD 生态，见 [firmware-docs/](../firmware-docs/README.md) |
