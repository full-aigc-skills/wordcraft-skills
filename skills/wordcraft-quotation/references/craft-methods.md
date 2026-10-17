# 字段、计算与原生命令

必填字段：quote_number、quote_date、issuer、customer、currency、pricing_basis、valid_until、terms、items。items每项仅含description、quantity、unit_price；可选expected_total。日期为ISO日期且有效期不早于报价日；币种为显式三个大写字母。金额按本技能两位小数格式展示，若业务要求其他精度请停止并说明。

脚本先验证全部字段和总额，再写输出或调用CLI。每项十进制计算后生成四列：项目、数量、单价、金额；最后一行是合计。正文保留计价口径和有效期，不伪造发票、签署或确认状态。

| 命令 | 参数证据 |
| --- | --- |
| `caret.docEnd` | `{"extend"?: bool}` |
| `caret.paraUp` | `{"extend"?: bool}` |
| `layout.margins` | `{"preset"?: "normal\|narrow\|moderate\|wide\|mirrored\|office2003", "top"?: pt, "bottom"?: pt, "left"?: pt, "right"?: pt, "gutter"?: pt}` |
| `layout.size` | `{"name"?: "Letter\|Legal\|A4\|…", "width"?: pt, "height"?: pt}` |
| `para.alignCenter` | `{}` |
| `para.alignLeft` | `{}` |
| `para.heading1` | `{}` |
| `para.heading2` | `{}` |
| `para.normal` | `{}` |
| `table.autofit` | `{"mode": "contents\|window\|fixed"}` |
| `table.borders` | `{"kind": "all\|outside\|inside\|none\|top\|bottom\|left\|right", "width"?: pt, "color"?: "RRGGBB"}` |
| `table.fromText` | `{"separator"?: "tab\|comma"}` |
| `table.look` | `{"headerRow"?: bool, "totalRow"?: bool, "bandedRows"?: bool, "firstColumn"?: bool, "lastColumn"?: bool, "bandedColumns"?: bool}` |
| `table.repeatHeader` | `{}` |
| `table.selectTable` | `{}` |
| `text.insert` | `{"text": string}` |
| `text.newParagraph` | `{}` |

执行顺序见[示例原生步骤](craft-steps.json)。段落必须用text.newParagraph，不能软换行；每一表格行先写制表分隔文本，再按行数caret.paraUp扩选，table.fromText转换。保留表头重复、窗口适配和原生表格边框。只操作新文档，不能把这个选择逻辑套在用户已有正文上。

## 长明细和分页

在新建空文档中，table.fromText生成的表格块索引由其前方实际text.newParagraph数量推导。select.range使用Pos结构 `{"story":"body","path":[表格块,行,列,0],"off":0}`，anchor与focus相同以定位单元格。逐行调用table.properties `{"allowBreak":false}`，不能仅全选表格调用一次（该命令只设置光标所在行）。随后逐列table.columnWidth设置250/45/75/81pt；数值列table.selectColumn后使用para.align `{"value":"right"}`，避免有状态快捷命令切换回左对齐。共享宿主须核对select.range实际回执，遇到位置钳制或非空文档立即停止。保存重开验证全部行的cantSplit、列宽和数值单元格对齐。
