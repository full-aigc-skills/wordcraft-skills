# 本场景的 Craft 方法与参数

先读取输入与当前选择。数值、路径、名称和对象编号仅为格式示例；用当前输入、实际返回ID和目标尺寸替换后执行。

| 顺序与目的 | 实际方法 | 参数例子 |
| --- | --- | --- |
| 1. 插入会议基本信息与决定 | `text.insert` | `{"text":"会议时间：待核实\n参会人：待核实\n决定：\n行动项："}` |
| 2. 插入行动项表格 | `insert.table` | `{"rows":3,"cols":4}` |
| 3. 核对全文结构 | `document.inspect` | `{"text":true}` |

## 如何调用

宿主内已打开编辑器时使用该同会话MCP；先等待editor_status就绪，读取实际工具schema和当前命令参数。独立CLI可用于文件任务，但新进程与已打开Web编辑器不是同一状态。

本插件MCP包装：`execute`，参数 `{"command": "text.insert", "params": {"text": "会议时间：待核实\n参会人：待核实\n决定：\n行动项："}}`。后续行保持同一会话和对象选择，逐条检查实际结果。

CLI 语法（下面是展示用写法，实际跨平台执行用argv避免shell引号差异）：

wordcraft-cli run --file input.docx --cmd 'text.insert={"text":"正文"}' --save output.docx。多个步骤使用多个 --cmd，同进程保留选择和插入点。

## 参数核对与完成标准

先查 [当前版本观察目录](craft-command-evidence.json) 中对应方法的完整参数，再按实际运行时查询更新。结构化步骤见 [craft-steps.json](craft-steps.json)。

区分讨论、决定和待办，行动项包含责任人、截止时间与状态。

边界：不得把讨论建议写成已达成决议；逐格填表需要当前table/cell选择。

保存可编辑工程后由新进程或重新打开的同一宿主会话核对；导出格式单独解码/查看。方法存在和零退出不代表本场景已经完成。

工作流来源与许可见 [workflow-sources.json](workflow-sources.json)。仅借鉴事实与方法，本文与参数例子原创编写。
