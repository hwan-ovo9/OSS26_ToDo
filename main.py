# requirement: PyQt5
# pip install PyQt5

import os
import sys
import json

from datetime import datetime

from PyQt5.QtCore import Qt, QDate
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

        self.setMinimumHeight(90)

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

        self.title = QLabel(
            todo_data["title"]
        )

        self.title.setFont(
            QFont("맑은 고딕", 15, QFont.Bold)
        )

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
            "완료": "✅"
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

    # ============================================
    # 완료 체크
    # ============================================

    def toggle_complete(self):

        self.todo_data["completed"] = (
            self.check.isChecked()
        )

        self.update_style()

    # ============================================
    # 스타일
    # ============================================

    def update_style(self):

        if self.check.isChecked():

            self.title.setStyleSheet("""
                color:#9e9ea4;
                text-decoration: line-through;
            """)

        else:

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

        # 자동 저장 파일
        self.auto_save_file = "todo_data.json"

        # 수정 모드용 변수
        self.editing_todo = None

        self.setWindowTitle("Reminder")

        self.resize(980, 760)

        self.setStyleSheet("""
            QWidget {
                background:#f2f2f7;
                font-family:'맑은 고딕';
            }
        """)

        self.init_ui()

        # 자동 불러오기
        self.auto_load_data()

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

    # ============================================
    # 그룹명
    # ============================================

    def get_group_name(self, deadline_str):

        today = datetime.now().date()

        deadline = datetime.strptime(
            deadline_str,
            "%Y-%m-%d"
        ).date()

        diff = (
            deadline - today
        ).days

        if diff < 0:
            return "초과"

        elif diff == 0:
            return "오늘"

        elif diff == 1:
            return "내일"

        elif diff == 2:
            return "모레"

        else:
            return (
                f"{deadline.month}월 "
                f"{deadline.day}일"
            )

    # ============================================
    # 정렬
    # ============================================

    def sort_todos(self):

        self.todos.sort(
            key=lambda x: datetime.strptime(
                x["deadline"],
                "%Y-%m-%d"
            )
        )

    # ============================================
    # 리스트 갱신
    # ============================================

    def refresh_list(self):

        while self.todo_layout.count():

            item = self.todo_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.sort_todos()

        grouped = {}

        for todo in self.todos:

            group_name = self.get_group_name(
                todo["deadline"]
            )

            if group_name not in grouped:
                grouped[group_name] = []

            grouped[group_name].append(todo)

        ordered_groups = []

        for name in [
            "초과",
            "오늘",
            "내일",
            "모레"
        ]:

            if name in grouped:
                ordered_groups.append(name)

        others = [
            x for x in grouped.keys()
            if x not in [
                "초과",
                "오늘",
                "내일",
                "모레"
            ]
        ]

        ordered_groups.extend(others)

        # 그룹 UI
        for group_name in ordered_groups:

            section = QLabel(group_name)

            section.setFont(
                QFont(
                    "맑은 고딕",
                    24,
                    QFont.Bold
                )
            )

            if group_name == "초과":

                section.setStyleSheet("""
                    color:#ff3b30;
                    margin-top:12px;
                """)

            else:

                section.setStyleSheet("""
                    color:black;
                    margin-top:12px;
                """)

            self.todo_layout.addWidget(
                section
            )

            for todo in grouped[group_name]:

                widget = TodoItemWidget(
                    todo,
                    self.delete_todo,
                    self.edit_todo
                )

                self.todo_layout.addWidget(
                    widget
                )

        self.todo_layout.addStretch()

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

            "deadline":
                self.date_input.date()
                .toString("yyyy-MM-dd"),

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
            "%Y-%m-%d"
        )

        self.date_input.setDate(
            QDate(
                date.year,
                date.month,
                date.day
            )
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
# 실행
# ============================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ReminderApp()

    window.show()

    sys.exit(app.exec_())