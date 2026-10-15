# 制造文件包（下单前核对装配）

> 当前 PCB 用 KiCad 10.0.7 重新填充铜区并导出。PCB 保留原有 KiCad 7 格式；仅更新铜区填充，孔、焊盘和走线保持当前基准。只上传现成制造包无需安装 KiCad。
> 原有 PDF 保留历史版本；制造以当前 PCB、原理图、BOM 和坐标为准。

## 文件清单

| 文件 | 用途 |
|---|---|
| `jlcpcb/m5-pantilt-gerbers-jlcpcb.zip` | PCB：铜层×2、阻焊×2、丝印×2、焊膏×2、板边、PTH/NPTH 钻孔，共 11 个文件 |
| `jlcpcb/m5-pantilt-bom-jlc.csv` | 商城采购/部分装配：19 组 / 26 件；SMT 15 组 / 21 件 + 通孔 4 组 / 5 件，均带 LCSC 号 |
| `jlcpcb/m5-pantilt-cpl-jlc.csv` | 上述 26 件的坐标；通孔件需另安排插件焊接或手焊，不会因存在坐标就自动机贴 |
| `jlcpcb/m5-pantilt-bom-full-assembly.csv` | 完整代工报价/工程审核：22 组 / 29 件，包含 J1/J2/SW1 客户供料和采购规格 |
| `jlcpcb/m5-pantilt-cpl-full-assembly.csv` | 完整 29 件双面坐标：J1 Bottom，其余 Top；不含机械孔、丝印和 R9–R12 |
| `jlcpcb/BOM.md` / `jlcpcb/ASSEMBLY.md` | 元件选型、自备件焊盘尺寸和完整代工装配要求 |
| `jlcpcb/assembly-parts.json` | 缺省料号补充、自备件采购规格；供导出脚本使用 |
| `jlcpcb/gerbers/` | Gerber/钻孔散文件；ZIP 不含非制造层和历史 PDF 钻孔图 |
| `jlcpcb/cpl/pos-both.csv` / `jlcpcb/python-bom.csv` | 当前工程导出的全量坐标、XML 网表；全量坐标需过滤后才能下单 |
| `checks/drc.json` / `checks/erc.json` / `checks/parity.json` | KiCad 检查记录，对应源文件/输出的 SHA256 见 `checks/manifest.json`，具体结论见文末 |

## 部分装配下单流程

1. 嘉立创 https://www.jlc.com → PCB 下单 → 上传 `m5-pantilt-gerbers-jlcpcb.zip`。参数：2 层、1.6mm；数量及表面处理按订单确认。
2. 勾选 SMT，上传 `m5-pantilt-bom-jlc.csv` + `m5-pantilt-cpl-jlc.csv`，确认商城型号、封装、极性和贴装角度。实际机贴范围为 21 个 SMD 器件；5 个通孔件另安排插件焊接或自行采购手焊，不把“料号可采购”当作“经济 SMT 可贴”。
3. 串行舵机版只装 R13/R14（0Ω）；R9–R12 已从清单剔除。若做 PWM/SG90：不装 R13/R14，另备 2 颗 0603 0Ω（C21189）——旧 Core 装 R9/R11，Core2/CoreS3 装 R10/R12，并修改固件类型和引脚，见 [配置表](../../../DIY_FIRMWARE.md#1-台架接线)。
4. J1/J2/SW1 不在默认商城清单内，单独采购并手焊；J1 在 Bottom，J2 在 Top。按 `BOM.md` 尺寸核对 SMD 焊脚及主机/外壳高度。C2337 是通孔单排件，不能裁切代替 J1。
5. 焊后核对极性和跳线，断电检查 5V/GND、3.3V/GND，再限流供电确认电压，最后连接主机和舵机测试。

## 完整代工需补充的材料

要求工厂全部焊好时，改用 `*-full-assembly.csv`，并附 [ASSEMBLY.md](jlcpcb/ASSEMBLY.md)。该清单包含全部 29 个串行版电气器件，J1/J2/SW1 按客户供料处理，不假造商城编号。

J1/J2 的供应商尺寸图、确定的型号和针高/插合高度仍需在采购时确认，并与主机和外壳试装；SW1 使用弯脚 OS102011MA1QN1。按装配板数和工厂余量要求准备来料。让工厂工程审核确认双面 SMT、通孔焊接、来料器件、角度和实际装配范围后再付款。[嘉立创官方说明](https://www.jlc.com/portal/server_guide_19327.html)支持双面贴片/插件及客户寄料，具体器件支持和报价以订单审核为准。

## 复现与验证

从仓库根目录执行，需要 Python 3 和 KiCad 10.0.7（或支持以下命令的兼容版本）：

```bash
python3 scripts/build-manufacture.py --kicad-cli /path/to/kicad-cli
python3 scripts/check-manufacture.py
npm run docs:build
```

脚本先在临时工程副本执行 `pcb drc --refill-zones --save-board`，把原生引擎生成的 `filled_polygon` 铜区填充复制回原 PCB，保留原有文件格式，再对实际 PCB 运行 DRC。存在 DRC 错误就停止；随后运行 ERC，同样在存在错误时停止。检查通过后导出 Gerber/钻孔/坐标/XML，并生成两套 BOM/CPL、11 文件 ZIP。不会生成或修改 PDF。

`check-manufacture.py` 核对两套 BOM/CPL 的位号、数量、封装、坐标、角度和层，检查安装孔保留、ZIP 一致性，并独立检查 U1 非 GND 焊盘内部点在 PCB 铺铜和导出 Gerber 中均不落入 GND。该回归检查防止旧铺铜短路重现，不能代替完整 DRC。

## 检查结果与实物验证

KiCad 10.0.7 检查结果（2026-10-15 封装入库与丝印修复后）：**DRC 0 错误、0 警告、0 未连接；PCB/原理图对应检查 0 错误、0 警告；ERC 0 错误、59 条警告**（58 条官方原理图内嵌符号与 KiCad 10 标准库的元数据差异 + 1 条机械件封装不在原理图，均为官方原版遗留、与电气无关）。

本次消除警告的方式（不是豁免，是实际修复）：
1. **34 个板载封装全部搬入项目库 `m5-pantilt.pretty`**（含 Q1 官方定制手焊 SOT-23 焊盘，单独命名 `SOT-23_HandSolder_Pads`；Q2 标准焊盘保留 `SOT-23`；R1/R2/R5 镜像摆放的变体加 `_Mirrored` 后缀），原理图 Footprint 字段同步指向项目库。焊盘几何、走线、网络一律未动——只是让封装与工程自带库自洽，DRC 对项目库比对全部通过。今后任何对焊盘的无意改动都会被 DRC 抓到。
2. **丝印修复**：J6（PH 4pin 侧入）与 SW1（侧拨开关）越出板边的丝印轮廓裁剪到板边内 0.4mm、完全在板外的线段删除；J1 底面两根与背面装饰边框相交的引脚刻度线缩短。铜层、阻焊、安装孔均未改动。
3. ERC 剩余 59 条警告：官方符号是多年前的库版本（引脚语义一致，仅描述/数据手册字段差异），重写符号库会改变原理图语义风险大于收益，保留并在报告中可见。

详情见 [检查说明](checks/README.md)。当前工程与检查记录一起提交；实板签核、连接器试装、总线波形及整机功能测试需要实物完成。历史 `../gerber/` 缺少铜层，不能用于制板；旧 PDF 的 Q2/R2 参数与当前工程有差异。
