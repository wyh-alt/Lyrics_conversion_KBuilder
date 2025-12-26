"""
小灰熊歌词格式转换器
将标准时间轴歌词转换为小灰熊歌词软件格式
"""
import sys
import os
import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox, QFileDialog,
    QProgressBar, QGroupBox, QCheckBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class DropArea(QTextEdit):
    """支持拖拽的文本显示区域"""
    files_dropped = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setReadOnly(True)
        self.setPlaceholderText("拖拽文件或文件夹到此处...\n支持 .txt 或 .lrc 格式的歌词文件")
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                files.append(file_path)
            elif os.path.isdir(file_path):
                # 递归获取文件夹中的所有歌词文件
                for root, _, filenames in os.walk(file_path):
                    for filename in filenames:
                        if filename.endswith(('.txt', '.lrc')):
                            files.append(os.path.join(root, filename))
        
        if files:
            self.files_dropped.emit(files)
        
        event.accept()


class LyricConverter:
    """歌词格式转换核心类"""
    
    # 时间戳正则表达式，支持多种格式
    # 匹配: [00:00.00], [00:00.000], 00:00.00, 00:00.000, 0:00.00, <00:00.00>, (00:00.00)
    TIME_PATTERN = re.compile(r'[\[\(<]?(\d{1,2}):(\d{2})\.(\d{2,3})[\]\)>]?')
    
    @staticmethod
    def parse_time(time_str):
        """解析时间字符串，返回 MM:SS.mmm 格式"""
        time_str = str(time_str).strip()
        
        # 移除可能的括号
        time_str = time_str.strip('[]()<>')
        
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds_parts = parts[1].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            
            # 如果毫秒只有两位，补齐到三位
            if len(seconds_parts) > 1 and len(seconds_parts[1]) == 2:
                milliseconds *= 10
            
            # 格式化为 MM:SS.mmm
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        
        return time_str
    
    @staticmethod
    def calculate_duration(start_time, end_time):
        """计算持续时间（毫秒）"""
        def time_to_ms(time_str):
            parts = time_str.split(':')
            minutes = int(parts[0])
            seconds_parts = parts[1].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1])
            return minutes * 60000 + seconds * 1000 + milliseconds
        
        start_ms = time_to_ms(start_time)
        end_ms = time_to_ms(end_time)
        return str(end_ms - start_ms)
    
    @staticmethod
    def extract_timestamps_and_lyric(line):
        """
        从一行文本中提取时间戳和歌词内容
        支持多种格式：
        - 开始时间 结束时间 歌词
        - [开始时间] 歌词 [结束时间]
        - 歌词 开始时间 结束时间
        - [开始时间][结束时间]歌词
        等等
        """
        line = line.strip()
        if not line:
            return None
        
        # 查找所有时间戳
        matches = list(LyricConverter.TIME_PATTERN.finditer(line))
        
        if len(matches) < 2:
            # 如果少于2个时间戳，尝试简单分割
            parts = line.split()
            if len(parts) >= 3:
                # 尝试解析前两个为时间
                try:
                    start_time = LyricConverter.parse_time(parts[0])
                    end_time = LyricConverter.parse_time(parts[1])
                    lyric_text = ' '.join(parts[2:])
                    return start_time, end_time, lyric_text
                except:
                    pass
            return None
        
        # 提取前两个时间戳
        start_match = matches[0]
        end_match = matches[1]
        
        # 解析时间
        start_time = LyricConverter.parse_time(start_match.group(0))
        end_time = LyricConverter.parse_time(end_match.group(0))
        
        # 提取歌词文本（移除所有时间戳）
        lyric_text = LyricConverter.TIME_PATTERN.sub('', line).strip()
        
        # 清理多余的空格和符号
        lyric_text = re.sub(r'\s+', ' ', lyric_text).strip()
        
        if not lyric_text:
            return None
        
        return start_time, end_time, lyric_text
    
    @staticmethod
    def convert_lyric_line(line):
        """转换单行歌词"""
        line = line.strip()
        if not line:
            return None
        
        # 检查是否已经是小灰熊格式，如果是则跳过（避免重复转换）
        if LyricConverter.KARAOKE_ADD_PATTERN.match(line):
            return None
        
        result = LyricConverter.extract_timestamps_and_lyric(line)
        
        if not result:
            return None
        
        start_time, end_time, lyric_text = result
        
        duration = LyricConverter.calculate_duration(start_time, end_time)
        
        # 给整句歌词添加方括号
        lyric_text = f"[{lyric_text}]"
        
        return f"karaoke.add('{start_time}', '{end_time}', '{lyric_text}', '{duration}');"
    
    # 反向转换：匹配 karaoke.add('开始时间', '结束时间', '[歌词]', '时长');
    KARAOKE_ADD_PATTERN = re.compile(
        r"karaoke\.add\s*\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*\)\s*;"
    )
    
    @staticmethod
    def format_time_simple(time_str):
        """将 MM:SS.mmm 格式转换为 M:SS.mmm 格式（去除前导零）"""
        time_str = time_str.strip()
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds_part = parts[1]
            return f"{minutes}:{seconds_part}"
        return time_str
    
    @staticmethod
    def reverse_convert_line(line):
        """反向转换单行歌词（小灰熊格式 -> 标准时间轴）"""
        line = line.strip()
        if not line:
            return None
        
        match = LyricConverter.KARAOKE_ADD_PATTERN.match(line)
        if not match:
            return None
        
        start_time = match.group(1)
        end_time = match.group(2)
        lyric_text = match.group(3)
        
        # 移除歌词两端的方括号
        if lyric_text.startswith('[') and lyric_text.endswith(']'):
            lyric_text = lyric_text[1:-1]
        
        # 格式化时间（去除前导零）
        start_time = LyricConverter.format_time_simple(start_time)
        end_time = LyricConverter.format_time_simple(end_time)
        
        return f"{start_time} {end_time} {lyric_text}"
    
    @staticmethod
    def reverse_convert_file(input_path):
        """反向转换整个文件（小灰熊格式 -> 标准时间轴）"""
        # 尝试多种编码读取文件
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'shift-jis', 'euc-kr']
        lines = None
        
        for encoding in encodings:
            try:
                with open(input_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if lines is None:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        # 转换每一行歌词
        output_lines = []
        lyric_count = 0
        for line in lines:
            converted = LyricConverter.reverse_convert_line(line)
            if converted:
                output_lines.append(converted)
                lyric_count += 1
        
        return "\n".join(output_lines), lyric_count
    
    @staticmethod
    def is_karaoke_format(lines):
        """检测文件是否已经是小灰熊格式"""
        if not lines:
            return False
        
        # 检查文件开头是否包含小灰熊格式的特征
        karaoke_indicators = [
            'karaoke := CreateKaraokeObject;',
            'karaoke.rows :=',
            'karaoke.clear;',
            'karaoke.songname :=',
            'karaoke.singer :='
        ]
        
        # 统计包含小灰熊格式特征的行数
        indicator_count = 0
        karaoke_add_count = 0
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # 检查是否包含小灰熊格式的特征标识
            for indicator in karaoke_indicators:
                if indicator in line_stripped:
                    indicator_count += 1
                    break
            
            # 检查是否包含 karaoke.add 语句
            if LyricConverter.KARAOKE_ADD_PATTERN.search(line_stripped):
                karaoke_add_count += 1
        
        # 如果同时满足以下条件，则认为是小灰熊格式：
        # 1. 包含至少2个小灰熊格式特征标识（如 karaoke := CreateKaraokeObject; 和 karaoke.clear;）
        # 2. 或者包含至少1个 karaoke.add 语句
        return indicator_count >= 2 or karaoke_add_count >= 1
    
    @staticmethod
    def convert_file(input_path, song_name=None, singer=None):
        """正向转换整个文件（标准时间轴 -> 小灰熊格式）"""
        # 尝试多种编码读取文件
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'shift-jis', 'euc-kr']
        lines = None
        
        for encoding in encodings:
            try:
                with open(input_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                break  # 成功读取，退出循环
            except (UnicodeDecodeError, UnicodeError):
                continue  # 尝试下一个编码
        
        if lines is None:
            # 如果所有编码都失败，使用 utf-8 并忽略错误
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        # 检测是否已经是小灰熊格式
        if LyricConverter.is_karaoke_format(lines):
            # 如果已经是小灰熊格式，直接返回原文件内容
            original_content = ''.join(lines)
            # 统计已有的歌词行数
            lyric_count = sum(1 for line in lines if LyricConverter.KARAOKE_ADD_PATTERN.search(line.strip()))
            return original_content, lyric_count
        
        # 如果没有提供歌曲名，使用文件名
        if not song_name:
            song_name = Path(input_path).stem
        
        if not singer:
            singer = '未知歌手'
        
        # 生成小灰熊格式
        output_lines = [
            "karaoke := CreateKaraokeObject;",
            "karaoke.rows := 2;",
            "karaoke.clear;",
            "",  # karaoke.clear; 之后的空白行
            f"karaoke.songname := '{song_name}'; // 歌曲名称",
            f"karaoke.singer := '{singer}'; // 歌手名称",
            "",  # karaoke.singer 之后的第一个空白行
            "",  # karaoke.singer 之后的第二个空白行
        ]
        
        # 转换每一行歌词
        lyric_count = 0
        for line in lines:
            converted = LyricConverter.convert_lyric_line(line)
            if converted:
                output_lines.append(converted)
                lyric_count += 1
        
        return "\n".join(output_lines), lyric_count


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("小灰熊歌词格式转换器")
        self.setMinimumSize(650, 500)
        self.resize(650, 550)  # 设置初始大小
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        
        # 拖拽区域
        self.drop_area = DropArea()
        self.drop_area.files_dropped.connect(self.on_files_dropped)
        self.drop_area.setMinimumHeight(120)
        self.drop_area.setMaximumHeight(350)  # 限制最大高度，约显示15行文件名
        file_layout.addWidget(self.drop_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.select_files_btn = QPushButton("选择文件")
        self.select_files_btn.clicked.connect(self.select_files)
        self.select_files_btn.setMinimumHeight(40)
        
        self.select_folder_btn = QPushButton("选择文件夹")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_folder_btn.setMinimumHeight(40)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_files)
        self.clear_btn.setMinimumHeight(40)
        
        button_layout.addWidget(self.select_files_btn)
        button_layout.addWidget(self.select_folder_btn)
        button_layout.addWidget(self.clear_btn)
        
        file_layout.addLayout(button_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 转换模式选择区域
        mode_group = QGroupBox("转换模式")
        mode_layout = QHBoxLayout()
        
        self.mode_button_group = QButtonGroup(self)
        
        self.mode_forward = QRadioButton("正向：时间轴 → 小灰熊格式")
        self.mode_forward.setChecked(True)  # 默认选择正向
        self.mode_button_group.addButton(self.mode_forward, 0)
        
        self.mode_reverse = QRadioButton("反向：小灰熊格式 → 时间轴")
        self.mode_button_group.addButton(self.mode_reverse, 1)
        
        mode_layout.addWidget(self.mode_forward)
        mode_layout.addWidget(self.mode_reverse)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # ANSI编码选项
        self.ansi_checkbox = QCheckBox("转换为ANSI编码（GBK）")
        self.ansi_checkbox.setChecked(True)  # 默认勾选
        self.ansi_checkbox.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.ansi_checkbox)
        
        # 开始转换按钮
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.convert_btn.setEnabled(False)
        layout.addWidget(self.convert_btn)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def on_files_dropped(self, files):
        """处理拖拽的文件"""
        self.selected_files = files
        self.convert_btn.setEnabled(len(files) > 0)
        self.statusBar().showMessage(f"已选择 {len(files)} 个文件")
        
        # 显示文件列表
        display_files = [os.path.basename(f) for f in files]
        display_text = f"已选择 {len(files)} 个文件:\n" + "\n".join(display_files)
        self.drop_area.setText(display_text)
        
    def select_files(self):
        """选择文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择歌词文件",
            "",
            "歌词文件 (*.txt *.lrc);;所有文件 (*.*)"
        )
        
        if files:
            self.selected_files = files
            # 显示文件列表
            display_files = [os.path.basename(f) for f in files]
            display_text = f"已选择 {len(files)} 个文件:\n" + "\n".join(display_files)
            self.drop_area.setText(display_text)
            self.convert_btn.setEnabled(True)
            self.statusBar().showMessage(f"已选择 {len(files)} 个文件")
            
    def select_folder(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.endswith(('.txt', '.lrc')):
                        files.append(os.path.join(root, filename))
            
            if files:
                self.selected_files = files
                # 显示文件列表
                display_files = [os.path.basename(f) for f in files]
                display_text = f"已选择 {len(files)} 个文件:\n" + "\n".join(display_files)
                self.drop_area.setText(display_text)
                self.convert_btn.setEnabled(True)
                self.statusBar().showMessage(f"已选择 {len(files)} 个文件")
            else:
                QMessageBox.warning(self, "提示", "所选文件夹中没有找到歌词文件！")
                
    def clear_files(self):
        """清空文件列表"""
        self.selected_files = []
        self.drop_area.clear()
        self.convert_btn.setEnabled(False)
        self.statusBar().showMessage("已清空文件列表")
        
    def start_conversion(self):
        """开始转换"""
        if not self.selected_files:
            QMessageBox.warning(self, "提示", "请先选择要转换的文件！")
            return
        
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        
        if not output_dir:
            return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.selected_files))
        self.progress_bar.setValue(0)
        
        # 禁用按钮
        self.convert_btn.setEnabled(False)
        
        # 获取转换模式（0=正向，1=反向）
        is_reverse_mode = self.mode_button_group.checkedId() == 1
        
        # 获取编码选项
        use_ansi = self.ansi_checkbox.isChecked()
        output_encoding = 'gbk' if use_ansi else 'utf-8'
        
        # 转换文件
        success_count = 0
        failed_files = []
        utf8_fallback_files = []  # 记录自动降级为UTF-8的文件
        
        for i, file_path in enumerate(self.selected_files):
            try:
                self.statusBar().showMessage(f"正在转换: {os.path.basename(file_path)}")
                
                # 根据模式选择转换方法
                if is_reverse_mode:
                    # 反向转换：小灰熊格式 -> 标准时间轴
                    output_content, lyric_count = LyricConverter.reverse_convert_file(file_path)
                else:
                    # 正向转换：标准时间轴 -> 小灰熊格式
                    output_content, lyric_count = LyricConverter.convert_file(file_path)
                
                # 保存
                output_filename = Path(file_path).stem + "_Converted.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                # 尝试用指定编码保存
                try:
                    with open(output_path, 'w', encoding=output_encoding) as f:
                        f.write(output_content)
                    success_count += 1
                except UnicodeEncodeError:
                    # 如果GBK编码失败（如韩文、emoji等），自动降级为UTF-8
                    if output_encoding == 'gbk':
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(output_content)
                        success_count += 1
                        utf8_fallback_files.append(os.path.basename(file_path))
                    else:
                        raise
                
            except Exception as e:
                failed_files.append((os.path.basename(file_path), str(e)))
            
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()  # 更新界面
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 恢复按钮
        self.convert_btn.setEnabled(True)
        
        # 显示结果
        self.show_result(success_count, failed_files, utf8_fallback_files, output_dir)
        
    def show_result(self, success_count, failed_files, utf8_fallback_files, output_dir):
        """显示转换结果"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("转换完成")
        
        if failed_files:
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setText(f"转换完成！\n\n成功: {success_count} 个\n失败: {len(failed_files)} 个")
            
            details = "失败文件:\n" + "\n".join([f"{f[0]}: {f[1]}" for f in failed_files])
            msg_box.setDetailedText(details)
        else:
            msg_box.setIcon(QMessageBox.Icon.Information)
            main_text = f"转换成功！\n\n共转换 {success_count} 个文件"
            
            # 如果有文件自动降级为UTF-8，添加提示
            if utf8_fallback_files:
                main_text += f"\n\n注意：{len(utf8_fallback_files)} 个文件包含韩文/特殊字符\n已自动使用UTF-8编码保存"
            
            main_text += f"\n\n输出目录: {output_dir}"
            msg_box.setText(main_text)
            
            # 如果有UTF-8降级文件，显示详情
            if utf8_fallback_files:
                details = "以下文件使用UTF-8编码（因包含韩文/特殊字符）:\n\n" + "\n".join(utf8_fallback_files)
                msg_box.setDetailedText(details)
        
        # 添加打开文件夹按钮
        open_btn = msg_box.addButton("打开输出文件夹", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(QMessageBox.StandardButton.Ok)
        
        msg_box.exec()
        
        # 如果点击了打开文件夹按钮
        if msg_box.clickedButton() == open_btn:
            os.startfile(output_dir)
        
        status_msg = f"转换完成：成功 {success_count} 个"
        if utf8_fallback_files:
            status_msg += f"（其中 {len(utf8_fallback_files)} 个使用UTF-8编码）"
        self.statusBar().showMessage(status_msg)


def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()




