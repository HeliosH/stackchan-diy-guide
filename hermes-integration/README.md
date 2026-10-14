# Stack-chan × Hermes 联动指南（把 Hermes 当她的大脑）

> 进阶玩法：Stack-chan 出"眼·耳·口·身体"，[HermesAgent](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server)（Nous Research 的 Hermes 智能体）出"大脑"。
> 网上有两个开源案例，技术路线一重一轻，本文整理两者做法、架构与上手路径。
> 整理自 2026-10，两个仓库均为社区项目，使用前先读各自 README 与安全说明。

---

## 0. 先搞清楚：Hermes 是什么角色

Stack-chan 原生固件的对话链路本来就是"可插拔"的：`tts.type: remote` 可指向自建服务器，ChatService 支持外部后端（见 [`../firmware-docs/`](../firmware-docs/README.md)）。所以接 Hermes 的本质是：

```
Stack-chan（传感器/执行器） ←实时通道→ 桥接进程（协议转换 + 语音管线） ←HTTP/SSE→ Hermes API（LLM 大脑）
```

机器人只负责：收音、拍照、动脖子、放音、显示表情；Hermes 负责"想"；中间的桥负责把两边说的话翻译成彼此听得懂的格式。

**Hermes 侧唯一的准备**：安装 HermesAgent 并开启 API Server——

```dotenv
# ~/.hermes/.env
API_SERVER_ENABLED=true
API_SERVER_HOST=127.0.0.1
API_SERVER_PORT=8642
API_SERVER_KEY=<自己生成的长随机串>
```

```bash
hermes gateway
```

桥接方主要用它的三个接口：`/health`、`/v1/capabilities`、`/v1/responses`（SSE 流式 + session key；图像理解需配视觉模型）。

---

## 1. 案例一：penpenguin/stackchan-hermes（完整方案，配官方 K151）

仓库：https://github.com/penpenguin/stackchan-hermes （日文文档）

**定位**：M5Stack **官方 StackChan（K151 / CoreS3）** 整机作为 HermesAgent 的化身。工程化程度最高：认证、固件备份、健康诊断、断线重连、故障注入测试都有。

### 1.1 架构（三层三端口）

```
┌─────────────┐  WebSocket:8765   ┌──────────────────┐  HTTP/SSE:8642  ┌──────────┐
│ StackChan    │ ◄──────────────► │ Python Bridge     │ ◄─────────────► │ Hermes   │
│ (CFW 固件)   │  图片上传同通道    │ (Mac/Linux/WSL2)  │                 │ Agent    │
│ 眼/耳/口/身体 │                  │ 管理:8766 / MCP   │                 │ 大脑     │
└─────────────┘                   └──────────────────┘                 └──────────┘
```

| 端口 | 用途 |
|---|---|
| `0.0.0.0:8765` | Device Gateway：设备 WebSocket 接入 + 摄像头图片上传 |
| `127.0.0.1:8766` | Control API：本地管理、**12 个 stdio MCP tool**、health/metrics |
| `127.0.0.1:8642` | 转发 Hermes API（对话 / 图像理解） |

### 1.2 固件层（CFW）

- 基于官方 vendor 快照的 CoreS3 固件，**ESP-IDF v5.5.4** 构建；
- **砍掉云功能与 OTA**，全部本地化（网络方针见其 `docs/network-policy.md`）；
- 内置：Bridge 客户端、官方 HAL 适配、NVS/USB 供电配置、mDNS、语音、摄像头、显示；
- 配网：开机变本地热点设 Wi-Fi；设备 ID / 主机 IP / token 通过 USB 串口 REPL 写入：

  ```text
  stackchan-hermes set-device-id stackchan-001
  （再写入主机 LAN IP 与 token，详见其 firmware/README.md）
  ```

- **烧录纪律（仓库强制）**：先做 16 MiB factory 备份 + 确认唯一串口，才允许 flash。

### 1.3 Bridge 层（Python 3.12 + uv）

语音回路：**麦克风 → VAD → Opus → STT → Hermes → TTS → 喇叭**

- STT：默认 mock；实战用本地 faster-whisper（`uv sync --locked --extra stt-local`）或任意 HTTP 服务；
- TTS：VOICEVOX Engine（`:50021`）、Irodori-TTS-Server（OpenAI 兼容 `/v1/audio/speech`）、或 mock；
- 认证双重：**设备 token**（`uv run stackchan-bridge token create --device-id stackchan-001`）与 **Hermes `API_SERVER_KEY`** 是两个不同的值，分别放 `.env` 的 `STACKCHAN_DEVICE_TOKEN` / `HERMES_API_KEY`。

### 1.4 上手顺序

