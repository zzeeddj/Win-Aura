import sys
import ctypes
import math
import psutil
import traceback
import win32gui
import win32process
import win32api
import win32con
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QRect, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath

# --- System Setup / 系统设置 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

# --- User Configuration / 用户参数配置 ---

FPS = 60
# Refresh Rate (Hz) / 界面刷新率

BORDER_WIDTH = 4
# Border Thickness (px) / 边框宽度

GLOW_LAYERS = 4
# Glow Layers count / 光晕层数

SMOOTHING_FACTOR = 0.08
# Animation Smoothing / 动画平滑系数

RAM_SENSITIVITY_CAP = 10.0
# RAM Red Threshold (%) / 内存满载阈值 (百分比)

BASE_BREATH_SPEED = 0.02
# Idle Breath Speed / 空闲呼吸速度

MAX_BREATH_SPEED = 0.15
# Max Load Breath Speed / 满载呼吸速度

ZEN_MODE_ALPHA = 180
# Zen Mode Mask Opacity (0-255) / 禅模式遮罩透明度

ZEN_TOGGLE_KEY = win32con.VK_F8
# Toggle Key / 开关快捷键

# Color Steps: Threshold -> RGB / 颜色阶梯：阈值 -> RGB
COLOR_STOPS = [
    (0.0, (255, 255, 255)),  # White  / 白
    (0.25, (0, 255, 255)),  # Cyan   / 青
    (0.5, (255, 255, 0)),  # Yellow / 黄
    (0.75, (255, 165, 0)),  # Orange / 橙
    (1.0, (255, 0, 0))  # Red    / 红
]

# --- Blacklists / 黑名单设置 ---

# Ignored Window Classes / 忽略的窗口类名
IGNORE_CLASSES = [
    "Progman", "WorkerW", "Shell_TrayWnd",
    "MultitaskingViewFrame", "TaskSwitcherWnd",
    "Windows.UI.Core.CoreWindow", "NotifyIconOverflowWindow"
]

# Ignored Process Names / 忽略的进程名
IGNORE_PROCESSES = [
    "SearchHost.exe", "StartMenuExperienceHost.exe",
    "ShellExperienceHost.exe", "TextInputHost.exe", "Widgets.exe"
]


# --- Win32 Structures / Win32 结构体 ---
class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long),
                ('right', ctypes.c_long), ('bottom', ctypes.c_long)]


DWMWA_EXTENDED_FRAME_BOUNDS = 9


# --- Helper Functions / 辅助函数 ---

def get_visual_rect(hwnd):
    """Get DWM visual bounds / 获取视觉边界"""
    rect = RECT()
    try:
        hr = ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd, ctypes.c_int(DWMWA_EXTENDED_FRAME_BOUNDS),
            ctypes.byref(rect), ctypes.sizeof(rect))
        if hr == 0:
            return (rect.left, rect.top, rect.right, rect.bottom)
    except Exception:
        pass
    return win32gui.GetWindowRect(hwnd)


def get_window_class(hwnd):
    """Retrieve window class name / 获取窗口类名"""
    try:
        return win32gui.GetClassName(hwnd)
    except Exception:
        return ""


def is_window_valid(hwnd):
    """Check validity and visibility / 检查有效性与可见性"""
    if not win32gui.IsWindow(hwnd): return False
    if not win32gui.IsWindowVisible(hwnd): return False
    return True


def interpolate_color(val, color_stops):
    """Linear color interpolation / 颜色线性插值"""
    for i in range(len(color_stops) - 1):
        low_thresh, low_color = color_stops[i]
        high_thresh, high_color = color_stops[i + 1]
        if low_thresh <= val <= high_thresh:
            ratio = (val - low_thresh) / (high_thresh - low_thresh)
            r = int(low_color[0] + (high_color[0] - low_color[0]) * ratio)
            g = int(low_color[1] + (high_color[1] - low_color[1]) * ratio)
            b = int(low_color[2] + (high_color[2] - low_color[2]) * ratio)
            return QColor(r, g, b)
    return QColor(*color_stops[-1][1])


# --- Main Class / 主程序类 ---

class WinAuraOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Win-Aura Monitor")

        # State / 状态变量
        self.target_rect = None
        self.current_pid = None
        self.process_handle = None
        self.raw_process_name = ""
        self.process_name = ""

        # Zen Mode State / 禅模式状态
        self.is_zen_mode = False
        self.key_pressed = False

        # Metrics / 性能数据
        self.display_ram_percent = 0.0
        self.display_cpu_percent = 0.0
        self.breath_phase = 0.0
        self.target_class_name = ""

        # Window Setup / 窗口设置
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Geometry / 尺寸初始化
        screen = QApplication.primaryScreen()
        self.screen_rect = screen.availableGeometry()
        self.resize(self.screen_rect.width(), self.screen_rect.height())

        # Timers / 定时器
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(1000 // FPS)

        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.fetch_process_data)
        self.data_timer.start(200)

    def showEvent(self, event):
        """Apply Click-Through Attribute / 应用鼠标穿透属性"""
        super().showEvent(event)
        hwnd = self.winId().__int__()
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)

    def fetch_process_data(self):
        """Background Task: Fetch Data / 后台任务：获取数据"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd or not is_window_valid(hwnd): return

            cls_name = get_window_class(hwnd)
            if cls_name in IGNORE_CLASSES:
                self.process_name = "SystemUI"
                self.current_pid = None
                return

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid <= 0: return

            # Update Process Handle / 更新进程句柄
            if pid != self.current_pid:
                self.current_pid = pid
                try:
                    self.process_handle = psutil.Process(pid)
                    self.raw_process_name = self.process_handle.name()
                except psutil.NoSuchProcess:
                    self.process_handle = None
                    self.raw_process_name = ""

            # Reset Name State / 重置名称状态
            self.process_name = self.raw_process_name

            # Explorer Whitelist Check / Explorer 白名单检查
            if self.process_name and self.process_name.lower() == "explorer.exe":
                if cls_name != "CabinetWClass":
                    self.process_name = "SystemUI"
                    return

                    # Fetch Metrics / 读取指标
            target_cpu = 0.0
            target_ram = 0.0

            if self.process_handle:
                try:
                    target_ram = self.process_handle.memory_percent()
                    target_cpu = self.process_handle.cpu_percent(interval=None) / psutil.cpu_count()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    self.process_handle = None

            self.raw_cpu = target_cpu
            self.raw_ram = target_ram
        except Exception:
            pass

    def update_animation(self):
        """Animation Loop / 动画循环"""
        try:
            # Hotkey Detection / 热键检测
            state = win32api.GetAsyncKeyState(ZEN_TOGGLE_KEY)
            if state & 0x8000:
                if not self.key_pressed:
                    self.is_zen_mode = not self.is_zen_mode
                    self.key_pressed = True
                    self.update()  # Force Redraw / 强制重绘
            else:
                self.key_pressed = False

            ratio = self.devicePixelRatio()
            hwnd = win32gui.GetForegroundWindow()

            should_draw = False

            if hwnd and is_window_valid(hwnd):
                # Anti-Flash Lock / 防闪烁锁
                _, real_pid = win32process.GetWindowThreadProcessId(hwnd)

                if real_pid == self.current_pid:
                    if self.process_name not in IGNORE_PROCESSES and self.process_name != "SystemUI":
                        self.target_class_name = get_window_class(hwnd)
                        if self.target_class_name not in IGNORE_CLASSES:

                            rect = get_visual_rect(hwnd)
                            x, y, r, b = rect
                            w, h = r - x, b - y

                            # Size Filter / 尺寸过滤
                            if w > 60 and h > 60:
                                self.target_rect = QRect(int(x / ratio), int(y / ratio), int(w / ratio), int(h / ratio))
                                should_draw = True

            if not should_draw:
                self.target_rect = None

            # Smoothing / 数值平滑
            if not hasattr(self, 'raw_cpu'): self.raw_cpu = 0.0
            if not hasattr(self, 'raw_ram'): self.raw_ram = 0.0

            self.display_cpu_percent += (self.raw_cpu - self.display_cpu_percent) * SMOOTHING_FACTOR
            self.display_ram_percent += (self.raw_ram - self.display_ram_percent) * SMOOTHING_FACTOR

            cpu_factor = min(100.0, self.display_cpu_percent) / 100.0
            current_speed = BASE_BREATH_SPEED + (cpu_factor * MAX_BREATH_SPEED)
            self.breath_phase += current_speed

            self.update()

        except Exception:
            traceback.print_exc()

    def paintEvent(self, event):
        """Render Loop / 渲染循环"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Zen Mode Mask / 禅模式遮罩
            if self.is_zen_mode and self.target_rect:
                # Full Screen Path (Float) / 全屏路径
                full_screen_path = QPainterPath()
                full_screen_path.addRect(0.0, 0.0, float(self.width()), float(self.height()))

                # Window Path (QRectF) / 窗口路径
                window_path = QPainterPath()
                adjusted_rect = self.target_rect.adjusted(-1, -1, 1, 1)
                window_path.addRect(QRectF(adjusted_rect))

                # Subtraction / 路径相减
                mask_path = full_screen_path.subtracted(window_path)

                # Fill / 填充
                painter.fillPath(mask_path, QColor(0, 0, 0, ZEN_MODE_ALPHA))

            # Border Rendering / 边框渲染
            if not self.target_rect:
                return

            ram_normalized = min(1.0, self.display_ram_percent / RAM_SENSITIVITY_CAP)
            base_color = interpolate_color(ram_normalized, COLOR_STOPS)

            breath = (math.sin(self.breath_phase) + 1) / 2
            breath = 0.2 + (breath * 0.8)

            for i in range(GLOW_LAYERS):
                alpha = int(140 * breath / (i + 1))
                base_color.setAlpha(alpha)

                pen = QPen(base_color)
                pen.setWidthF(BORDER_WIDTH + (i * 1.5))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)

                offset = i * 1.0
                draw_rect = self.target_rect.adjusted(
                    int(-offset), int(-offset), int(offset), int(offset)
                )
                painter.drawRect(draw_rect)

        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = WinAuraOverlay()
    overlay.show()
    sys.exit(app.exec())