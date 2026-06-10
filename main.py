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

        side_bar.setFixedWidth(15)

        side_bar.setStyleSheet(f"""
            background:{color};
            border-radius:5px;
        """)

        # ============================================
        # 체크박스 (회색 배경 + 라운드 검은 가장자리 해결)
        # ============================================
        self.check = QCheckBox()
        self.check.setChecked(todo_data["completed"])
        self.check.stateChanged.connect(self.toggle_complete)

        self.check.setStyleSheet("""
                   QCheckBox {
                       spacing: 10px;
                       color: #1c1c1e;
                       font-size: 15px;
                       background: transparent; /* ✅ 부모 배경이 새어 검은 테두리 생기는 현상 차단 */
                   }
                   QCheckBox::indicator {
                       width: 22px;
                       height: 22px;
                       border-radius: 7px;   /* 부드럽고 정확한 라운드 처리 */
                       background-color: #e5e5ea; /* ✅ 살짝 회색 배경 (iOS/Android 시스템 그레이 계열) */
                       border: none;
                   }
                   QCheckBox::indicator:checked {
                       background-color: #007aff; /* 체크 시 파란색으로 변경 */
                       /* Qt가 자동으로 흰색 체크마크를 그려줍니다. 별도 아이콘 파일 필요 없음 */
                   }
               """)

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
        # 공통 스타일 (먼저 정의!)
        # ============================================
        tag_style = """
            background:#f2f2f7; color:#3a3a3c; border-radius:10px; padding:6px 12px; font-size:15px; font-weight:600;
        """

        # ✅ 1. 메타 정보 태그 생성 (중복 제거 & 안정화)
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(8)

        date_val = str(todo_data.get("deadline", ""))
        priority_val = todo_data.get("priority", "보통")
        category_val = todo_data.get("category", "개인")
        status_val = todo_data.get("status", "진행 전")

        date_label = QLabel(f'📅 {date_val}')
        priority_icon = {"높음": "🔥", "보통": "⭐", "낮음": "🌱"}
        priority_label = QLabel(f'{priority_icon.get(priority_val, "⭐")} {priority_val}')
        category_label = QLabel(f'📁 {category_val}')
        status_icon = {"진행 전": "🕓", "진행 중": "⏳", "완료": "✅", "지연": "🚨"}
        self.status_tag = QLabel(f'{status_icon.get(status_val, "🕓")} {status_val}')

        # ✅ 시작 시간 태그 (문자열 공백 제거 후 길이 체크)
        start_time_raw = str(todo_data.get("start_time", "")).strip()
        if len(start_time_raw) >= 5:
            start_tag = QLabel(f'🕐 {start_time_raw[:16]}')
            start_tag.setStyleSheet(tag_style)
            meta_layout.addWidget(start_tag)

        # ⬇️ 리스트 내부의 status_label을 self.status_tag로 변경
        for tag in [date_label, priority_label, category_label, self.status_tag]:
            tag.setStyleSheet(tag_style)
            meta_layout.addWidget(tag)

        meta_layout.addStretch()
        text_layout.addLayout(meta_layout)

        # ============================================
        # 알림 기능 관련
        # ============================================
        from PyQt5.QtWidgets import QProgressBar

        self.progress = QProgressBar()

        start_str = todo_data.get("start_time", "") or ""
        if start_str and len(start_str) >= 5:
            try:
                created = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            except ValueError:
                created = datetime.strptime(todo_data["created_at"], "%Y-%m-%d %H:%M:%S")
        else:
            created = datetime.strptime(todo_data["created_at"], "%Y-%m-%d %H:%M:%S")

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
            font-size:15px;
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
            start_str = self.todo_data.get("start_time", "") or ""
            if start_str and len(start_str) >= 5:
                try:
                    created = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    created = datetime.strptime(self.todo_data.get("created_at", ""), "%Y-%m-%d %H:%M:%S")
            else:
                created = datetime.strptime(self.todo_data.get("created_at", ""), "%Y-%m-%d %H:%M:%S")

            deadline = datetime.strptime(self.todo_data.get("deadline", ""), "%Y-%m-%d %H:%M")
            now = datetime.now()

            total_seconds = (deadline - created).total_seconds()
            remain_seconds = (deadline - now).total_seconds()

            if remain_seconds <= 0:
                percent = 0
            elif total_seconds <= 0:
                percent = 100
            else:
                ratio = remain_seconds / total_seconds
                percent = int((ratio ** 2) * 100)

            percent = max(0, min(percent, 100))
            self.progress.setValue(percent)

            if percent > 60:
                color = "#34c759"
            elif percent > 30:
                color = "#ffcc00"
            elif percent > 10:
                color = "#ff9500"
            else:
                color = "#ff3b30"

            self.progress.setStyleSheet(
                f"""QProgressBar {{ border:none; background:#e5e5ea; border-radius:6px; }} QProgressBar::chunk {{ background:{color}; border-radius:6px; }} """)

            # ✅ 실시간 마감 감지 및 '지연' 태그 자동 변경 (1초 단위 실행)
            if remain_seconds <= 0 and not self.check.isChecked():
                # 상태가 처음으로 '지연'으로 바뀔 때만 데이터베이스 저장하여 I/O 과부하 방지
                if self.todo_data.get("status") != "지연":
                    self.todo_data["status"] = "지연"
                    self.window().auto_save_data()

                self.status_tag.setText("🚨 지연")
                self.countdown_label.setText("🚨 마감 초과")

            elif self.check.isChecked():
                # 완료 체크 시 상태 즉시 반영 (타이머에서 중복 저장 방지용)
                if self.todo_data.get("status") != "완료":
                    self.todo_data["status"] = "완료"
                    self.window().auto_save_data()
                self.status_tag.setText("✅ 완료")
                self.countdown_label.setText("⏰ 마감 완료")

            else:
                # 마감 이전 정상 진행 중 상태
                hours = int(remain_seconds // 3600)
                minutes = int((remain_seconds % 3600) // 60)
                second = int((remain_seconds % 3600) % 60)
                self.countdown_label.setText(f"⏰ {hours}시간 {minutes}분 {second}초 남음")

            if percent > 60:
                card_bg = "#ffffff"
            elif percent > 30:
                card_bg = "#fff9e6"
            elif percent > 10:
                card_bg = "#fff1e6"
            else:
                card_bg = "#ffeaea"

            if not self.check.isChecked():
                self.setStyleSheet(f"""QFrame {{ background:{card_bg}; border-radius:22px; }} """)

        except Exception:
            # 날짜 형식 오류 시 프로그램 강제 종료 방지
            self.progress.setValue(0)
            self.countdown_label.setText("⏰ 날짜 정보 오류")

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
        # 입력 카드 (레이아웃 정재)
        # ============================================

        input_card = QFrame()
        input_card.setStyleSheet("""
                    QFrame {
                        background:white;
                        border-radius:24px;
                    }
                """)

        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(24, 24, 24, 24)
        input_layout.setSpacing(12)

        # --------------------------------------------------
        # 1. 제목 입력
        # --------------------------------------------------
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("할 일을 입력하세요")
        self.title_input.setStyleSheet("""
                    QLineEdit { border:none; font-size:18px; padding:12px; background:#f2f2f7; border-radius:14px; }
                """)
        input_layout.addWidget(self.title_input)

        # ============================================
        # 2 & 3. 시작/마감 시점 (같은 줄에 정렬)
        # ============================================
        time_picker_layout = QHBoxLayout()
        time_picker_layout.setSpacing(14)

        # 시작 시점 컬럼
        start_col = QVBoxLayout()
        start_col.addWidget(QLabel("🕐 시작"), alignment=Qt.AlignLeft)

        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        # ✅ 날짜 형식을 직관적인 'YYYY-MM-DD'로 고정 (지역 설정 의존 제거)
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.start_date_input.setToolTip("📅 캘린더를 클릭하여 시작 날짜를 선택하세요")
        self.start_date_input.setStyleSheet("""
            background:#f2f2f7; border:none; border-radius:10px; padding:8px 12px; 
            font-size:30px; color:#1c1c1e; font-weight:bold; selection-background-color:#3395ff;
        """)

        self.selected_start_time = QTime.currentTime()
        self.start_time_btn = QPushButton(f"🕒 {self.selected_start_time.toString('HH:mm')}")
        self.start_time_btn.clicked.connect(self.open_start_time_picker)
        self.start_time_btn.setToolTip("🕒 시작 시간을 선택하세요")
        self.start_time_btn.setStyleSheet("""
            background:#f2f2f7; border:none; border-radius:10px; padding:8px 14px; 
            font-size:30px; min-width:75px; color:#1c1c1e; font-weight:bold;
        """)

        start_row = QHBoxLayout()
        start_row.addWidget(self.start_date_input, 1)
        start_row.addWidget(self.start_time_btn)
        start_col.addLayout(start_row)

        time_picker_layout.addLayout(start_col, 1)
        time_picker_layout.addSpacing(20)

        # 마감 시점 컬럼
        deadline_col = QVBoxLayout()
        deadline_col.addWidget(QLabel("📅 마감"), alignment=Qt.AlignLeft)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        # ✅ 날짜 형식 통일
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setToolTip("📅 캘린더를 클릭하여 마감 날짜를 선택하세요")
        self.date_input.setStyleSheet("""
            background:#f2f2f7; border:none; border-radius:10px; padding:8px 12px; 
            font-size:30px; color:#1c1c1e; font-weight:bold; selection-background-color:#3395ff;
        """)

        self.selected_time = QTime.currentTime()
        self.time_btn = QPushButton(f"🕒 {self.selected_time.toString('HH:mm')}")
        self.time_btn.clicked.connect(self.open_time_picker)
        self.time_btn.setToolTip("🕒 마감 시간을 선택하세요")
        self.time_btn.setStyleSheet("""
            background:#f2f2f7; border:none; border-radius:10px; padding:8px 14px; 
            font-size:30px; min-width:75px; color:#1c1c1e; font-weight:bold;
        """)

        deadline_row = QHBoxLayout()
        deadline_row.addWidget(self.date_input, 1)
        deadline_row.addWidget(self.time_btn)
        deadline_col.addLayout(deadline_row)

        time_picker_layout.addLayout(deadline_col, 1)

        input_layout.addLayout(time_picker_layout)

        # --------------------------------------------------
        # 4. 설정 영역 (중요도, 카테고리, 상태) -> 카드 내부 유지 but 시각적 박스 제거
        # --------------------------------------------------

        # 1️⃣ 위젯 먼저 생성 (이전 오류는 이 순서가 빠졌기 때문이었습니다)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["낮음", "보통", "높음"])

        self.category_input = QComboBox()
        self.category_input.addItems(["학업", "개인", "팀플", "업무"])

        self.status_input = QComboBox()
        self.status_input.addItems(["진행 전", "진행 중", "완료"])

        # 2. 카드의 흰색 배경과 자연스럽게 합쳐지도록 스타일 적용 (테두리/배경 투명화 & 드롭다운 검은 테두리 해결)
        combo_style = """
            QComboBox {
                background-color: #f2f2f7; /* 부모와 동일한 연한 회색으로 고정하여 배경 새는 현상 차단 */
                border: none;
                border-radius: 10px;
                padding: 6px 14px;
                font-size: 25px; /* 콤보박스 내부 여백 고려해 적절히 조정 */
                color: #1c1c1e;
                font-weight:bold;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }
            QComboBox::down-arrow {
                image: none; /* 기본 화살표 제거 (원하시면 SVG 이미지로 교체 가능) */
                border: none;
                background: transparent;
            }
            /* ✅ 드롭다운 목록의 검은 테두리, 배경 새는 현상, 모서리 간극 완전 차단 */
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e5e5ea;
                border-radius: 10px;
                outline: none;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                background-color: transparent;
                color: #1c1c1e;
                padding: 8px;
                border-radius: 6px;
                margin: 2px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #007aff;
                color: white;
            }
        """
        for combo in [self.priority_input, self.category_input, self.status_input]:
            combo.setStyleSheet(combo_style)

        # 3. 가로 행 레이아웃 구성
        settings_row_layout = QHBoxLayout()
        settings_row_layout.setSpacing(28)
        settings_row_layout.setContentsMargins(0, 6, 0, 0)  # 카드 내부 상단 여백만 확보

        for label_text, combo in [
            ("🔥 중요도", self.priority_input),
            ("📂 카테고리", self.category_input),
            ("✅ 상태", self.status_input)
        ]:
            col = QVBoxLayout()
            col.addWidget(QLabel(label_text))
            col.setAlignment(Qt.AlignVCenter)
            col.addWidget(combo)
            settings_row_layout.addLayout(col, 1)

        # 4️⃣ 기존과 동일하게 'input_card' 내부에 추가 (레이아웃 구조 변경 없음)
        input_layout.addLayout(settings_row_layout)

        # --------------------------------------------------
        # 5. 버튼 영역 (기존 유지)
        # --------------------------------------------------
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("추가")
        self.add_btn.clicked.connect(self.add_or_update_todo)

        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_data)

        load_btn = QPushButton("불러오기")
        load_btn.clicked.connect(self.load_data)

        for btn in [self.add_btn, save_btn, load_btn]:
            btn.setFixedHeight(42)
            btn.setStyleSheet("""
                        QPushButton { background:#007aff; color:white; border:none; border-radius:14px; font-size:15px; font-weight:bold; }
                        QPushButton:hover { background:#3395ff; }
                    """)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(load_btn)
        input_layout.addLayout(btn_layout)

        input_card.setLayout(input_layout)
        main_layout.addWidget(input_card)

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
    # 정렬 (예외 안전 처리)
    # ============================================
    def sort_todos(self):
        def safe_date_key(x):
            try:
                return datetime.strptime(str(x.get("deadline", "")), "%Y-%m-%d %H:%M")
            except ValueError:
                return datetime.max  # 깨진 데이터는 맨 뒤로 밀어냄

        self.todos.sort(key=safe_date_key)

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
                    try:
                        widget = TodoItemWidget(todo, self.delete_todo, self.edit_todo)
                        self.todo_widgets.append(widget)
                        self.todo_layout.addWidget(widget)
                    except Exception as e:
                        print(f"[경고] 위젯 렌더링 실패 ({todo.get('title', 'Unknown')}): {e}")

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

        deadline_str = self.date_input.date().toString("yyyy-MM-dd") + " " + self.selected_time.toString("HH:mm")
        start_str = self.start_date_input.date().toString("yyyy-MM-dd") + " " + self.selected_start_time.toString(
            "HH:mm")

        todo_data = {
            "title": title,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "deadline": deadline_str,
            "start_time": start_str,  # 👈 시작 시간 저장 키 추가
            "priority": self.priority_input.currentText(),
            "category": self.category_input.currentText(),
            "status": self.status_input.currentText(),
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

        # 1. 제목 설정
        self.title_input.setText(todo.get("title", ""))

        # 2. 마감 날짜/시간 파싱 (예외 처리 추가)
        deadline_str = str(todo.get("deadline", ""))
        try:
            date_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        except ValueError:
            # 저장 형식이 다르면 현재 시간으로 대체하여 crashing 방지
            date_dt = datetime.now()

        self.date_input.setDate(QDate(date_dt.year, date_dt.month, date_dt.day))
        self.selected_time = QTime(date_dt.hour, date_dt.minute)
        self.time_btn.setText(f"🕒 {self.selected_time.toString('HH:mm')}")

        # 3. 시작 날짜/시간 파싱 (빈값/없음 안전 처리)
        start_data = str(todo.get("start_time", ""))
        if len(start_data) >= 5:
            try:
                start_dt = datetime.strptime(start_data, "%Y-%m-%d %H:%M")
            except ValueError:
                start_dt = date_dt  # 파싱 실패 시 마감 시간과 동일하게 처리
        else:
            start_dt = date_dt  # 데이터가 아예 없을 경우 마감 시간과 동일하게 처리

        self.start_date_input.setDate(QDate(start_dt.year, start_dt.month, start_dt.day))
        self.selected_start_time = QTime(start_dt.hour, start_dt.minute)
        self.start_time_btn.setText(f"🕒 {self.selected_start_time.toString('HH:mm')}")

        # 4. 콤보박스 안전 설정 (공백 제거 및 매칭 실패 대비)
        def safe_set_combo(combo, text):
            clean_text = text.strip() if text else ""
            idx = combo.findText(clean_text)
            combo.setCurrentIndex(idx if idx != -1 else 0)

        safe_set_combo(self.priority_input, todo.get("priority"))
        safe_set_combo(self.category_input, todo.get("category"))
        safe_set_combo(self.status_input, todo.get("status"))

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

        self.start_date_input.setDate(QDate.currentDate())
        self.selected_start_time = QTime.currentTime()
        self.start_time_btn.setText(f"🕒 {self.selected_start_time.toString('HH:mm')}")


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
    # 자동 불러오기 (데이터 안전성 강화)
    # ============================================
    def auto_load_data(self):
        if not os.path.exists(self.auto_save_file):
            self.todos = []
            return

        try:
            with open(self.auto_save_file, "r", encoding="utf-8") as f:
                raw_list = json.load(f)

            # ✅ 레거시 데이터 호환 & 누락 필드 자동 보완
            safe_todos = []
            for item in raw_list:
                if not isinstance(item, dict):
                    continue
                item.setdefault("priority", "보통")
                item.setdefault("category", "개인")
                item.setdefault("status", "진행 전")
                item.setdefault("completed", False)
                item.setdefault("memo", "")
                item.setdefault("checklist", [])
                if not item.get("start_time"):
                    item["start_time"] = ""
                safe_todos.append(item)

            self.todos = safe_todos
            self.refresh_list()

        except Exception as e:
            print(f"[경고] 데이터 파일 손상 또는 읽기 실패 ({e}). 초기 상태로 시작합니다.")
            self.todos = []

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

    def open_start_time_picker(self):
        dialog = TimePickerDialog(self.selected_start_time, self)
        if dialog.exec_():
            self.selected_start_time = dialog.get_time()
            self.start_time_btn.setText(f"🕒 {self.selected_start_time.toString('HH:mm')}")

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
# 일반 타이머 + 뽀모도로 통합 기능
# ============================================================================
from PyQt5.QtWidgets import QSpinBox, QProgressBar, QStackedWidget
from PyQt5.QtCore import QTimer


class TimerDialog(QDialog):
    """일반 타이머와 뽀모도로를 한 창에서 전환해 사용하는 통합 타이머."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("⏱ 통합 집중 타이머")
        self.resize(500, 520)

        # 현재 타이머 종류: normal 또는 pomodoro
        self.timer_type = "normal"
        self.is_running = False

        # 공통 시간 상태
        self.total_seconds = 25 * 60
        self.remaining_seconds = self.total_seconds

        # 뽀모도로 기본 규칙
        self.focus_minutes = 25
        self.short_break_minutes = 5
        self.long_break_minutes = 15
        self.max_cycle = 4

        # 뽀모도로 진행 상태
        self.pomodoro_mode = "focus"  # focus, short_break, long_break
        self.cycle_count = 1

        # 일반/뽀모도로가 함께 사용하는 단 하나의 QTimer
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
                font-size:14px;
                font-weight:bold;
                padding:10px;
            }

            QProgressBar {
                border:none;
                background:#e5e5ea;
                border-radius:10px;
                height:18px;
            }
        """)

        self.init_ui()
        self.switch_to_normal()

    # ------------------------------------------------------------------------
    # 화면 구성
    # ------------------------------------------------------------------------
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("⏱ 통합 집중 타이머")
        title.setFont(QFont("맑은 고딕", 24, QFont.Bold))
        title.setStyleSheet("color:#ff3b30;")
        main_layout.addWidget(title)

        # 같은 팝업 안에서 일반 타이머/뽀모도로 전환
        mode_layout = QHBoxLayout()

        self.normal_mode_btn = QPushButton("일반 타이머")
        self.pomodoro_mode_btn = QPushButton("🍅 뽀모도로")

        self.normal_mode_btn.clicked.connect(self.switch_to_normal)
        self.pomodoro_mode_btn.clicked.connect(self.switch_to_pomodoro)

        mode_layout.addWidget(self.normal_mode_btn)
        mode_layout.addWidget(self.pomodoro_mode_btn)
        main_layout.addLayout(mode_layout)

        # 종류별 설정 화면만 교체하고, 시간 표시와 제어 버튼은 함께 사용
        self.setting_stack = QStackedWidget()
        self.setting_stack.addWidget(self.create_normal_setting_page())
        self.setting_stack.addWidget(self.create_pomodoro_setting_page())
        main_layout.addWidget(self.setting_stack)

        self.status_label = QLabel("일반 타이머")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("맑은 고딕", 17, QFont.Bold))
        main_layout.addWidget(self.status_label)

        self.time_label = QLabel("00:25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("맑은 고딕", 38, QFont.Bold))
        main_layout.addWidget(self.time_label)

        self.cycle_label = QLabel("")
        self.cycle_label.setAlignment(Qt.AlignCenter)
        self.cycle_label.setFont(QFont("맑은 고딕", 13, QFont.Bold))
        self.cycle_label.setStyleSheet("color:#8e8e93;")
        main_layout.addWidget(self.cycle_label)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        main_layout.addWidget(self.progress)

        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("시작")
        self.pause_btn = QPushButton("일시정지")
        self.reset_btn = QPushButton("초기화")
        self.next_btn = QPushButton("다음 단계")

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
        self.next_btn.setStyleSheet("""
            QPushButton { background:#34c759; }
            QPushButton:hover { background:#4cd964; }
        """)

        self.start_btn.clicked.connect(self.start_timer)
        self.pause_btn.clicked.connect(self.pause_timer)
        self.reset_btn.clicked.connect(self.reset_timer)
        self.next_btn.clicked.connect(self.next_pomodoro_stage)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.reset_btn)
        control_layout.addWidget(self.next_btn)
        main_layout.addLayout(control_layout)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("맑은 고딕", 11))
        self.info_label.setStyleSheet("color:#8e8e93;")
        main_layout.addWidget(self.info_label)

        self.setLayout(main_layout)

    def create_normal_setting_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

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

        self.hour_spin.valueChanged.connect(self.update_normal_input_time)
        self.minute_spin.valueChanged.connect(self.update_normal_input_time)
        self.second_spin.valueChanged.connect(self.update_normal_input_time)

        layout.addWidget(self.hour_spin)
        layout.addWidget(self.minute_spin)
        layout.addWidget(self.second_spin)

        page.setLayout(layout)
        return page

    def create_pomodoro_setting_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        rule_label = QLabel(
            "25분 집중 → 5분 짧은 휴식 → 4사이클 후 15분 긴 휴식"
        )
        rule_label.setAlignment(Qt.AlignCenter)
        rule_label.setStyleSheet("""
            QLabel {
                background:white;
                border-radius:14px;
                padding:12px;
                color:#3a3a3c;
                font-weight:bold;
            }
        """)

        layout.addWidget(rule_label)
        page.setLayout(layout)
        return page

    # ------------------------------------------------------------------------
    # 일반 타이머/뽀모도로 전환
    # ------------------------------------------------------------------------
    def stop_before_switch(self):
        self.timer.stop()
        self.is_running = False
        self.set_normal_inputs_enabled(True)

    def switch_to_normal(self):
        self.stop_before_switch()
        self.timer_type = "normal"
        self.setting_stack.setCurrentIndex(0)

        self.normal_mode_btn.setStyleSheet("""
            QPushButton { background:#007aff; }
        """)
        self.pomodoro_mode_btn.setStyleSheet("""
            QPushButton { background:#8e8e93; }
        """)

        self.next_btn.hide()
        self.cycle_label.hide()
        self.info_label.setText("시·분·초를 직접 설정하는 일반 집중 타이머")

        self.update_normal_input_time()

    def switch_to_pomodoro(self):
        self.stop_before_switch()
        self.timer_type = "pomodoro"
        self.setting_stack.setCurrentIndex(1)

        self.normal_mode_btn.setStyleSheet("""
            QPushButton { background:#8e8e93; }
        """)
        self.pomodoro_mode_btn.setStyleSheet("""
            QPushButton { background:#ff3b30; }
        """)

        self.next_btn.show()
        self.cycle_label.show()
        self.info_label.setText(
            "집중이 끝나면 휴식으로, 휴식이 끝나면 다음 집중으로 전환됩니다."
        )

        self.reset_pomodoro_state()
        self.update_display()

    # ------------------------------------------------------------------------
    # 공통 제어
    # ------------------------------------------------------------------------
    def start_timer(self):
        if self.remaining_seconds <= 0:
            if self.timer_type == "pomodoro":
                self.next_pomodoro_stage()
            else:
                QMessageBox.warning(
                    self,
                    "경고",
                    "타이머 시간을 1초 이상 설정하세요."
                )
                return

        self.is_running = True

        if self.timer_type == "normal":
            self.set_normal_inputs_enabled(False)

        self.timer.start(1000)

    def pause_timer(self):
        self.timer.stop()
        self.is_running = False

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False

        if self.timer_type == "normal":
            self.set_normal_inputs_enabled(True)
            self.update_normal_input_time()
        else:
            self.reset_pomodoro_state()
            self.update_display()

        self.progress.setValue(0)

    def update_timer(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()

        if self.remaining_seconds > 0:
            return

        self.timer.stop()
        self.is_running = False

        if self.timer_type == "normal":
            self.set_normal_inputs_enabled(True)
            QMessageBox.information(
                self,
                "타이머 종료",
                "설정한 시간이 끝났습니다!"
            )
        else:
            QMessageBox.information(
                self,
                "뽀모도로 알림",
                self.get_pomodoro_finish_message()
            )
            self.next_pomodoro_stage()

    # ------------------------------------------------------------------------
    # 일반 타이머
    # ------------------------------------------------------------------------
    def set_normal_inputs_enabled(self, enabled):
        self.hour_spin.setEnabled(enabled)
        self.minute_spin.setEnabled(enabled)
        self.second_spin.setEnabled(enabled)

    def update_normal_input_time(self):
        if self.timer_type != "normal" or self.is_running:
            return

        hours = self.hour_spin.value()
        minutes = self.minute_spin.value()
        seconds = self.second_spin.value()

        self.total_seconds = hours * 3600 + minutes * 60 + seconds
        self.remaining_seconds = self.total_seconds
        self.update_display()

    # ------------------------------------------------------------------------
    # 뽀모도로
    # ------------------------------------------------------------------------
    def reset_pomodoro_state(self):
        self.pomodoro_mode = "focus"
        self.cycle_count = 1
        self.total_seconds = self.focus_minutes * 60
        self.remaining_seconds = self.total_seconds

    def next_pomodoro_stage(self):
        if self.timer_type != "pomodoro":
            return

        self.timer.stop()
        self.is_running = False

        if self.pomodoro_mode == "focus":
            if self.cycle_count >= self.max_cycle:
                self.pomodoro_mode = "long_break"
                self.total_seconds = self.long_break_minutes * 60
            else:
                self.pomodoro_mode = "short_break"
                self.total_seconds = self.short_break_minutes * 60

        elif self.pomodoro_mode == "short_break":
            self.cycle_count += 1
            self.pomodoro_mode = "focus"
            self.total_seconds = self.focus_minutes * 60

        else:  # long_break
            self.cycle_count = 1
            self.pomodoro_mode = "focus"
            self.total_seconds = self.focus_minutes * 60

        self.remaining_seconds = self.total_seconds
        self.update_display()

    def get_pomodoro_finish_message(self):
        if self.pomodoro_mode == "focus":
            return "집중 시간이 끝났습니다. 휴식하세요!"

        if self.pomodoro_mode == "short_break":
            return "짧은 휴식이 끝났습니다. 다시 집중할 시간입니다!"

        return "긴 휴식이 끝났습니다. 새로운 사이클을 시작하세요!"

    # ------------------------------------------------------------------------
    # 공통 화면 갱신
    # ------------------------------------------------------------------------
    def update_display(self):
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60

        if self.timer_type == "normal":
            self.status_label.setText("⏱ 일반 타이머")
            time_color = "#007aff"
            progress_color = "#34c759"
            self.time_label.setText(
                f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
        else:
            if self.pomodoro_mode == "focus":
                self.status_label.setText("🔥 집중 시간")
                time_color = "#ff3b30"
                progress_color = "#ff3b30"
            elif self.pomodoro_mode == "short_break":
                self.status_label.setText("☕ 짧은 휴식")
                time_color = "#34c759"
                progress_color = "#34c759"
            else:
                self.status_label.setText("🌙 긴 휴식")
                time_color = "#007aff"
                progress_color = "#007aff"

            total_minutes = self.remaining_seconds // 60
            self.time_label.setText(
                f"{total_minutes:02d}:{seconds:02d}"
            )
            self.cycle_label.setText(
                f"{self.cycle_count} / {self.max_cycle} 사이클"
            )

        self.time_label.setStyleSheet(f"""
            QLabel {{
                background:white;
                color:{time_color};
                border-radius:22px;
                padding:22px;
            }}
        """)

        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border:none;
                background:#e5e5ea;
                border-radius:10px;
                height:18px;
            }}

            QProgressBar::chunk {{
                background:{progress_color};
                border-radius:10px;
            }}
        """)

        if self.total_seconds > 0:
            progress_value = int(
                ((self.total_seconds - self.remaining_seconds)
                 / self.total_seconds) * 100
            )
        else:
            progress_value = 0

        self.progress.setValue(progress_value)


# ============================================================================
# ReminderApp 메인 화면에 통합 타이머 버튼 추가.
# ============================================================================
def open_focus_timer(self):
    # 일반 타이머와 뽀모도로가 모두 들어 있는 하나의 창을 연다.
    dialog = TimerDialog(self)
    dialog.exec_()


ReminderApp.open_focus_timer = open_focus_timer


# 기존 init_ui를 보존한 뒤, 입력 카드 아래에 통합 타이머 카드를 추가
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

    timer_label = QLabel("⏱ 집중 타이머 · 🍅 뽀모도로")
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

# 데이터 저장 공간 보장 오버라이딩 패치 (완전 복구형)
original_add_or_update_for_checklist = ReminderApp.add_or_update_todo


def new_add_or_update_for_checklist(self):
    title = self.title_input.text().strip()
    if not title:
        QMessageBox.warning(self, "경고", "할 일을 입력하세요.")
        return

    # 👇 시작/마감 시간 포맷을 표준 문자열로 미리 생성
    start_str = f"{self.start_date_input.date().toString('yyyy-MM-dd')} {self.selected_start_time.toString('HH:mm')}"
    deadline_str = f"{self.date_input.date().toString('yyyy-MM-dd')} {self.selected_time.toString('HH:mm')}"

    # 기본 데이터 구조
    base_data = {
        "title": title,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deadline": deadline_str,
        "start_time": start_str,
        "priority": self.priority_input.currentText(),
        "category": self.category_input.currentText(),
        "status": self.status_input.currentText(),
        "completed": False,
        "memo": "",
        "checklist": []  # 기본값은 빈 리스트로 설정
    }

    if self.editing_todo is not None:
        # ✅ 수정 모드일 때는 기존 체크리스트를 반드시 보존해야 합니다!
        base_data["checklist"] = self.editing_todo.get("checklist", [])

        self.editing_todo.update(base_data)
        self.editing_todo = None
        self.add_btn.setText("추가")
    else:
        # ✅ 신규 추가일 때만 빈 체크리스트 적용
        self.todos.append(base_data)
        
    self.clear_inputs()
    self.refresh_list()
    self.auto_save_data()


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

# 최종적으로 생성자 변경 적용
TodoItemWidget.__init__ = patched_todo_init_with_counter

# ============================================================================
# [추가 코드] 체크리스트 취소선 추가
# ============================================================================

if 'NewChecklistItemRow' in globals():

    original_row_init = NewChecklistItemRow.__init__


    def patched_row_init(self, text, checked, on_delete):
        original_row_init(self, text, checked, on_delete)

        def apply_strikeout(state):
            font = self.checkbox.font()
            font.setStrikeOut(state == 2)
            self.checkbox.setFont(font)

        self.checkbox.stateChanged.connect(apply_strikeout)
        apply_strikeout(2 if checked else 0)


    NewChecklistItemRow.__init__ = patched_row_init

elif 'ChecklistDialog' in globals():

    original_add_item = ChecklistDialog.add_item


    def patched_add_item(self, text="", checked=False):
        original_add_item(self, text, checked)

        # 가장 최근에 추가된 체크박스를 동적으로 찾아 취소선을 실시간 연동합니다.
        if hasattr(self, 'items') and self.items:
            _, checkbox = self.items[-1]

            def apply_strikeout(state):
                font = checkbox.font()
                font.setStrikeOut(state == 2)
                checkbox.setFont(font)

            checkbox.stateChanged.connect(apply_strikeout)
            apply_strikeout(2 if checked else 0)


    ChecklistDialog.add_item = patched_add_item

# ============================================
# 실행
# ============================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ReminderApp()

    window.show()

    sys.exit(app.exec_())