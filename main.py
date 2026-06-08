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

        QTimer.singleShot(
            0,
            self.window().refresh_list
        )

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

        self.todo_widgets = []

        for i in reversed(range(self.todo_layout.count())):
            widget = self.todo_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        seen = set()
        unique_todos = []

        for t in self.todos:
            key = (
                t["title"],
                t["deadline"],
                t.get("created_at", "")
            )
            if key not in seen:
                seen.add(key)
                unique_todos.append(t)

        self.todos = unique_todos

        self.todo_widgets.clear()

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

            is_open = self.group_states.get(group_name, True)

            arrow = "▼" if is_open else "▶"

            section = QPushButton(
                f"{arrow} {group_name} ({len(grouped[group_name])})"
            )

            section.clicked.connect(
                lambda checked, g=group_name: self.toggle_group(g)
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

# ============================================================================
# 집중 타이머 기능 추가(6월 3일) - 우상민
# ============================================================================
from PyQt5.QtWidgets import QSpinBox, QProgressBar
from PyQt5.QtCore import QTimer

class TimerDialog(QDialog):
    """시/분/초를 설정하고 시작, 일시정지, 초기화할 수 있는 타이머 팝업"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("⏱ 집중 타이머")
        self.resize(460, 380)

        # 타이머 상태값
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False

        # 1초마다 update_timer 실행
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.setStyleSheet("""
            QDialog {
                background:#f2f2f7;
                font-family:'맑은 고딕';
            }

            QLabel {
                color:#1c1c1e;
            }

            QSpinBox {
                background:white;
                border:none;
                border-radius:12px;
                padding:10px;
                font-size:16px;
            }

            QPushButton {
                color:white;
                border:none;
                border-radius:14px;
                font-size:15px;
                font-weight:bold;
                padding:10px;
            }

            QProgressBar {
                border:none;
                background:#e5e5ea;
                border-radius:10px;
                height:18px;
            }

            QProgressBar::chunk {
                background:#34c759;
                border-radius:10px;
            }
        """)

        self.init_ui()
        self.update_input_time()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        title = QLabel("⏱ 집중 타이머")
        title.setFont(QFont("맑은 고딕", 24, QFont.Bold))
        title.setStyleSheet("color:#ff3b30;")
        main_layout.addWidget(title)

        # 시간 입력 영역
        input_layout = QHBoxLayout()

        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setSuffix(" 시간")

        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setSuffix(" 분")
        self.minute_spin.setValue(25)

        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 59)
        self.second_spin.setSuffix(" 초")

        input_layout.addWidget(self.hour_spin)
        input_layout.addWidget(self.minute_spin)
        input_layout.addWidget(self.second_spin)

        main_layout.addLayout(input_layout)

        # 남은 시간 표시
        self.time_label = QLabel("00:25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("맑은 고딕", 34, QFont.Bold))
        self.time_label.setStyleSheet("""
            QLabel {
                background:white;
                color:#ff3b30;
                border-radius:20px;
                padding:20px;
            }
        """)
        main_layout.addWidget(self.time_label)

        # 진행률 표시
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        main_layout.addWidget(self.progress)

        # 버튼 영역
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("시작")
        self.pause_btn = QPushButton("일시정지")
        self.reset_btn = QPushButton("초기화")

        self.start_btn.setStyleSheet("""
            QPushButton { background:#007aff; }
            QPushButton:hover { background:#3395ff; }
        """)
        self.pause_btn.setStyleSheet("""
            QPushButton { background:#ff9500; }
            QPushButton:hover { background:#ffaa33; }
        """)
        self.reset_btn.setStyleSheet("""
            QPushButton { background:#ff3b30; }
            QPushButton:hover { background:#ff5c52; }
        """)

        self.start_btn.clicked.connect(self.start_timer)
        self.pause_btn.clicked.connect(self.pause_timer)
        self.reset_btn.clicked.connect(self.reset_timer)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.reset_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # 입력값 변경 시 대기 화면 갱신
        self.hour_spin.valueChanged.connect(self.update_input_time)
        self.minute_spin.valueChanged.connect(self.update_input_time)
        self.second_spin.valueChanged.connect(self.update_input_time)

    def update_input_time(self):
        """사용자가 입력한 시/분/초 값을 남은 시간에 반영"""
        if self.is_running:
            return

        hours = self.hour_spin.value()
        minutes = self.minute_spin.value()
        seconds = self.second_spin.value()

        self.total_seconds = hours * 3600 + minutes * 60 + seconds
        self.remaining_seconds = self.total_seconds

        self.update_display()

    def start_timer(self):
        """타이머 시작"""
        if self.remaining_seconds <= 0:
            QMessageBox.warning(
                self,
                "경고",
                "타이머 시간을 1초 이상 설정하세요."
            )
            return

        self.is_running = True
        self.hour_spin.setEnabled(False)
        self.minute_spin.setEnabled(False)
        self.second_spin.setEnabled(False)
        self.timer.start(1000)

    def pause_timer(self):
        """타이머 일시정지"""
        self.timer.stop()
        self.is_running = False

    def reset_timer(self):
        """타이머 초기화"""
        self.timer.stop()
        self.is_running = False

        self.hour_spin.setEnabled(True)
        self.minute_spin.setEnabled(True)
        self.second_spin.setEnabled(True)

        self.update_input_time()
        self.progress.setValue(0)

    def update_timer(self):
        """1초마다 남은 시간을 감소시키고 화면을 갱신"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()

        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.is_running = False

            self.hour_spin.setEnabled(True)
            self.minute_spin.setEnabled(True)
            self.second_spin.setEnabled(True)

            QMessageBox.information(
                self,
                "타이머 종료",
                "설정한 시간이 끝났습니다!"
            )

    def update_display(self):
        """남은 시간과 진행률 화면 갱신"""
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60

        self.time_label.setText(
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )

        if self.total_seconds > 0:
            progress_value = int(
                ((self.total_seconds - self.remaining_seconds)
                 / self.total_seconds) * 100
            )
        else:
            progress_value = 0

        self.progress.setValue(progress_value)


# ============================================================================
# ReminderApp 메인 화면에 타이머 버튼 추가
# ============================================================================

def open_focus_timer(self):
    dialog = TimerDialog(self)
    dialog.exec_()


ReminderApp.open_focus_timer = open_focus_timer


# 기존 init_ui를 보존한 뒤, 입력 카드 아래에 타이머 카드를 추가
original_init_ui_for_timer = ReminderApp.init_ui


def new_init_ui_for_timer(self):
    original_init_ui_for_timer(self)

    timer_card = QFrame()
    timer_card.setStyleSheet("""
        QFrame {
            background:white;
            border-radius:22px;
        }
    """)

    timer_layout = QHBoxLayout()
    timer_layout.setContentsMargins(22, 18, 22, 18)

    timer_label = QLabel("⏱ 집중 타이머")
    timer_label.setFont(QFont("맑은 고딕", 18, QFont.Bold))

    timer_btn = QPushButton("타이머 열기")
    timer_btn.setFixedHeight(44)
    timer_btn.setStyleSheet("""
        QPushButton {
            background:#34c759;
            color:white;
            border:none;
            border-radius:14px;
            font-size:15px;
            font-weight:bold;
        }

        QPushButton:hover {
            background:#4cd964;
        }
    """)
    timer_btn.clicked.connect(self.open_focus_timer)

    timer_layout.addWidget(timer_label)
    timer_layout.addStretch()
    timer_layout.addWidget(timer_btn)

    timer_card.setLayout(timer_layout)

    # 화면 구조: 제목(0), 입력 카드(1), 타이머 카드(2), 스크롤 영역(3)
    self.layout().insertWidget(2, timer_card)


ReminderApp.init_ui = new_init_ui_for_timer


# ============================================================================
# 체크리스트 - 06.08 -지오
# ============================================================================

class ChecklistDialog(QDialog):
    """세련된 밑줄 스타일과 개별 삭제 기능이 포함된 체크리스트 팝업 창"""

    def __init__(self, title, current_items, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"✅ 체크리스트 - {title}")
        self.resize(420, 500)
        self.setStyleSheet("""
            QDialog {
                background: #f2f2f7;
                font-family: '맑은 고딕';
            }
            QLabel {
                color: #1c1c1e;
            }
            QLineEdit {
                background: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                border-bottom: 2px solid #007aff;
            }
            QPushButton {
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
        """)

        self.items = []

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        label = QLabel("체크할 항목을 관리하세요. 더블클릭으로 안전하게 진입된 창입니다.")
        label.setFont(QFont("맑은 고딕", 10))
        label.setStyleSheet("color: #8e8e93;")
        layout.addWidget(label)

        input_layout = QHBoxLayout()
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("새로운 체크 항목을 입력하고 Enter 또는 추가 클릭")
        self.item_input.returnPressed.connect(self.add_item_from_input)

        add_btn = QPushButton("추가")
        add_btn.setFixedWidth(72)
        add_btn.setStyleSheet("""
            QPushButton { background: #34c759; color: white; }
            QPushButton:hover { background: #2cd054; }
        """)
        add_btn.clicked.connect(self.add_item_from_input)

        input_layout.addWidget(self.item_input)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: white;
                border: none;
                border-radius: 14px;
            }
        """)

        self.list_widget = QWidget()
        self.list_widget.setStyleSheet("background: white;")
        self.list_layout = QVBoxLayout()
        self.list_layout.setContentsMargins(12, 12, 12, 12)
        self.list_layout.setSpacing(0)
        self.list_layout.addStretch()
        self.list_widget.setLayout(self.list_layout)
        self.scroll_area.setWidget(self.list_widget)
        layout.addWidget(self.scroll_area)

        close_btn = QPushButton("완료")
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet("""
            QPushButton { background: #007aff; color: white; }
            QPushButton:hover { background: #3395ff; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

        if current_items:
            for item in current_items:
                self.add_item(item.get("text", ""), item.get("checked", False))

    def add_item_from_input(self):
        text = self.item_input.text().strip()
        if text:
            self.add_item(text, False)
            self.item_input.clear()

    def add_item(self, text="", checked=False):
        # 공책 노트 패드 감성의 하단 밑줄 프레임 생성
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: none;
                border-bottom: 2px solid #d1d1d6; /* 선명한 가로 밑줄 스타일 */
            }
        """)
        frame_layout = QHBoxLayout()
        frame_layout.setContentsMargins(4, 8, 4, 8)

        checkbox = QCheckBox(text)
        checkbox.setChecked(checked)
        checkbox.setStyleSheet("""
            QCheckBox {
                border: none;
                font-size: 14px;
                color: #1c1c1e;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(24, 24)
        del_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ff3b30;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background: #ffeaea;
                border-radius: 12px;
            }
        """)
        del_btn.clicked.connect(lambda: self.delete_item(item_frame, checkbox))

        frame_layout.addWidget(checkbox, 1)
        frame_layout.addWidget(del_btn)
        item_frame.setLayout(frame_layout)

        self.list_layout.insertWidget(self.list_layout.count() - 1, item_frame)
        self.items.append((item_frame, checkbox))

    def delete_item(self, frame, checkbox):
        self.list_layout.removeWidget(frame)
        frame.deleteLater()
        self.items = [item for item in self.items if item[1] != checkbox]

    def get_items(self):
        result = []
        for _, checkbox in self.items:
            text = checkbox.text().strip()
            if text:
                result.append({
                    "text": text,
                    "checked": checkbox.isChecked()
                })
        return result


def open_checklist_window(widget):
    todo_data = widget.todo_data
    if "checklist" not in todo_data:
        todo_data["checklist"] = []

    dialog = ChecklistDialog(
        todo_data["title"],
        todo_data["checklist"],
        widget.window()
    )

    if dialog.exec_():
        todo_data["checklist"] = dialog.get_items()
        widget.window().auto_save_data()


def find_layout_containing_widget(layout, target_widget):
    if layout is None:
        return None
    if layout.indexOf(target_widget) >= 0:
        return layout
    for index in range(layout.count()):
        child_layout = layout.itemAt(index).layout()
        found_layout = find_layout_containing_widget(child_layout, target_widget)
        if found_layout is not None:
            return found_layout
    return None


# 기존의 __init__ 체인을 안전하게 백업 및 확장 호출
original_init_for_checklist = TodoItemWidget.__init__


def new_init_for_checklist(self, todo_data, delete_callback, edit_callback):
    # 상위 메모장 이모티콘 장착 로직 완료 후 제어권을 이어받음
    original_init_for_checklist(self, todo_data, delete_callback, edit_callback)

    if "checklist" not in self.todo_data:
        self.todo_data["checklist"] = []

    # 체크리스트 진입용 이모티콘 라벨 별도 구성
    self.checklist_icon = QLabel("✅")
    self.checklist_icon.setFont(QFont("맑은 고딕", 15, QFont.Bold))
    self.checklist_icon.setCursor(Qt.PointingHandCursor)
    self.checklist_icon.setToolTip("더블클릭하여 체크리스트를 엽니다.")

    self.checklist_icon.mouseDoubleClickEvent = lambda event: open_checklist_window(self)

    title_layout = find_layout_containing_widget(self.layout(), self.title)
    if title_layout is not None:
        title_index = title_layout.indexOf(self.title)
        if title_index >= 0:
            # 📝와 ✅를 일렬 횡대로 묶어줄 초정밀 가로 레이아웃 신설
            title_row = QHBoxLayout()
            title_row.setContentsMargins(0, 0, 0, 0)
            title_row.setSpacing(6)  # 메모장과 체크 사이의 완벽하고 자연스러운 간격

            title_layout.takeAt(title_index)
            title_row.addWidget(self.title)  # 제목 및 📝 이모티콘 배치
            title_row.addWidget(self.checklist_icon)  # 바로 오른쪽에 ✅ 이모티콘 밀착 배치
            title_row.addStretch()  # 나머지 공백은 뒤로 밀어내 정렬 고정

            title_layout.insertLayout(title_index, title_row)


TodoItemWidget.__init__ = new_init_for_checklist

# 데이터 저장 공간 보장 오버라이딩 패치
original_add_or_update_for_checklist = ReminderApp.add_or_update_todo


def new_add_or_update_for_checklist(self):
    title = self.title_input.text().strip()
    if title and self.editing_todo is None:
        todo_data = {
            "title": title,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "deadline": self.date_input.date().toString("yyyy-MM-dd") + " " + self.selected_time.toString("HH:mm"),
            "priority": self.priority_input.currentText(),
            "category": self.category_input.currentText(),
            "status": self.status_input.currentText(),
            "completed": False,
            "memo": "",
            "checklist": []
        }
        self.todos.append(todo_data)
        self.clear_inputs()
        self.refresh_list()
        self.auto_save_data()
    else:
        original_add_or_update_for_checklist(self)


ReminderApp.add_or_update_todo = new_add_or_update_for_checklist

# ============================================================================
# [추가 코드] 체크리스트 실시간 개수 카운트 (a/n) 표시 연동
# ============================================================================

def update_checklist_counter(widget):
    """체크리스트의 총 개수(n)와 완료된 개수(a)를 계산하여 표시를 갱신합니다."""
    checklist = widget.todo_data.get("checklist", [])
    n = len(checklist)
    a = sum(1 for item in checklist if item.get("checked", False))
    widget.checklist_icon.setText(f" ✅ ({a}/{n})")


# 1. 팝업창에서 '완료'를 눌렀을 때 카운터가 즉시 갱신되도록 함수 재정의
def open_checklist_window(widget):
    todo_data = widget.todo_data
    if "checklist" not in todo_data:
        todo_data["checklist"] = []

    dialog = ChecklistDialog(
        todo_data["title"],
        todo_data["checklist"],
        widget.window()
    )

    if dialog.exec_():
        todo_data["checklist"] = dialog.get_items()
        update_checklist_counter(widget)  # 데이터 저장 후 즉시 카운터 갱신
        widget.window().auto_save_data()


# 2. 처음 프로그램이 켜지거나 리스트가 갱신되어 카드가 생성될 때 초기 카운터 표시 래핑
original_counter_init = TodoItemWidget.__init__


def patched_todo_init_with_counter(self, todo_data, delete_callback, edit_callback):
    # 이전 패치 기능(UI 배치 등)을 먼저 실행합니다.
    original_counter_init(self, todo_data, delete_callback, edit_callback)
    # 생성이 끝난 직후 처음 저장되어 있던 카운트(a/n)를 화면에 반영합니다.
    update_checklist_counter(self)


# 최종적으로 생성자 변경 적용
TodoItemWidget.__init__ = patched_todo_init_with_counter

# ============================================
# 실행
# ============================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ReminderApp()

    window.show()

    sys.exit(app.exec_())