```bash
git clone https://github.com/penpenguin/stackchan-hermes && cd stackchan-hermes
# ① 无硬件先跑通 E2E（Simulator + Mock Hermes + Mock STT/TTS，不需要任何 API key）
./scripts/run-simulator-e2e.sh
# ② 起 Hermes API（见 §0），然后配置 Bridge
cp config.example.toml config.toml && cp .env.example .env && chmod 600 .env config.toml
uv run --locked stackchan-bridge token create --device-id stackchan-001   # 填入 .env
uv run --locked --env-file .env stackchan-bridge serve --config config.toml
# ③ 另开终端诊断
uv run --locked --env-file .env stackchan-bridge doctor --config config.toml --json
curl -fsS http://127.0.0.1:8766/health/ready
# ④ 固件：ESP-IDF 5.5.4 → fetch_repos.py → idf.py reconfigure → verify-firmware.sh → 备份 → flash
```

**适合**：有官方 K151 整机、想要产品级稳定（诊断/重连/认证齐备）、能接受 ESP-IDF 工具链的用户。

---

## 2. 案例二：tiudsng/stack-chan-hermes（轻量方案，社区固件 + MOD）

仓库：https://github.com/tiudsng/stack-chan-hermes

**定位**：官方 **Moddable 社区固件的 fork**，用 [MOD 热装机制](../README.md)实现，改动量很小。适合**自制路线**（CoreS3 + 社区固件，即本仓库方案 B/D/E 的主机）。

做法（看它的提交记录一目了然）：

1. **复用官方示例 MOD `cheerup_ws`**（本来就是 WebSocket 客户端示例），把 WebSocket URL 指向 Hermes bridge（`ws://<主机>:8000`）；
2. 在 `mod.js` 里加 **TTS handler**（本地 TTS，注释称 "CVM brain integration"）；
3. 内嵌官方 **`mcp` MOD**（MCP Server 示例，见 [`../firmware-docs/README.md`](../firmware-docs/README.md) 的示例索引）；
4. 构建期把 **Wi-Fi 凭据预烧进 NVS**（仅当 NVS 为空时生效），CI 自动产出 cores3 固件 bin。

要点：机器人端没有任何新协议——就是"一个 WebSocket MOD + Hermes 后端"，桥接服务在主机侧（端口 8000）。

**适合**：已经按本仓库方案 B/D/E 做好自制 Stack-chan、想快速接 Hermes 试玩的玩家。

---

## 3. 两案例对比与选型

| 维度 | penpenguin（案例一） | tiudsng（案例二） |
|---|---|---|
| 目标硬件 | 官方 K151 / CoreS3 整机 | CoreS3 + 社区固件（自制机身即可） |
| 固件路线 | CFW（vendor 快照 + ESP-IDF 5.5.4） | Moddable fork + MOD 热装 |
| 机器人↔桥通道 | WebSocket :8765（认证 token + 图片上传） | WebSocket :8000（cheerup_ws MOD） |
| 语音管线 | Bridge 内建：VAD/Opus/STT/TTS 全套（faster-whisper + VOICEVOX/Irodori） | MOD 内 TTS handler，管线简单 |
| 视觉 | 摄像头拍照上传 Hermes（视觉模型） | 无（纯对话） |
| MCP | 12 个 stdio MCP tool | 内嵌 mcp 示例 MOD |
| 无硬件试跑 | ✅ Simulator + Mock 全家桶 | ❌ 需真机 |
| 安全/运维 | 认证、factory 备份、doctor、重连、故障注入 | 基本 CI 构建 |
| 复杂度 | 高 | 低 |

**选型**：

- 官方 K151 整机、要稳 → 案例一；
- 自制 CoreS3 机器人、快速试 → 案例二；
- 两个都想要的思路：先用案例二的 MOD 方式验证对话链路，再迁移到案例一的完整 Bridge。

---

## 4. 与本仓库方案的衔接

| 本仓库方案 | 可否接 Hermes | 说明 |
|---|---|---|
| A · K151 整机 | ✅ 案例一的原生目标 | 刷 CFW 前先做 factory 备份（恢复出厂见 [A 方案 §4](../k151-kit-route/README.md)） |
| B · v1.0 + XL330 | ✅ 案例二路线 | CoreS3 + 社区固件，改 MOD 即可 |
| D · SCS0009 / E · K151 复刻 | ✅ 案例二路线 | 同上，主机是 CoreS3 就行 |
| C · v0 + SG90（Core 主机） | ⚠️ 需验证 | 社区固件支持 Core 系列，但两案例都在 CoreS3 上开发 |

前置知识：MOD 机制与官方 API 见 [`../firmware-docs/`](../firmware-docs/README.md)；刷社区固件见主指南 §4.4。

---

## 5. 风险与注意

- **两个均为社区项目**，非官方出品，版本迭代快，动手前读原仓库最新 README；
- 案例一会**替换官方出厂固件**（删除云功能与 OTA）——务必先 factory 备份；
- Hermes API key、设备 token 都是凭据，`.env` 权限 600，不要提交进任何仓库；
- 摄像头/麦克风数据会发给 Hermes 侧的 LLM，注意隐私边界（案例一有专门的 `docs/network-policy.md` 通信方针文档，建议先读）；
- 国内网络环境：HermesAgent 与视觉模型服务需自行解决连通性。
