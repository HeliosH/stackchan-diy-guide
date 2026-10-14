# 制造文件包（下单前核对装配）

> 由官方 KiCad 工程（本目录上级）用 `kicad-cli 7.0` 于 2026-10 生成，**无需再装 KiCad/KiBot**。
> 生成命令见文末，可复现。

## 文件清单

| 文件 | 用途 |
|---|---|
| `jlcpcb/m5-pantilt-gerbers-jlcpcb.zip` | **PCB 下单用**：铜层×2 + 阻焊×2 + 丝印×2 + 钢网×2 + 板边 + 钻孔（PTH/NPTH 分离），嘉立创上传页直接拖入 |
| `jlcpcb/m5-pantilt-cpl-jlc.csv` | **SMT 贴片坐标**（26 个贴装位；已剔除 LOGO 丝印图形、Hole1–Hole4 安装孔、R9–R12 串行版跳线、J1/J2/SW1 来料件） |
| `jlcpcb/m5-pantilt-bom-jlc.csv` | **SMT 物料表（匹配编号后仍须检查实际型号/封装）**（19 组，全部带经嘉立创元件库验证的 LCSC 编号；J3/J8=C160259、J6=C157926 为本仓库补充核实） |
| `jlcpcb/BOM.md` | 人类可读版 BOM（含手插件清单） |
| `jlcpcb/gerbers/` | Gerber/钻孔散文件（含官方图纸里没提交的铜层，以及 Courtyard/Fab 等非制造层，zip 里已剔除） |
| `jlcpcb/cpl/pos-both.csv` | kicad-cli 原始坐标输出（全量，未转 JLC 格式） |
| `jlcpcb/python-bom.csv` | 原理图网表 XML（元件/网络级数据，核对用） |

## 下单流程

1. 嘉立创 https://www.jlc.com → PCB 下单 → 上传 `m5-pantilt-gerbers-jlcpcb.zip`。
   参数：**2 层、1.6mm、喷锡（HASL）、5 片**。
2. 勾选 **SMT 贴片** → 上传 `m5-pantilt-bom-jlc.csv` + `m5-pantilt-cpl-jlc.csv` → 元件匹配页逐项确认 LCSC 编号。
3. **跳线已按串行版处理（无需再改）**：串行舵机版（CoreS3 + XL330 / SCS0009）**只装 R13、R14**（0Ω）；R9–R12 是 PWM 模式的 Core 型号选择跳线，**已从 BOM/CPL 中剔除**，匹配页不会再出现。
   - 若你要做 **PWM/SG90 版**：不装 R13/R14（下单时手动设不贴），自行购买 4 颗 0603 0Ω（LCSC C21189）手焊——Core Basic/Gray 短 R9+R11，Core2/CoreS3 短 R10+R12，并在固件显式指定 PWM 类型和引脚；详见 [自制配置表](../../../DIY_FIRMWARE.md#1-台架接线)。
4. **J1/J2/SW1 为来料件**（不在 BOM/CPL 里）：J1 是背面（bottom）2×15 贴片排针，到手自己焊（方向照实拍图 `../../../images/m5-pantilt-bottom.png`）；J2 排母、SW1 开关同样自备手焊，采购规格见 `jlcpcb/BOM.md` 第三节。
5. 通孔件 J3/J8/J5/J6/J7 有 LCSC 料号可随单采购，到手按实际装配方式手焊；封装分类与来料清单见 `BOM.md`。

## 元件速览（详表见 jlcpcb/BOM.md）

- U1 = MAX3485（**窄体 SOIC-8 3.9×4.9mm**，半双工收发；C668204 为窄体 SOP-8，PCB 封装已由宽体 SO-8 修正为 SOIC-8_3.9x4.9mm 并重新验证连通/DRC，2026-10）、Q1 = IRLML6402（电源软开关）、Q2 = BC857（方向控制）
- D1 = SS54、D2 = PMEG3030EP（电源路径）
- 电容 100µ×4 + 0.1µ×1、电阻 0603 ×15（R13/R14 为串行版 0Ω 跳线；R9–R12 不贴）
- J1/J2 = 2×15 排针/排母（M-BUS，来料）、J3/J8 = JST EH 3pin 舵机口（C160259）、J5 = PH2.0 电池（C2319）、J6 = PH 4pin 侧贴（C157926）、J7 = XH 5V（C20079）、SW1 = SPDT 开关（来料）

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
# zip 打包 + JLC 格式 BOM/CPL 转换由脚本完成（剔除 LOGO/Hole1-4/R9-R12/J1/J2/SW1，见 jlcpcb/BOM.md）
```

## 制造基准与未完成验证

采用当前 `.kicad_sch` / `.kicad_pcb` 和导出的制造文件作为同一基准；旧 PDF 原理图的 Q2/R2 参数与当前工程有差异，不混用其元件清单。尚未完成 DRC/ERC、实板签核及总线波形测试。提交订单前检查铜层/板边、孔径、极性、焊盘方向、跳线和全部料号。`../gerber/` 仅有历史丝印及钻孔，不能直接制板。

BOM 的 J3/J8/J5 为通孔封装，不能据表中“SMD 可贴”文字认定支持经济贴片；J1/J2 为 SMD 排针/排母，但需确认供货和贴装能力。THT/人工装配项按当前服务实际支持处理。
