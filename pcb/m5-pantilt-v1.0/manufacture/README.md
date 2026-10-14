# 制造文件包（嘉立创可直接下单）

> 由官方 KiCad 工程（本目录上级）用 `kicad-cli 7.0` 于 2026-10 生成，**无需再装 KiCad/KiBot**。
> 生成命令见文末，可复现。

## 文件清单

| 文件 | 用途 |
|---|---|
| `jlcpcb/m5-pantilt-gerbers-jlcpcb.zip` | **PCB 下单用**：铜层×2 + 阻焊×2 + 丝印×2 + 钢网×2 + 板边 + 钻孔（PTH/NPTH 分离），嘉立创上传页直接拖入 |
| `jlcpcb/m5-pantilt-cpl-jlc.csv` | **SMT 贴片坐标**（37 个贴装位，含 J1/J2 双排母、J3/J8 舵机口、U1 等；LOGO 丝印图形已剔除） |
| `jlcpcb/m5-pantilt-bom-jlc.csv` | **SMT 物料表**（23 组，含官方原理图带的 LCSC 编号，嘉立创 SMT 下单直接匹配） |
| `jlcpcb/BOM.md` | 人类可读版 BOM（含手插件清单） |
| `jlcpcb/gerbers/` | Gerber/钻孔散文件（含官方图纸里没提交的铜层，以及 Courtyard/Fab 等非制造层，zip 里已剔除） |
| `jlcpcb/cpl/pos-both.csv` | kicad-cli 原始坐标输出（全量，未转 JLC 格式） |
| `jlcpcb/python-bom.csv` | 原理图网表 XML（元件/网络级数据，核对用） |

## 下单流程

1. 嘉立创 https://www.jlc.com → PCB 下单 → 上传 `m5-pantilt-gerbers-jlcpcb.zip`。
   参数：**2 层、1.6mm、喷锡（HASL）、5 片**。
2. 勾选 **SMT 贴片** → 上传 `m5-pantilt-bom-jlc.csv` + `m5-pantilt-cpl-jlc.csv` → 元件匹配页逐项确认 LCSC 编号。
3. **跳线必改（重要）**：串行舵机版（CoreS3 + XL330 / SCS0009）**只装 R13、R14**（0Ω），在匹配页把 **R9、R10、R11、R12 设为"不贴"**（它们是 PWM 模式的 Core 型号选择跳线，串行模式不用）。
   - 若你要做 **PWM/SG90 版**：反过来——不装 R13/R14，装 R9+R11（CoreS3）或 R10+R12 组合（Core2，详见原理图 `m5-pantilt.pdf` 的 Short 说明）。
4. **J1 在背面（bottom）**：经济 SMT 只贴单面时，建议把 J1 设为不贴、到手自己焊（方向照实拍图 `../../../images/m5-pantilt-bottom.png`）；或选双面贴装（加价）。
5. THT 件（J6、J7、SW1、J1 若免贴）到手手焊；`BOM.md` 里标了 `THT 手焊`。

## 元件速览（详表见 jlcpcb/BOM.md）

- U1 = MAX3485（SO-8，半双工收发）、Q1 = IRLML6402（电源软开关）、Q2 = BC857（方向控制）
- D1 = SS54、D2 = PMEG3030EP（电源路径）
- 电容 100µ×4 + 0.1µ×1、电阻 0603 ×15（R13/R14 为 0Ω 跳线）
- J1/J2 = 2×15 排母/排针（M-BUS）、J3/J8 = JST EH 3pin 舵机口、J5 = PH2.0 电池、J6 = PH 4pin、J7 = XH 5V、SW1 = SPDT 开关

## 复现命令（kicad-cli 7.0）

```bash
cd pcb/m5-pantilt-v1.0
mkdir -p manufacture/jlcpcb/gerbers
kicad-cli pcb export gerbers --output manufacture/jlcpcb/gerbers m5-pantilt.kicad_pcb
kicad-cli pcb export drill --generate-map --excellon-separate-th \
  --output "$(pwd)/manufacture/jlcpcb/gerbers/" m5-pantilt.kicad_pcb
kicad-cli pcb export pos --format csv --units mm --side both \
  --output manufacture/jlcpcb/cpl/pos-both.csv m5-pantilt.kicad_pcb
kicad-cli sch export python-bom --output manufacture/jlcpcb/python-bom.csv m5-pantilt.kicad_sch
# zip 打包 + JLC 格式 BOM/CPL 转换由脚本完成（见本文件生成记录）
```
