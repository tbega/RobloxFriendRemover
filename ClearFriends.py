import sys
import subprocess

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                QTextEdit, QMessageBox, QFrame, QTabWidget,
                                QSpinBox, QCheckBox, QPlainTextEdit, QDoubleSpinBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMutex
    from PyQt6.QtGui import QFont, QPixmap
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                QTextEdit, QMessageBox, QFrame, QTabWidget,
                                QSpinBox, QCheckBox, QPlainTextEdit, QDoubleSpinBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMutex
    from PyQt6.QtGui import QFont, QPixmap

import time

HEADERS = {}
CSRF_TOKEN = None

class UnfriendWorker(QThread):
    progress_update = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, cookie, excluded_users, skip_friends, exclude_followers):
        super().__init__()
        self.cookie = cookie
        self.excluded_users = excluded_users
        self.skip_friends = skip_friends
        self.exclude_followers = exclude_followers
        self.delay = 0.1
        self.mutex = QMutex()
        self.running = True
    
    def update_delay(self, new_delay):
        self.mutex.lock()
        self.delay = new_delay
        self.mutex.unlock()
    
    def stop(self):
        self.running = False
    
    def run(self):
        try:
            if self.skip_friends:
                self.progress_update.emit("Skipping friends removal as requested.\n")
                self.finished.emit()
                return
                
            global HEADERS
            HEADERS = {
                "Cookie": f".ROBLOSECURITY={self.cookie}",
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.roblox.com/"
            }
            get_csrf_token()
            my_id = get_user_id()
            friends = get_friends(my_id)
            
            followers_set = set()
            if self.exclude_followers:
                followers = get_followers(my_id)
                followers_set = {str(f["id"]) for f in followers}
                self.progress_update.emit(f"Found {len(followers)} followers to exclude.\n")
            
            filtered_friends = []
            for f in friends:
                user_id = str(f["id"])
                if user_id not in self.excluded_users and (not self.exclude_followers or user_id not in followers_set):
                    filtered_friends.append(f)
            
            excluded_count = len(friends) - len(filtered_friends)
            follower_excluded = len([f for f in friends if str(f["id"]) in followers_set]) if self.exclude_followers else 0
            
            self.progress_update.emit(f"Found {len(friends)} friends, excluding {excluded_count} users")
            if self.exclude_followers:
                self.progress_update.emit(f" ({follower_excluded} followers excluded)")
            self.progress_update.emit(".\n")
            
            for friend in filtered_friends:
                if not self.running:
                    break
                    
                unfriend(friend["id"])
                self.progress_update.emit(f"Unfriended user {friend['id']}\n")
                
                self.mutex.lock()
                current_delay = self.delay
                self.mutex.unlock()
                
                time.sleep(current_delay)
            
            self.progress_update.emit("Done!\n")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class UnfollowWorker(QThread):
    progress_update = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, cookie, excluded_users, skip_followers, exclude_friends):
        super().__init__()
        self.cookie = cookie
        self.excluded_users = excluded_users
        self.skip_followers = skip_followers
        self.exclude_friends = exclude_friends
        self.delay = 0.1
        self.mutex = QMutex()
        self.running = True
    
    def update_delay(self, new_delay):
        self.mutex.lock()
        self.delay = new_delay
        self.mutex.unlock()
    
    def stop(self):
        self.running = False
    
    def run(self):
        try:
            if self.skip_followers:
                self.progress_update.emit("Skipping followers removal as requested.\n")
                self.finished.emit()
                return
                
            global HEADERS
            HEADERS = {
                "Cookie": f".ROBLOSECURITY={self.cookie}",
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.roblox.com/"
            }
            get_csrf_token()
            my_id = get_user_id()
            followers = get_followers(my_id)
            
            friends_set = set()
            if self.exclude_friends:
                friends = get_friends(my_id)
                friends_set = {str(f["id"]) for f in friends}
                self.progress_update.emit(f"Found {len(friends)} friends to exclude.\n")
            
            filtered_followers = []
            for f in followers:
                user_id = str(f["id"])
                if user_id not in self.excluded_users and (not self.exclude_friends or user_id not in friends_set):
                    filtered_followers.append(f)
            
            excluded_count = len(followers) - len(filtered_followers)
            friend_excluded = len([f for f in followers if str(f["id"]) in friends_set]) if self.exclude_friends else 0
            
            self.progress_update.emit(f"Found {len(followers)} followers, excluding {excluded_count} users")
            if self.exclude_friends:
                self.progress_update.emit(f" ({friend_excluded} friends excluded)")
            self.progress_update.emit(".\n")
            
            for follower in filtered_followers:
                if not self.running:
                    break
                    
                block_user(follower["id"])
                self.progress_update.emit(f"Blocked follower {follower['id']}\n")
                time.sleep(0.5) 
                
                unblock_user(follower["id"])
                self.progress_update.emit(f"Unblocked follower {follower['id']}\n")
                
                self.mutex.lock()
                current_delay = self.delay
                self.mutex.unlock()
                
                time.sleep(current_delay)
            
            self.progress_update.emit("Done!\n")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

