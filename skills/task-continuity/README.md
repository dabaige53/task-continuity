# Task Continuity Skill

一个面向白领长期任务的轻量 skill。

它的目标不是做重量级项目管理，而是让 AI 在多轮对话里：
- 判断应该续接旧 task 还是新建 task
- 把用户原始问题保留下来
- 把 `task.md` 维护成唯一主上下文入口
- 用有目的的 run 文件夹记录每次推进
- 默认复用当前 active run，而不是每条指令都新开 run
- 保持任务目录整洁、可追溯、可恢复

## 包内内容

```text
task-continuity/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── init_task.py
└── references/
    └── task-files.md
```

## 目录模型

```text
tasks/
└── <task-short-name>-YYYYMMDD/
    ├── task.md
    ├── request.md
    ├── index.json
    ├── task.log
    ├── error_notes.md
    └── runs/
        ├── 001-<run-short-name>-YYYYMMDD/
        │   ├── run_summary.md
        │   └── outputs...
        └── ...
```

说明：
- task 根目录只放任务级记忆文件：`task.md`、`request.md`、`index.json`、`task.log`、`error_notes.md`
- 实际工作文件、草稿、输出文件默认放在 **active run** 文件夹里
- 不要把所有文件都丢到根目录

## 文件职责

- `task.md`：唯一主上下文入口。进入 task 后优先阅读它。
- `request.md`：保存用户原始问题与后续补充原话。
- `index.json`：轻量索引，用于匹配 task、恢复 task，并记录 `active_run`。
- `task.log`：关键里程碑日志。
- `error_notes.md`：需要避免重复犯错的点、偏好、风险。
- `runs/.../run_summary.md`：当前 run 的目标、输入、输出、决策和下一步。
- `runs/.../*`：该 run 期间产生的草稿、分析文件、修订版、导出文件等。

## 自带脚本

`scripts/init_task.py` 只依赖 Python 标准库，适合 Linux、macOS、Windows。

功能：
1. 初始化一个新 task
2. 在已有 task 中定位当前 active run
3. 仅在明确要求时创建新的 run
4. 可选写入用户原始问题或补充说明
5. 可选输出 JSON，方便其他工具调用

### 新建 task

```bash
python scripts/init_task.py "客户方案修订"
```

指定任务目录：

```bash
python scripts/init_task.py "客户方案修订" --root ./tasks
```

指定首个 run 名称：

```bash
python scripts/init_task.py "客户方案修订" --run "initial-intake"
```

同时写入原始问题：

```bash
python scripts/init_task.py "客户方案修订" --request "整理客户反馈并重写方案结构"
```

### 在已有 task 中读取当前 active run

```bash
python scripts/init_task.py --task-dir "./tasks/客户方案修订-20260417"
```

### 在已有 task 中显式新开 run

```bash
python scripts/init_task.py --task-dir "./tasks/客户方案修订-20260417" --new-run --run "提炼客户反馈"
```

### 给其他工具读 JSON 输出

```bash
python scripts/init_task.py "客户方案修订" --json
python scripts/init_task.py --task-dir "./tasks/客户方案修订-20260417" --json
python scripts/init_task.py --task-dir "./tasks/客户方案修订-20260417" --new-run --run "重写结构" --json
```

## 说明

- 不依赖第三方库
- 保留 Unicode 文件夹名，适合中文任务名
- 会自动清理 Windows 不允许的文件名字符
- 默认任务目录为当前工作目录下的 `tasks/`
- 如果同名 task 已存在，会自动追加数字后缀避免覆盖
- 现有 task 默认**复用 active run**，不会自动新开 run

## 建议使用方式

1. 新任务进来时，先初始化 task。
2. 立即把用户原始问题写入 `request.md`。
3. 把 `task.md` 填成当前任务最可靠的单文件上下文。
4. 小调整、小补充、小修订继续沿用当前 active run。
5. 只有在阶段切换、子目标变化、需要新检查点时才新开 run。
6. 结束一个 run 时更新 `task.md`、`index.json`、`task.log` 和 `run_summary.md`。
