# SolarWolf Game QA Portfolio

这是一个面向游戏测试 / Game QA 岗位的个人 QA 作品集项目。项目以开源 Python/Pygame 游戏 **SolarWolf** 为被测对象，展示范围受控的手工测试、缺陷分析与 pytest 自动化测试实践。

## 重要声明

SolarWolf 是 Pete “ShredWheat” Shinners 创作的开源 Python/Pygame 游戏，以 LGPL 发布。本仓库**不包含 SolarWolf 游戏源码**，也不将游戏本身、游戏美术或玩法设计表述为本人的作品。

本仓库中的个人成果包括：测试计划、测试用例、探索性测试记录、主动黑盒验证、缺陷报告、证据、Python 源码分析记录与 pytest 自动化测试。

原项目说明见 SolarWolf 随附 README：`SolarWolf - http://pygame.org/shredwheat/solarwolf/index.shtml`。

## 项目概览

| 项目 | 结果 |
| --- | --- |
| 核心测试模块 | 4 个：移动与小方块、危险物与生命、特殊道具与计时器、UI/HUD 与存档 |
| 正式手工用例 | 13 / 13 通过 |
| pytest 自动化测试 | 28 passed in 1.01s |
| 已确认缺陷 | 1 个：BUG-UI-001（高严重性 / 高优先级，开放） |
| 测试环境 | Windows 11、Python 3.11.9、Pygame 2.6.1、pytest 9.1.1 |

这里的“通过”只描述已覆盖的测试条件；不代表 SolarWolf 全部功能、全部关卡或全部随机组合均无缺陷。

## 关键文档

- [测试计划](Test-Plan/SolarWolf-Test-Plan-v1.0.md)
- [首次探索性测试记录](Exploratory-Testing/Exploratory-Session-01.md)
- [主动黑盒测试记录](Test-Plan/Active-Black-Box-Test-Record-01.md)
- [正式手工测试用例与执行结果](Test-Cases/TC-Normal-Gameplay-v1.0.md)
- [BUG-UI-001 正式缺陷报告](Bug-Reports/BUG-UI-001-Focus-Return-Incomplete-HUD-Redraw.md)
- [pytest 自动化执行记录](Automation/Automation-Test-Run-01.md)
- [最终测试报告](Test-Report/SolarWolf-Test-Report-v1.0.md)

## 测试策略

测试先从黑盒探索开始：实际游玩并记录可观察的控制方式、关卡目标、危险物、特殊道具、HUD 和存档行为；未在第一阶段查询 GitHub Issues 或预先阅读源码。

确认 BUG-UI-001 后，才阅读相关 Python 源码。源码分析仅记录与现象相符的可能机制，不在缺少运行时验证时断言根因。

自动化范围刻意限制在稳定、适合程序验证的逻辑：移动边界、物体交互、随机行为的可重复验证，以及存档保存读取与独立性。它不尝试自动化完整全屏 GUI。

## 自动化测试

自动化测试依赖 SolarWolf 原项目源码，但源码应与本 QA 仓库保持逻辑分离。当前测试按以下同级目录结构定位被测源码：

```text
工作目录/
├── SolarWolf-QA-Portfolio/
└── solarwolf/
```

在 `SolarWolf-QA-Portfolio` 目录中，安装与测试环境匹配的依赖后执行：

```powershell
python -m pytest Automation -q
```

本项目记录的最终人工执行结果为 `28 passed in 1.01s`。详见 [自动化执行记录](Automation/Automation-Test-Run-01.md)。

## 目录结构

```text
SolarWolf-QA-Portfolio/
├── Automation/              # pytest 测试与执行记录
├── Bug-Reports/             # 已确认缺陷报告
├── Evidence/                # 游戏记录、缺陷截图与自动化截图
├── Exploratory-Testing/     # 首轮黑盒探索记录
├── Test-Cases/              # 正式手工测试用例与结果
├── Test-Plan/               # 测试计划与主动黑盒验证
└── Test-Report/             # 最终测试报告
```

## 当前结论与限制

- 已确认的 BUG-UI-001 仍保持开放：当前没有修复构建，因此没有将其误记为“回归通过”。
- 未确认或证据不足的现象不会被包装为缺陷。
- 实际游玩、测试执行、结果确认和缺陷判断由项目作者完成；AI 仅辅助整理测试设计、阅读源码、扩展测试思路与编写自动化测试。