def get_csrf_token():
    global CSRF_TOKEN
    resp = requests.post("https://friends.roblox.com/v1/users/1/unfriend", headers=HEADERS)
    token = resp.headers.get("x-csrf-token")
    if token:
        CSRF_TOKEN = token
        HEADERS["X-CSRF-TOKEN"] = CSRF_TOKEN

def get_user_id():
    resp = requests.get("https://users.roblox.com/v1/users/authenticated", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def get_friends(user_id):
    friends = []
    cursor = ""
    while True:
        url = f"https://friends.roblox.com/v1/users/{user_id}/friends"
        if cursor:
            url += f"?cursor={cursor}"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        friends.extend(data["data"])
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return friends

def unfriend(user_id):
    url = f"https://friends.roblox.com/v1/users/{user_id}/unfriend"
    resp = requests.post(url, headers=HEADERS)
    if resp.status_code == 403 and "x-csrf-token" in resp.headers:
        HEADERS["X-CSRF-TOKEN"] = resp.headers["x-csrf-token"]
        resp = requests.post(url, headers=HEADERS)

def get_followers(user_id):
    followers = []
    cursor = ""
    while True:
        url = f"https://friends.roblox.com/v1/users/{user_id}/followers"
        if cursor:
            url += f"?cursor={cursor}"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        followers.extend(data["data"])
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return followers

def block_user(user_id):
    url = f"https://accountsettings.roblox.com/v1/users/{user_id}/block"
    resp = requests.post(url, headers=HEADERS)
    if resp.status_code == 403 and "x-csrf-token" in resp.headers:
        HEADERS["X-CSRF-TOKEN"] = resp.headers["x-csrf-token"]
        resp = requests.post(url, headers=HEADERS)

def unblock_user(user_id):
    url = f"https://accountsettings.roblox.com/v1/users/{user_id}/unblock"
    resp = requests.post(url, headers=HEADERS)
    if resp.status_code == 403 and "x-csrf-token" in resp.headers:
        HEADERS["X-CSRF-TOKEN"] = resp.headers["x-csrf-token"]
        resp = requests.post(url, headers=HEADERS)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(700, 650)  
        central_widget = QWidget()
        self.setCentralWidget(central_widget)      
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)     
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.close)
        close_btn.setFixedSize(30, 30)      
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        rate_layout = QHBoxLayout()
        rate_label = QLabel("Delay between actions (seconds):")
        rate_label.setFont(QFont("Segoe UI", 10))
        self.rate_spinbox = QDoubleSpinBox()
        self.rate_spinbox.setRange(0.1, 10.0)
        self.rate_spinbox.setSingleStep(0.1)
        self.rate_spinbox.setDecimals(1)
        self.rate_spinbox.setValue(0.1)
        self.rate_spinbox.setObjectName("rateSpinbox")
        self.rate_spinbox.valueChanged.connect(self.update_rate)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(self.rate_spinbox)
        rate_layout.addStretch()
        layout.addLayout(rate_layout)
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tabWidget")   
        friends_tab = self.create_friends_tab()
        self.tab_widget.addTab(friends_tab, "Remove Friends")
        followers_tab = self.create_followers_tab()
        self.tab_widget.addTab(followers_tab, "Remove Followers")
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
    
    def create_friends_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        cookie_label = QLabel(".ROBLOSECURITY cookie:")
        cookie_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(cookie_label)
        self.friends_cookie_entry = QLineEdit()
        self.friends_cookie_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.friends_cookie_entry.setPlaceholderText("Paste your cookie here...")
        self.friends_cookie_entry.setFont(QFont("Segoe UI", 11))
        self.friends_cookie_entry.setObjectName("cookieEntry")
        layout.addWidget(self.friends_cookie_entry)
        self.skip_friends_checkbox = QCheckBox("Skip removing friends")
        self.skip_friends_checkbox.setFont(QFont("Segoe UI", 10))
        self.skip_friends_checkbox.setObjectName("checkbox")
        layout.addWidget(self.skip_friends_checkbox)        
        self.exclude_followers_checkbox = QCheckBox("Don't remove followers from friends list")
        self.exclude_followers_checkbox.setFont(QFont("Segoe UI", 10))
        self.exclude_followers_checkbox.setObjectName("checkbox")
        layout.addWidget(self.exclude_followers_checkbox)     
        excluded_label = QLabel("Excluded User IDs (one per line):")
        excluded_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(excluded_label)       
        self.friends_excluded_text = QPlainTextEdit()
        self.friends_excluded_text.setPlaceholderText("123456789\n987654321\n...")
        self.friends_excluded_text.setFont(QFont("Consolas", 9))
        self.friends_excluded_text.setObjectName("excludedText")
        self.friends_excluded_text.setMaximumHeight(80)
        layout.addWidget(self.friends_excluded_text)        
        self.friends_start_button = QPushButton("Remove All Friends")
        self.friends_start_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.friends_start_button.setObjectName("startButton")
        self.friends_start_button.clicked.connect(self.on_start_friends)
        layout.addWidget(self.friends_start_button)
        self.friends_stop_button = QPushButton("Stop")
        self.friends_stop_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.friends_stop_button.setObjectName("stopButton")
        self.friends_stop_button.clicked.connect(self.on_stop_friends)
        self.friends_stop_button.setEnabled(False)
        layout.addWidget(self.friends_stop_button)
        self.friends_result_text = QTextEdit()
        self.friends_result_text.setFont(QFont("Consolas", 10))
        self.friends_result_text.setReadOnly(True)
        self.friends_result_text.setObjectName("resultText")
        layout.addWidget(self.friends_result_text)  
        widget.setLayout(layout)
        return widget
    
    def create_followers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        cookie_label = QLabel(".ROBLOSECURITY cookie:")
        cookie_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(cookie_label)        
        self.followers_cookie_entry = QLineEdit()
        self.followers_cookie_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.followers_cookie_entry.setPlaceholderText("Paste your cookie here...")
        self.followers_cookie_entry.setFont(QFont("Segoe UI", 11))
        self.followers_cookie_entry.setObjectName("cookieEntry")
        layout.addWidget(self.followers_cookie_entry)      
        self.skip_followers_checkbox = QCheckBox("Skip removing followers")
        self.skip_followers_checkbox.setFont(QFont("Segoe UI", 10))
        self.skip_followers_checkbox.setObjectName("checkbox")
        layout.addWidget(self.skip_followers_checkbox)
        self.exclude_friends_checkbox = QCheckBox("Don't remove friends from followers list")
        self.exclude_friends_checkbox.setFont(QFont("Segoe UI", 10))
        self.exclude_friends_checkbox.setObjectName("checkbox")
        layout.addWidget(self.exclude_friends_checkbox)
        excluded_label = QLabel("Excluded User IDs (one per line):")
        excluded_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(excluded_label)      
        self.followers_excluded_text = QPlainTextEdit()
        self.followers_excluded_text.setPlaceholderText("123456789\n987654321\n...")
        self.followers_excluded_text.setFont(QFont("Consolas", 9))
        self.followers_excluded_text.setObjectName("excludedText")
        self.followers_excluded_text.setMaximumHeight(80)
        layout.addWidget(self.followers_excluded_text)
        self.followers_start_button = QPushButton("Remove All Followers")
        self.followers_start_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.followers_start_button.setObjectName("startButton")
        self.followers_start_button.clicked.connect(self.on_start_followers)
        layout.addWidget(self.followers_start_button)
        self.followers_stop_button = QPushButton("Stop")
        self.followers_stop_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.followers_stop_button.setObjectName("stopButton")
        self.followers_stop_button.clicked.connect(self.on_stop_followers)
        self.followers_stop_button.setEnabled(False)
        layout.addWidget(self.followers_stop_button)
        self.followers_result_text = QTextEdit()
        self.followers_result_text.setFont(QFont("Consolas", 10))
        self.followers_result_text.setReadOnly(True)
        self.followers_result_text.setObjectName("resultText")
        layout.addWidget(self.followers_result_text)     
        widget.setLayout(layout)
        return widget
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                border: 2px solid #3a3a3a;
            }
            
            #closeButton {
                background-color: #ff4757;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 12pt;
                font-weight: bold;
            }
            
            #closeButton:hover {
                background-color: #ff3838;
            }
            
            #rateSpinbox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px;
                font-size: 11pt;
                min-width: 60px;
            }
            
            #rateSpinbox:focus {
                border-color: #00b894;
            }
            
            #checkbox {
                color: #ffffff;
                font-size: 11pt;
            }
            
            #checkbox::indicator {
                width: 18px;
                height: 18px;
            }
            
            #checkbox::indicator:unchecked {
                background-color: #2d2d2d;
                border: 2px solid #3a3a3a;
                border-radius: 4px;
            }
            
            #checkbox::indicator:checked {
                background-color: #00b894;
                border: 2px solid #00b894;
                border-radius: 4px;
            }
            
            #excludedText {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
            
            #excludedText:focus {
                border-color: #00b894;
            }
            
            #stopButton {
                background-color: #ff4757;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 12pt;
                min-height: 20px;
            }
            
            #stopButton:hover {
                background-color: #ff3838;
            }
            
            #stopButton:disabled {
                background-color: #3a3a3a;
                color: #636e72;
            }
            
            #tabWidget {
                background-color: #1e1e1e;
            }
            
            #tabWidget::pane {
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                background-color: #2d2d2d;
            }
            
            #tabWidget::tab-bar {
                alignment: center;
            }
            
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #ffffff;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 6px;
                font-size: 11pt;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: #00b894;
            }
            
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            
            #cookieEntry {
                padding: 12px;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 11pt;
            }
            
            #cookieEntry:focus {
                border-color: #00b894;
                outline: none;
            }
            
            #startButton {
                background-color: #00b894;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 12pt;
                min-height: 20px;
            }
            
            #startButton:hover {
                background-color: #00a085;
            }
            
            #startButton:pressed {
                background-color: #008f7a;
            }
            
            #startButton:disabled {
                background-color: #3a3a3a;
                color: #636e72;
            }
            
            #resultText {
                background-color: #1a1a1a;
                color: #00ff41;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
            
            QLabel {
                color: #ffffff;
            }
        """)
    
    def update_rate(self):
        if self.worker and hasattr(self.worker, 'update_delay'):
            self.worker.update_delay(self.rate_spinbox.value())
    
    def get_excluded_users(self, text_widget):
        excluded_text = text_widget.toPlainText().strip()
        if not excluded_text:
            return set()
        return set(line.strip() for line in excluded_text.split('\n') if line.strip())
    
    def on_start_friends(self):
        cookie = self.friends_cookie_entry.text().strip()
        if not cookie:
            QMessageBox.warning(self, "Input Required", 
                               "Please enter your .ROBLOSECURITY cookie.")
            return
        
        excluded_users = self.get_excluded_users(self.friends_excluded_text)
        skip_friends = self.skip_friends_checkbox.isChecked()
        exclude_followers = self.exclude_followers_checkbox.isChecked()
        
        self.friends_start_button.setEnabled(False)
        self.friends_stop_button.setEnabled(True)
        self.friends_start_button.setText("Removing Friends...")
        self.friends_result_text.clear()        
        self.worker = UnfriendWorker(cookie, excluded_users, skip_friends, exclude_followers)
        self.worker.update_delay(self.rate_spinbox.value())
        self.worker.progress_update.connect(self.update_friends_progress)
        self.worker.finished.connect(self.on_friends_finished)
        self.worker.error.connect(self.on_friends_error)
        self.worker.start()
    
    def on_start_followers(self):
        cookie = self.followers_cookie_entry.text().strip()
        if not cookie:
            QMessageBox.warning(self, "Input Required", 
                               "Please enter your .ROBLOSECURITY cookie.")
            return
        
        excluded_users = self.get_excluded_users(self.followers_excluded_text)
        skip_followers = self.skip_followers_checkbox.isChecked()
        exclude_friends = self.exclude_friends_checkbox.isChecked()      
        self.followers_start_button.setEnabled(False)
        self.followers_stop_button.setEnabled(True)
        self.followers_start_button.setText("Removing Followers...")
        self.followers_result_text.clear()    
        self.worker = UnfollowWorker(cookie, excluded_users, skip_followers, exclude_friends)
        self.worker.update_delay(self.rate_spinbox.value())
        self.worker.progress_update.connect(self.update_followers_progress)
        self.worker.finished.connect(self.on_followers_finished)
        self.worker.error.connect(self.on_followers_error)
        self.worker.start()
    
    def on_stop_friends(self):
        if self.worker:
            self.worker.stop()
            self.friends_start_button.setEnabled(True)
            self.friends_stop_button.setEnabled(False)
            self.friends_start_button.setText("Remove All Friends")
    
    def on_stop_followers(self):
        if self.worker:
            self.worker.stop()
            self.followers_start_button.setEnabled(True)
            self.followers_stop_button.setEnabled(False)
            self.followers_start_button.setText("Remove All Followers")
    
    def update_friends_progress(self, message):
        self.friends_result_text.append(message.rstrip())
        self.friends_result_text.ensureCursorVisible()
    
    def update_followers_progress(self, message):
        self.followers_result_text.append(message.rstrip())
        self.followers_result_text.ensureCursorVisible()
    
    def on_friends_finished(self):
        self.friends_start_button.setEnabled(True)
        self.friends_stop_button.setEnabled(False)
        self.friends_start_button.setText("Remove All Friends")
        QMessageBox.information(self, "Complete", "Friends removal process completed!")
    
    def on_followers_finished(self):
        self.followers_start_button.setEnabled(True)
        self.followers_stop_button.setEnabled(False)
        self.followers_start_button.setText("Remove All Followers")
        QMessageBox.information(self, "Complete", "Followers removal process completed!")
    
    def on_friends_error(self, error_message):
        self.friends_start_button.setEnabled(True)
        self.friends_stop_button.setEnabled(False)
        self.friends_start_button.setText("Remove All Friends")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
    
    def on_followers_error(self, error_message):
        self.followers_start_button.setEnabled(True)
        self.followers_stop_button.setEnabled(False)
        self.followers_start_button.setText("Remove All Followers")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
