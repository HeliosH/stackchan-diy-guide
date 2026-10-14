# 官方进阶固件文档包（原文存档 + 中文导读）

本目录是 stack-chan 官方仓库 `firmware/docs/` 的进阶文档存档（英文原文，个别仅有日文版），并附中文导读。刷机/装配等基础内容见仓库主 README 第 7 章；这里是"装好之后继续玩"的部分。

## 文档一览

| 本地文件 | 原文路径（官方仓库） | 内容一句话 |
|---|---|---|
| `api.md` | `firmware/docs/api.md` | **MOD 开发 API**：StackchanContext 能力对象（UI/动作/语音/输入）、右手坐标系（X=脸前、Y=脸左、Z=头顶；米/弧度）、RobotUI、Motion、Audio |
| `stackchan-voice.md` | `firmware/docs/stackchan-voice.md` | **内置离线 TTS**：CoreS3/WASM 默认引擎，voice=`normal`/`cute`，以及 `robot.audio.sing()` 唱歌记谱法（`#C4,450ki` = C4 音高唱"き"450ms） |
| `text-to-speech.md` | `firmware/docs/text-to-speech.md` | **外接 TTS**：预生成（构建时抓音频）/远程流式两种模式；支持 Google Cloud TTS、Coqui、VoiceVox、ElevenLabs 的配置方法 |
| `local-peer-communication.md` | `firmware/docs/local-peer-communication.md` | **多机本地互联**：`context.connectivity.localPeer` 统一 API，底层 ESP-NOW（首选）或 BLE 串口（Nordish UART，服务名 `STK-LP-XXXX`），无需联网 |
| `setting-preferences-web.md` | `firmware/docs/setting-preferences-web.md` | **网页改设置**：按住 C 键（触屏机触摸）开机进设置模式 → 浏览器开 https://stack-chan.github.io/stack-chan/web/preference/ → BLE 连接后表单式改配置，**不用配 Wi-Fi** |
| `mini-apps_ja.md` | `firmware/docs/mini-apps_ja.md` | **迷你应用（实验性）**：临时替换脸屏幕的 Piu 小应用，区域 320×196（AppBar 下方）；`context.ui.miniApps.register()` 注册；外部 archive 只能 import `miniapp`/`piu/MC`/`piu/Timeline` |
| `mods-README.md` | `firmware/mods/README.md` | **MOD 机制总览**：MOD Gallery / 积木编辑器 / 模拟器入口，`npm run mod -- mods/examples/xxx/manifest.json` 单刷 MOD |
| `firmware-README.md` | `firmware/README.md` | **固件仓库总说明**：出厂固件 vs 本仓库固件的区分、浏览器工具、本地开发命令速查、AI Stack-chan（robo8080 的另一项目）指引 |

## 官方示例 MOD（`firmware/mods/examples/`，31 个）

学 API / 抄代码的最佳素材（括号为要点）：

- **动作/舵机**：`look_around`（API 官方示范）、`calibration`（舵机校准）、`setup_rs30x`（RS30X 初始化）、`dynamixel`
- **对话/AI**：`chatgpt`、`ai_stackchan`、`ai_stackchan_api`、`codex_voice`、`provider-dialogues`、`chat_audioio`
- **语音/显示**：`lip_sync`（口型同步）、`face`、`image_avatar_lite`、`monologue`（预生成语音示例）
- **互联/传感**：`local_peer_hello`（多机互联示范）、`beacon_advertiser` / `beacon_scanner`、`mediapipe_ble`（面部/手势跟踪）、`mimic_follow` / `mimic_main`、`unit_temperature`（外接温度 Unit）
- **平台/杂项**：`m5stackchan_smoke`（整机自检）、`mcp`（MCP Server MOD）、`web_radio`、`light`、`cheerup_ble_lite` / `cheerup_ws`、`mini_app_sample` / `mini_app_ui_sample`、`localized_drawer`

## 快速上手路径

1. 装好固件（主指南 §7）→ 先用 [MOD Gallery](https://stack-chan.github.io/stack-chan/web/mod-gallery/) 挑现成 MOD 玩
2. 想自己写 → 积木编辑器（零代码）或读 `api.md` + 抄 `examples/look_around`
3. 想让她说话/唱歌 → `stackchan-voice.md`；想接自己的 TTS → `text-to-speech.md`
4. 两台 stack-chan 联动 / 手机 BLE 控制 → `local-peer-communication.md`

> 注意：官方文档持续更新，最新版以 https://github.com/stack-chan/stack-chan/tree/main/firmware/docs 为准；本包为 v1.1.0 时期快照。
