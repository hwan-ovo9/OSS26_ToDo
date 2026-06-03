# requirement: PyQt5
# pip install PyQt5

import os
import sys
import json

from datetime import datetime

from PyQt5.QtCore import (
    Qt,
    QDate,
    QTime,
    QTimer
)

from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QFileDialog,
    QFrame,
    QComboBox,
    QCheckBox,
    QDateEdit,
    QScrollArea,
    QTimeEdit,
    QDialog,
    QTextEdit
)


# ============================================
# Todo Card Widget
# ============================================

class TodoItemWidget(QFrame):
    def __init__(
        self,
        todo_data,
        delete_callback,
        edit_callback
    ):
        super().__init__()

        self.todo_data = todo_data

        self.delete_callback = delete_callback
        self.edit_callback = edit_callback

        # ============================================
        # 카드 자체를 흰색 둥근 배경으로 통일
        # ============================================

        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 22px;
            }
        """)

        self.setMinimumHeight(160)

        from PyQt5.QtWidgets import QSizePolicy

        self.setFixedHeight(160)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        # ============================================
        # 메인 레이아웃
        # ============================================

        layout = QHBoxLayout()

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        layout.setSpacing(14)

        # ============================================
        # 중요도 컬러 바
        # ============================================

        priority_color = {
            "높음": "#ff3b30",
            "보통": "#007aff",
            "낮음": "#8e8e93"
        }

        color = priority_color.get(
            todo_data["priority"],
            "#007aff"
        )

        side_bar = QFrame()

        side_bar.setFixedWidth(6)

        side_bar.setStyleSheet(f"""
            background:{color};
            border-radius:3px;
        """)

        # ============================================
        # 체크박스
        # ============================================

        self.check = QCheckBox()

        self.check.setChecked(
            todo_data["completed"]
        )

        self.check.stateChanged.connect(
            self.toggle_complete
        )

        # ============================================
        # 텍스트
        # ============================================

        text_layout = QVBoxLayout()

        text_layout.setSpacing(4)

        # ============================================
        # 제목
        # ============================================

        self.title = QLabel(
            todo_data["title"]
        )

        self.title.setFont(
            QFont("맑은 고딕", 15, QFont.Bold)
        )

        text_layout.addWidget(self.title)

        # ============================================
        # 메타 정보 태그 레이아웃
        # ============================================

        meta_layout = QHBoxLayout()

        meta_layout.setSpacing(8)

        # 날짜 태그
        date_label = QLabel(
            f'📅 {todo_data["deadline"]}'
        )

        # 중요도 태그
        priority_icon = {
            "높음": "🔥",
            "보통": "⭐",
            "낮음": "🌱"
        }

        priority_label = QLabel(
            f'{priority_icon.get(todo_data["priority"], "⭐")} '
            f'{todo_data["priority"]}'
        )

        # 카테고리 태그
        category_label = QLabel(
            f'📁 {todo_data["category"]}'
        )

        # 상태 태그
        status_icon = {
            "진행 전": "🕓",
            "진행 중": "⏳",
            "완료": "✅",
            "지연": "🚨"
        }

        status_label = QLabel(
            f'{status_icon.get(todo_data["status"], "🕓")} '
            f'{todo_data["status"]}'
        )

        # ============================================
        # 공통 스타일
        # ============================================

        tag_style = """
            background:#f2f2f7;
            color:#3a3a3c;
            border-radius:10px;
            padding:4px 10px;
            font-size:11px;
            font-weight:600;
        """

        for tag in [
            date_label,
            priority_label,
            category_label,
            status_label
        ]:
            tag.setStyleSheet(tag_style)

        # ============================================
        # 레이아웃 추가
        # ============================================

        meta_layout.addWidget(date_label)
        meta_layout.addWidget(priority_label)
        meta_layout.addWidget(category_label)
        meta_layout.addWidget(status_label)

        meta_layout.addStretch()

        text_layout.addLayout(meta_layout)

        # ============================================
        # 알림 기능 관련
        # ============================================
        from PyQt5.QtWidgets import QProgressBar

        self.progress = QProgressBar()

        try:

            created = datetime.strptime(
                todo_data["created_at"],
                "%Y-%m-%d %H:%M:%S"
            )

        except:

            created = datetime.now()

        deadline = datetime.strptime(
            todo_data["deadline"],
            "%Y-%m-%d %H:%M"
        )

        now = datetime.now()

        total_seconds = (
                deadline - created
        ).total_seconds()

        remain_seconds = (
                deadline - now
        ).total_seconds()

        text_layout.addWidget(self.progress)

        if remain_seconds <= 0:
            percent = 0

        elif total_seconds <= 0:
            percent = 100

        else:
            ratio = remain_seconds / total_seconds

            # 긴박감 증가
            percent = int((ratio ** 2) * 100)

        percent = max(0, min(percent, 100))

        if percent > 60:
            color = "#34c759"  # 초록

        elif percent > 30:
            color = "#ffcc00"  # 노랑

        elif percent > 10:
            color = "#ff9500"  # 주황

        else:
            color = "#ff3b30"  # 빨강

        self.progress.setValue(percent)

        self.progress.setTextVisible(False)

        self.progress.setFixedHeight(12)

        self.progress.setStyleSheet(f"""
        QProgressBar {{
            border:none;
            background:#e5e5ea;
            border-radius:6px;
        }}

        QProgressBar::chunk {{
            background:{color};
            border-radius:6px;
        }}
        """)

        if remain_seconds <= 0:

            remain_text = "🚨 마감 초과"

        else:

            hours = int(remain_seconds // 3600)
            minutes = int(
                (remain_seconds % 3600) // 60
            )

            remain_text = (
                f"⏰ {hours}시간 "
                f"{minutes}분 남음"
            )

        self.countdown_label = QLabel(
            remain_text
        )

        self.countdown_label.setStyleSheet("""
            color:#8e8e93;
            font-size:11px;
            font-weight:bold;
        """)

        text_layout.addWidget(self.countdown_label)

        # ============================================
        # 수정 버튼
        # ============================================

        edit_btn = QPushButton("수정")

        edit_btn.setFixedSize(65, 34)

        edit_btn.setStyleSheet("""
            QPushButton {
                background:#007aff;
                color:white;
                border:none;
                border-radius:12px;
                font-size:12px;
                font-weight:bold;
            }

            QPushButton:hover {
                background:#3395ff;
            }
        """)

        edit_btn.clicked.connect(
            self.edit_item
        )

        # ============================================
        # 삭제 버튼
        # ============================================

        delete_btn = QPushButton("삭제")

        delete_btn.setFixedSize(65, 34)

        delete_btn.setStyleSheet("""
            QPushButton {
                background:#ff3b30;
                color:white;
                border:none;
                border-radius:12px;
                font-size:12px;
                font-weight:bold;
            }

            QPushButton:hover {
                background:#ff5c52;
            }
        """)

        delete_btn.clicked.connect(
            self.delete_item
        )

        # 버튼 세로 배치
        button_layout = QVBoxLayout()

        button_layout.setSpacing(8)

        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)

        # ============================================
        # 전체 배치
        # ============================================

        layout.addWidget(side_bar)

        layout.addWidget(
            self.check,
            alignment=Qt.AlignTop
        )

        layout.addLayout(text_layout)

        layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.update_style()

        self.update_progress()

    def update_progress(self):

        try:

            created = datetime.strptime(
                self.todo_data["created_at"],
                "%Y-%m-%d %H:%M:%S"
            )

        except:

            created = datetime.now()

        deadline = datetime.strptime(
            self.todo_data["deadline"],
            "%Y-%m-%d %H:%M"
        )

        now = datetime.now()

        total_seconds = (
                deadline - created
        ).total_seconds()

        remain_seconds = (
                deadline - now
        ).total_seconds()

        if remain_seconds <= 0:

            percent = 0

        elif total_seconds <= 0:

            percent = 100

        else:

            ratio = remain_seconds / total_seconds

            percent = int(
                (ratio ** 2) * 100
            )

        percent = max(
            0,
            min(percent, 100)
        )

        self.progress.setValue(percent)

        if percent > 60:
            color = "#34c759"

        elif percent > 30:
            color = "#ffcc00"

        elif percent > 10:
            color = "#ff9500"

        else:
            color = "#ff3b30"

        self.progress.setStyleSheet(f"""
        QProgressBar {{
            border:none;
            background:#e5e5ea;
            border-radius:6px;
        }}

        QProgressBar::chunk {{
            background:{color};
            border-radius:6px;
        }}
        """)

        if remain_seconds <= 0:

            self.countdown_label.setText(
                "🚨 마감 초과"
            )

        else:

            hours = int(
                remain_seconds // 3600
            )

            minutes = int(
                (remain_seconds % 3600) // 60
            )

            second = int(
                (remain_seconds % 3600) % 60
            )

            self.countdown_label.setText(
                f"⏰ {hours}시간 {minutes}분 {second}초 남음"
            )

        if percent > 60:
            card_bg = "#ffffff"

        elif percent > 30:
            card_bg = "#fff9e6"

        elif percent > 10:
            card_bg = "#fff1e6"

        else:
            card_bg = "#ffeaea"

        if not self.check.isChecked():
            self.setStyleSheet(f"""
                QFrame {{
                    background:{card_bg};
                    border-radius:22px;
                }}
            """)

    # ============================================
    # 완료 체크
    # ============================================

    def toggle_complete(self):

        checked = self.check.isChecked()

        self.todo_data["completed"] = checked

        if checked:
            self.todo_data["status"] = "완료"

        elif self.todo_data["status"] == "완료":
            self.todo_data["status"] = "진행 전"

        self.update_style()

        self.window().refresh_list()

        self.window().auto_save_data()

    # ============================================
    # 스타일
    # ============================================

    def update_style(self):

        if self.check.isChecked():

            self.setStyleSheet("""
                QFrame {
                    background:#e5e5ea;
                    border-radius:22px;
                }
            """)

            self.title.setStyleSheet("""
                color:#9e9ea4;
                text-decoration: line-through;
            """)

        else:

            self.setStyleSheet("""
                QFrame {
                    background:white;
                    border-radius:22px;
                }
            """)

            self.title.setStyleSheet("""
                color:black;
            """)

    # ============================================
    # 수정
    # ============================================

    def edit_item(self):

        self.edit_callback(
            self.todo_data
        )

    # ============================================
    # 삭제
    # ============================================

    def delete_item(self):

        self.delete_callback(self)

# ============================================
# Main Window
# ============================================

class ReminderApp(QWidget):

    def __init__(self):
        super().__init__()

        self.todos = []
        #알림 관련
        self.todo_widgets = []

        #중복 알림 방지용
        self.notified = set()

        self.selected_time = QTime.currentTime()

        # 자동 저장 파일
        self.auto_save_file = "todo_data.json"

        # 수정 모드용 변수
        self.editing_todo = None

        # 그룹 펼침 상태
        self.group_states = {
            "🚨 마감 초과": True,
            "☀️ 오늘": True,
            "🌅 내일": True,
            "🗓️ 이번 주": True,
            "📅 이번 달": True,
            "📊 이번 분기 (1분기)": False,  # 먼 일정은 접어두기
            "📊 이번 분기 (2분기)": False,
            "📊 이번 분기 (3분기)": False,
            "📊 이번 분기 (4분기)": False,
            "🌓 올해 상반기": False,
            "🌓 올해 하반기": False,
            "✨ 올해 남은 일정": False,
            "완료됨": False
        }

        self.setWindowTitle("Reminder")

        self.resize(980, 760)

        self.setStyleSheet("""
            QWidget {
                background:#f2f2f7;
                font-family:'맑은 고딕';
            }
        """)

        self.init_ui()

        self.auto_load_data()

        # 알림 타이머
        self.reminder_timer = QTimer()

        self.reminder_timer.timeout.connect(
            self.check_reminders
        )

        self.reminder_timer.start(60000)

        self.refresh_timer = QTimer()

        self.refresh_timer.timeout.connect(
            self.auto_refresh
        )

        self.refresh_timer.start(1000)

    # ============================================
    # UI
    # ============================================

    def init_ui(self):

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        main_layout.setSpacing(16)

        # 제목
        title = QLabel("예정")

        title.setFont(
            QFont(
                "맑은 고딕",
                32,
                QFont.Bold
            )
        )

        title.setStyleSheet("""
            color:#ff3b30;
        """)

        main_layout.addWidget(title)

        # ============================================
        # 입력 카드
        # ============================================

        input_card = QFrame()

        input_card.setStyleSheet("""
            QFrame {
                background:white;
                border-radius:24px;
            }
        """)

        input_layout = QVBoxLayout()

        input_layout.setContentsMargins(
            24,
            24,
            24,
            24
        )

        input_layout.setSpacing(14)

        # 제목 입력
        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "할 일을 입력하세요"
        )

        self.title_input.setStyleSheet("""
            QLineEdit {
                border:none;
                font-size:18px;
                padding:12px;
                background:#f2f2f7;
                border-radius:14px;
            }
        """)

        input_layout.addWidget(
            self.title_input
        )

        # 옵션
        option_layout = QHBoxLayout()

        self.date_input = QDateEdit()

        self.date_input.setDate(
            QDate.currentDate()
        )

        self.date_input.setCalendarPopup(True)

        self.time_btn = QPushButton()

        self.time_btn.setText(
            f"🕒 {self.selected_time.toString('HH:mm')}"
        )

        self.time_btn.clicked.connect(
            self.open_time_picker
        )

        self.date_input.setCalendarPopup(True)

        self.priority_input = QComboBox()
        self.priority_input.addItems([
            "낮음",
            "보통",
            "높음"
        ])

        self.category_input = QComboBox()
        self.category_input.addItems([
            "학업",
            "개인",
            "팀플",
            "업무"
        ])

        self.status_input = QComboBox()
        self.status_input.addItems([
            "진행 전",
            "진행 중",
            "완료"
        ])

        for widget in [
            self.date_input,
            self.time_btn,
            self.priority_input,
            self.category_input,
            self.status_input
        ]:
            widget.setStyleSheet("""
                background:#f2f2f7;
                border:none;
                border-radius:12px;
                padding:8px;
            """)

        option_layout.addWidget(
            self.date_input
        )

        option_layout.addWidget(
            self.time_btn
        )

        option_layout.addWidget(
            self.priority_input
        )

        option_layout.addWidget(
            self.category_input
        )

        option_layout.addWidget(
            self.status_input
        )

        input_layout.addLayout(
            option_layout
        )

        # ============================================
        # 버튼
        # ============================================

        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("추가")

        self.add_btn.clicked.connect(
            self.add_or_update_todo
        )

        save_btn = QPushButton("저장")

        save_btn.clicked.connect(
            self.save_data
        )

        load_btn = QPushButton("불러오기")

        load_btn.clicked.connect(
            self.load_data
        )

        for btn in [
            self.add_btn,
            save_btn,
            load_btn
        ]:

            btn.setFixedHeight(42)

            btn.setStyleSheet("""
                QPushButton {
                    background:#007aff;
                    color:white;
                    border:none;
                    border-radius:14px;
                    font-size:15px;
                    font-weight:bold;
                }

                QPushButton:hover {
                    background:#3395ff;
                }
            """)

        btn_layout.addWidget(
            self.add_btn
        )

        btn_layout.addWidget(save_btn)

        btn_layout.addWidget(load_btn)

        input_layout.addLayout(
            btn_layout
        )

        input_card.setLayout(
            input_layout
        )

        main_layout.addWidget(
            input_card
        )

        # ============================================
        # 스크롤
        # ============================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.container = QWidget()

        self.todo_layout = QVBoxLayout()

        self.todo_layout.setSpacing(18)

        self.container.setLayout(
            self.todo_layout
        )

        scroll.setWidget(
            self.container
        )

        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

        self.todo_layout.setAlignment(Qt.AlignTop)

    # ============================================
    # 그룹명
    # ============================================

    def get_group_name(self, deadline_str):
        now = datetime.now()
        today = now.date()
        deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        deadline_date = deadline_dt.date()
        diff = (deadline_date - today).days

        if diff < 0: return "🚨 마감 초과"
        if diff == 0: return "☀️ 오늘"
        if diff == 1: return "🌅 내일"
        if diff < 7: return "🗓️ 이번 주"

        # 이번 달
        if deadline_date.year == today.year and deadline_date.month == today.month:
            return "📅 이번 달"

        # 이번 분기 (1~3월, 4~6월...)
        curr_q = (now.month - 1) // 3
        dead_q = (deadline_dt.month - 1) // 3
        if deadline_date.year == today.year and curr_q == dead_q:
            return f"📊 이번 분기 ({curr_q + 1}분기)"

        # 이번 반기 (상/하반기)
        curr_h = (now.month - 1) // 6
        dead_h = (deadline_dt.month - 1) // 6
        if deadline_date.year == today.year and curr_h == dead_h:
            h_name = "상반기" if dead_h == 0 else "하반기"
            return f"🌓 올해 {h_name}"

        # 올해 남은 일정
        if deadline_date.year == today.year:
            return "✨ 올해 남은 일정"

        # 내년 이후
        return f"🚀 {deadline_date.year}년 이후"

    # ============================================
    # 정렬
    # ============================================

    def sort_todos(self):

        self.todos.sort(
            key=lambda x: datetime.strptime(
                x["deadline"],
                "%Y-%m-%d %H:%M"
            )
        )

    # ============================================
    # 리스트 갱신
    # ============================================

    def refresh_list(self):

        self.todo_widgets.clear()

        while self.todo_layout.count():

            item = self.todo_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.sort_todos()
        active_todos = [t for t in self.todos if not t["completed"]]
        completed_todos = [t for t in self.todos if t["completed"]]

        grouped = {}
        for todo in active_todos:
            group_name = self.get_group_name(todo["deadline"])
            self.ensure_group_state(group_name)
            if group_name not in grouped:
                grouped[group_name] = []
            grouped[group_name].append(todo)

        # 정의된 카테고리 순서 (이 순서대로 화면에 배치됩니다)
        priority_order = [
            "🚨 마감 초과",
            "☀️ 오늘",
            "🌅 내일",
            "🗓️ 이번 주",
            "📅 이번 달",
            "📊 이번 분기 (1분기)", "📊 이번 분기 (2분기)", "📊 이번 분기 (3분기)", "📊 이번 분기 (4분기)",
            "🌓 올해 상반기", "🌓 올해 하반기",
            "✨ 올해 남은 일정"
        ]
        # 정렬된 그룹 목록 생성
        ordered_groups = []
        # 1. 우선순위 리스트에 있는 카테고리 순서대로 추가
        for name in priority_order:
            if name in grouped:
                ordered_groups.append(name)

        # 2. '내년 이후' 처럼 리스트에 없는 나머지 카테고리 추가
        others = sorted([x for x in grouped.keys() if x not in priority_order])
        ordered_groups.extend(others)

        # --- 아래는 기존 UI 생성 로직 (section 버튼 생성 등) ---
        for group_name in ordered_groups:
        # (중략: 기존 코드와 동일하게 버튼 및 TodoItemWidget 추가)

        self.sort_todos()

        active_todos = []
        completed_todos = []

        for todo in self.todos:

            if todo["completed"]:
                completed_todos.append(todo)

            else:
                active_todos.append(todo)

        grouped = {}

        for todo in active_todos:

            group_name = self.get_group_name(
                todo["deadline"]
            )

            self.ensure_group_state(
                group_name
            )

            if group_name not in grouped:
                grouped[group_name] = []

            grouped[group_name].append(todo)

        ordered_groups = []

        ordered_groups.extend(others)

        # 그룹 UI
        for group_name in ordered_groups:

            is_open = self.group_states.get(
                group_name,
                True
            )

            arrow = "▼" if is_open else "▶"

            section = QPushButton(
                f"{arrow} {group_name} ({len(grouped[group_name])})"
            )

            section.clicked.connect(
                lambda checked,
                       g=group_name:
                self.toggle_group(g)
            )

            section.setStyleSheet("""
                QPushButton{
                    background:white;
                    border:none;
                    border-radius:18px;
                    text-align:left;
                    padding:14px;
                    font-size:20px;
                    font-weight:bold;
                }
            """)

            self.todo_layout.addWidget(section)

            if is_open:

                for todo in grouped[group_name]:
                    widget = TodoItemWidget(
                        todo,
                        self.delete_todo,
                        self.edit_todo
                    )

                    self.todo_widgets.append(widget)

                    self.todo_layout.addWidget(widget)

        # ============================================
        # 완료됨 섹션
        # ============================================

        if completed_todos:

            is_open = self.group_states.get(
                "완료됨",
                False
            )

            arrow = "▼" if is_open else "▶"

            completed_btn = QPushButton(
                f"{arrow} 완료됨 ({len(completed_todos)})"
            )

            completed_btn.clicked.connect(
                lambda:
                self.toggle_group("완료됨")
            )

            completed_btn.setStyleSheet("""
                QPushButton{
                    background:white;
                    border:none;
                    border-radius:18px;
                    text-align:left;
                    padding:14px;
                    font-size:18px;
                    font-weight:bold;
                }
            """)

            self.todo_layout.addWidget(
                completed_btn
            )

            if is_open:

                for todo in completed_todos:
                    widget = TodoItemWidget(
                        todo,
                        self.delete_todo,
                        self.edit_todo
                    )

                    self.todo_widgets.append(widget)
                    self.todo_layout.addWidget(widget)

                self.todo_layout.addStretch()

    # ============================================
    # 완료 항목 접기 / 펼치기
    # ============================================

    def toggle_group(self, group_name):

        current = self.group_states.get(
            group_name,
            True
        )

        self.group_states[group_name] = (
            not current
        )

        self.refresh_list()

    def ensure_group_state(self, group_name):

        if group_name not in self.group_states:
            self.group_states[group_name] = True

    # ============================================
    # 추가 / 수정
    # ============================================

    def add_or_update_todo(self):

        title = (
            self.title_input.text()
            .strip()
        )

        if not title:

            QMessageBox.warning(
                self,
                "경고",
                "할 일을 입력하세요."
            )

            return

        todo_data = {
            "title": title,

            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "deadline":
                self.date_input.date().toString("yyyy-MM-dd")
                + " " +
                self.selected_time.toString("HH:mm"),

            "priority":
                self.priority_input.currentText(),

            "category":
                self.category_input.currentText(),

            "status":
                self.status_input.currentText(),

            "completed": False,
        }

        # ============================================
        # 수정 모드
        # ============================================

        if self.editing_todo is not None:

            self.editing_todo.update(
                todo_data
            )

            self.editing_todo = None

            self.add_btn.setText("추가")

        # ============================================
        # 일반 추가
        # ============================================

        else:

            self.todos.append(todo_data)

        self.clear_inputs()

        self.refresh_list()
        self.auto_save_data()

    # ============================================
    # 수정 시작
    # ============================================

    def edit_todo(self, todo):

        self.editing_todo = todo

        self.title_input.setText(
            todo["title"]
        )

        date = datetime.strptime(
            todo["deadline"],
            "%Y-%m-%d %H:%M"
        )

        self.date_input.setDate(
            QDate(
                date.year,
                date.month,
                date.day
            )
        )

        self.selected_time = QTime(
            date.hour,
            date.minute
        )

        self.time_btn.setText(
            f"🕒 {self.selected_time.toString('HH:mm')}"
        )

        self.priority_input.setCurrentText(
            todo["priority"]
        )

        self.category_input.setCurrentText(
            todo["category"]
        )

        self.status_input.setCurrentText(
            todo["status"]
        )

        # 버튼 텍스트 변경
        self.add_btn.setText("수정 완료")

    # ============================================
    # 입력 초기화
    # ============================================

    def clear_inputs(self):

        self.title_input.clear()

        self.date_input.setDate(
            QDate.currentDate()
        )

        self.selected_time = QTime.currentTime()

        self.time_btn.setText(
            f"🕒 {self.selected_time.toString('HH:mm')}"
        )

        self.priority_input.setCurrentIndex(0)

        self.category_input.setCurrentIndex(0)

        self.status_input.setCurrentIndex(0)

    # ============================================
    # 삭제
    # ============================================

    def delete_todo(self, widget):

        reply = QMessageBox.question(
            self,
            "삭제",
            "정말 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:

            self.todos.remove(
                widget.todo_data
            )

            self.refresh_list()
            self.auto_save_data()

    # ============================================
    # 저장
    # ============================================

    def save_data(self):

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "저장",
            "",
            "JSON Files (*.json)"
        )

        if not file_name:
            return

        with open(
            file_name,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.todos,
                f,
                ensure_ascii=False,
                indent=4
            )

        QMessageBox.information(
            self,
            "완료",
            "저장되었습니다."
        )

    # ============================================
    # 불러오기
    # ============================================

    def load_data(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "불러오기",
            "",
            "JSON Files (*.json)"
        )

        if not file_name:
            return

        with open(
            file_name,
            "r",
            encoding="utf-8"
        ) as f:

            self.todos = json.load(f)

        self.refresh_list()

        QMessageBox.information(
            self,
            "완료",
            "불러왔습니다."
        )

    # ============================================
    # 자동 저장
    # ============================================

    def auto_save_data(self):

        with open(
            self.auto_save_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.todos,
                f,
                ensure_ascii=False,
                indent=4
            )

    # ============================================
    # 자동 불러오기
    # ============================================

    def auto_load_data(self):

        if not os.path.exists(
            self.auto_save_file
        ):
            return

        try:

            with open(
                self.auto_save_file,
                "r",
                encoding="utf-8"
            ) as f:

                self.todos = json.load(f)

            self.refresh_list()

        except Exception as e:

            print("자동 불러오기 실패:", e)

    # ============================================
    # 종료 이벤트
    # ============================================

    def closeEvent(self, event):

        self.auto_save_data()

        event.accept()

    # ============================================
    # 시간 선택 함수
    # ============================================

    def open_time_picker(self):

        dialog = TimePickerDialog(
            self.selected_time,
            self
        )

        if dialog.exec_():
            self.selected_time = dialog.get_time()

            self.time_btn.setText(
                f"🕒 {self.selected_time.toString('HH:mm')}"
            )

    # ============================================
    # 알림 검사 함수
    # ============================================
    def check_reminders(self):

        now = datetime.now()

        for todo in self.todos:

            if todo["completed"]:
                continue

            deadline = datetime.strptime(
                todo["deadline"],
                "%Y-%m-%d %H:%M"
            )

            remain = (
                    deadline - now
            ).total_seconds()

            # 마감 초과 자동 처리
            if remain < 0 and not todo["completed"]:

                if todo["status"] != "지연":
                    todo["status"] = "지연"

                    self.auto_save_data()

            title = todo["title"]

            # 30분 전
            if 1700 <= remain <= 1800:

                key = (
                    title,
                    "30"
                )

                if key not in self.notified:
                    QMessageBox.information(
                        self,
                        "알림",
                        f"[30분 전]\n\n{title}"
                    )

                    self.notified.add(key)

            # 10분 전
            elif 500 <= remain <= 600:

                key = (
                    title,
                    "10"
                )

                if key not in self.notified:
                    QMessageBox.information(
                        self,
                        "알림",
                        f"[10분 전]\n\n{title}"
                    )

                    self.notified.add(key)

            # 1분 전
            elif 0 <= remain <= 60:

                key = (
                    title,
                    "1"
                )

                if key not in self.notified:
                    QMessageBox.warning(
                        self,
                        "알림",
                        f"[1분 전]\n\n{title}"
                    )

                    self.notified.add(key)

    # ============================================
    # 자동 갱신
    # ============================================

    def auto_refresh(self):

        for widget in self.todo_widgets:
            widget.update_progress()


# ============================================================================
# 시간 선택 팝업 클래스 06.02 - 환
# ============================================================================


class TimePickerDialog(QDialog):

    def __init__(self, current_time, parent=None):
        super().__init__(parent)

        self.setWindowTitle("시간 선택")

        layout = QVBoxLayout()

        self.hour_spin = QComboBox()
        self.minute_spin = QComboBox()

        for i in range(24):
            self.hour_spin.addItem(f"{i:02d}")

        for i in range(60):
            self.minute_spin.addItem(f"{i:02d}")

        self.hour_spin.setCurrentText(
            current_time.toString("HH")
        )

        self.minute_spin.setCurrentText(
            current_time.toString("mm")
        )

        layout.addWidget(QLabel("시"))
        layout.addWidget(self.hour_spin)

        layout.addWidget(QLabel("분"))
        layout.addWidget(self.minute_spin)

        ok_btn = QPushButton("확인")
        ok_btn.clicked.connect(self.accept)

        layout.addWidget(ok_btn)

        self.setLayout(layout)

    def get_time(self):

        return QTime(
            int(self.hour_spin.currentText()),
            int(self.minute_spin.currentText())
        )


# ============================================================================
# 메모장 기능 확장 및 실행 06.01 - 이지오
# ============================================================================
from PyQt5.QtWidgets import QDialog, QTextEdit


# 1. 메모장 팝업 창
class MemoDialog(QDialog):
    def __init__(self, title, current_memo, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"📋 메모 - {title}")
        self.resize(400, 450)
        self.setStyleSheet("QDialog { background: #f2f2f7; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)

        label = QLabel("내용을 입력하고 완료를 누르거나 창을 닫으면 저장됩니다.")
        label.setFont(QFont("맑은 고딕", 10))
        label.setStyleSheet("color: #8e8e93; margin-bottom: 4px;")
        layout.addWidget(label)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("맑은 고딕", 12))
        self.text_edit.setText(current_memo)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: white;
                border: none;
                border-radius: 14px;
                padding: 12px;
            }
        """)
        layout.addWidget(self.text_edit)

        close_btn = QPushButton("완료")
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #007aff; color: white; border: none;
                border-radius: 12px; font-size: 14px; font-weight: bold; margin-top: 8px;
            }
            QPushButton:hover { background: #3395ff; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)

    def get_text(self):
        return self.text_edit.toPlainText()


# 2. 기존 TodoItemWidget에 추가 (더블클릭 및 메모 아이콘 고정)
original_init = TodoItemWidget.__init__


def new_init(self, todo_data, delete_callback, edit_callback):
    original_init(self, todo_data, delete_callback, edit_callback)

    # 처음부터 제목 뒤에 📝 이모지가 항상 붙어있도록 설정
    if not self.title.text().endswith(" 📝"):
        self.title.setText(todo_data["title"] + " 📝")

    # 마우스 커서를 손가락 모양으로 변경하여 클릭 가능함을 안내
    self.title.setCursor(Qt.PointingHandCursor)
    self.title.setToolTip("더블클릭하여 메모장을 엽니다.")

    # 더블클릭 이벤트 연결
    self.title.mouseDoubleClickEvent = lambda event: open_memo_window(self)


TodoItemWidget.__init__ = new_init

# 3. 기존 ReminderApp 기능 확장 (새 데이터 생성 시 기본 메모 공간 할당)
original_add_or_update = ReminderApp.add_or_update_todo


def new_add_or_update(self):
    title = self.title_input.text().strip()
    if title and self.editing_todo is None:
        todo_data = {
            "title": title,

            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "deadline":
                self.date_input.date().toString("yyyy-MM-dd")
                + " " +
                self.selected_time.toString("HH:mm"),

            "priority": self.priority_input.currentText(),
            "category": self.category_input.currentText(),
            "status": self.status_input.currentText(),
            "completed": False,
            "memo": ""
        }
        self.todos.append(todo_data)
        self.clear_inputs()
        self.refresh_list()
        self.auto_save_data()
    else:
        original_add_or_update(self)


ReminderApp.add_or_update_todo = new_add_or_update


# 4. 메모 창을 열고 데이터를 저장하는 핵심 로직 함수
def open_memo_window(widget):
    todo_data = widget.todo_data
    if "memo" not in todo_data:
        todo_data["memo"] = ""

    dialog = MemoDialog(todo_data["title"], todo_data["memo"], widget.window())
    if dialog.exec_():
        todo_data["memo"] = dialog.get_text()
        widget.window().auto_save_data()


# ============================================
# 실행
# ============================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ReminderApp()

    window.show()

    sys.exit(app.exec_())

# 시간설정 기능 및 정렬

from datetime import datetime

# 할 일 목록을 저장할 리스트
todo_list = []

def add_task():
    print("\n--- [새로운 할 일 추가] ---")
title = input("할 일 내용을 입력하세요: ")

# 1. 마감일 입력 (YYYY-MM-DD 형식)
date_input = input("마감일을 입력하세요 (예: 2026-06-05): ")

# 2. 마감 시간 입력 (HH:MM 형식) - 질문하신 시간 설정 기능
time_input = input("마감 시간을 입력하세요 (예: 15:30): ")

# 3. 예상 소요 시간 입력 (시간 단위)
try:
    estimated_hours = float(input("예상 소요 시간(시간 단위)을 입력하세요 (예: 2.5): "))
except ValueError:
    print("❌ 숫자로만 입력해주세요. 0으로 설정됩니다.")
estimated_hours = 0.0

try:
# 입력받은 날짜와 시간을 하나의 datetime 객체로 결합
    deadline_str = f"{date_input} {time_input}"
    deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")

# 딕셔너리 형태로 할 일 저장
    task = {
"title": title,
"deadline": deadline_dt,
"estimated_hours": estimated_hours,
"completed": False
}
    todo_list.append(task)
    print(f"✅ '{title}' 항목이 추가되었습니다.")

except ValueError:
    print("❌ 날짜나 시간 형식이 올바르지 않습니다. 다시 시도해주세요. (형식: YYYY-MM-DD / HH:MM)")

def show_tasks():
    if not todo_list:
        print("\n등록된 할 일이 없습니다.")
    return

# 마감일(deadline) 기준으로 자동 정렬 (가장 가까운 마감일이 위로)
# '마감일 기반 자동 정렬' 로직에 대입
sorted_list = sorted(todo_list, key=lambda x: x["deadline"])

print("\n--- [할 일 목록 (마감일 순 정렬)] ---")
for idx, task in enumerate(sorted_list, start=1):
    status = "[완료]" if task["completed"] else "[진행중]"
# 출력할 때 보기 좋게 포맷팅
deadline_display = task["deadline"].strftime("%Y-%m-%d %H:%M")
print(f"{idx}. {status} {task['title']}")
print(f" - 마감일시: {deadline_display}")
print(f" - 예상 소요 시간: {task['estimated_hours']}시간")
print("-" * 35)

# 간단한 프로그램 실행 루프
while True:
        print("\n1. 할 일 추가 | 2. 할 일 목록 보기 | 3. 종료")
        choice = input("원하는 메뉴를 선택하세요: ")

        if choice == "1":
            add_task()
        elif choice == "2":
            show_tasks()
        elif choice == "3":
            print("프로그램을 종료합니다.")
            break
        else:
            print("올바른 번호를 선택해주세요.")