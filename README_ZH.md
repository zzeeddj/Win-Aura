# Win-Aura Monitor (系统灵动光环)

> **让你的系统“呼吸”起来。**
>
> 一个沉浸式、极简且无干扰的 Windows 系统性能监视器。它能将当前活动窗口的边框转化为实时的性能仪表盘。

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.8+-yellow.svg) ![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg)

**Win-Aura** 并不是一个传统的任务管理器。它是一个环境光效层，通过边框的**颜色**（内存占用）和**呼吸频率**（CPU 占用），让你在不分心的情况下直观感知系统负载。

## ✨ 核心特性

* **🧠 内存可视化 (色彩映射)**
    * 边框颜色根据当前进程的内存占用动态变化。
    * **白/青色：** 轻量级应用 (空闲)。
    * **黄/橙色：** 中等负载。
    * **红色：** 高负载/满载。
    * *阈值与颜色完全可配置。*

* **🫀 CPU 呼吸律动 (动态频率)**
    * 光晕的“呼吸”速度代表 CPU 活跃度。
    * **禅模式：** CPU 空闲时，边框缓慢、悠闲地呼吸。
    * **警报模式：** CPU 满载时，边框急促闪烁。

* **🛡️ 智能过滤与防闪烁**
    * **零干扰：** 自动屏蔽桌面、任务栏、开始菜单、搜索栏、通知中心及托盘溢出菜单。
    * **资源管理器白名单：** 仅在文件资源管理器窗口显示，自动屏蔽 Explorer 的属性弹窗和系统组件。
    * **进程锁 (PID-Lock)：** 独创的同步校验机制，彻底消除切换窗口时的“幽灵边框”闪烁问题。

* **⚡ 原生级性能**
    * **DWM 集成：** 直接调用 `dwmapi.dll` 获取视觉边界，完美贴合 Windows 11 圆角窗口，剔除隐形阴影。
    * **鼠标穿透：** 采用 `WS_EX_TRANSPARENT` 属性，全屏透明层对鼠标操作完全无感。

## 🛠️ 安装与使用

1.  **克隆项目**
    ```bash
    git clone [https://github.com/YourUsername/Win-Aura.git](https://github.com/YourUsername/Win-Aura.git)
    cd Win-Aura
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **运行**
    ```bash
    python main.py
    ```

## ⚙️ 参数配置

Win-Aura 专为极客设计，你可以在 `main.py` 顶部轻松修改配置：

   ```python
   # 用户参数配置
   BORDER_WIDTH = 4           # 边框宽度 (px)
   GLOW_LAYERS = 4            # 光晕层数 (数值越大光晕越厚)
   RAM_SENSITIVITY_CAP = 12.0 # 内存满载阈值 (占系统总内存的百分比)

   # 颜色阶梯 (阈值 -> RGB)
   COLOR_STOPS = [
       (0.0,  (255, 255, 255)), # 空闲
       (1.0,  (255, 0, 0))      # 满载
   ]
   ```

## 📄 开源协议

本项目基于 MIT 协议开源。
