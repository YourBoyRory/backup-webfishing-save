import zipfile
import json
import os
import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QApplication, QWidget, QPushButton, QVBoxLayout, QMenuBar, QMenu, QAction, QFileDialog, QLabel

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = {
            "pull_timestamp": None
            "save_folder_location": "/home/rory/.local/share/Steam/steamapps/compatdata/3146520/pfx/drive_c/users/steamuser/AppData/Roaming/Godot/app_userdata/webfishing_2_newver",
            "backup_path": "./backup_folder"
        }
        self.game_path = self.config['save_folder_location']
        self.backup_path = self.config['backup_path']

        self.setWindowTitle('Backup WEBFISHING')
        self.setMinimumSize(400, 300)
        
        # Create buttons
        self.pull_button = QPushButton('Pull Save')
        self.push_button = QPushButton('Push Save')

        # Connect buttons to functions
        self.pull_button.clicked.connect(self.pull_function)
        self.push_button.clicked.connect(self.push_function)

        # Create layout and add buttons
        layout = QVBoxLayout()
        layout.addWidget(self.pull_button)
        layout.addWidget(self.push_button)

        # Set up central widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set up menu bar
        self.menu_bar = self.menuBar()
        options_menu = self.menu_bar.addMenu('File')

        # Create actions for menu
        add_target_action = QAction('Set WEBFISHING Folder', self)
        add_target_action.triggered.connect(self.set_game)
        options_menu.addAction(add_target_action)

        add_destination_action = QAction('Set Backup Folder', self)
        add_destination_action.triggered.connect(self.set_backup)
        options_menu.addAction(add_destination_action)

        self.target_text_area = QTextEdit()
        self.target_text_area.setReadOnly(True)
        layout.addWidget(self.target_text_area)
        
        if self.game_path == None or self.backup_path == None:
            self.target_text_area.setText("Paths not set, Select [File] > [Set...]\n")

    def pull_function(self):
        with zipfile.ZipFile(f"{self.backup_path}/webfishing_backup.zip", 'r') as zipf:
            zipf.extractall(self.game_path)
        print(f"Pull From: {self.backup_path} \nTo: {self.game_path}")
        self.target_text_area.append(f"Pull From: {self.backup_path} \nTo: {self.game_path}\n")

    def push_function(self):
        with zipfile.ZipFile(f"{self.backup_path}/webfishing_backup.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(f"{self.game_path}/webfishing_migrated_data.save", arcname="webfishing_migrated_data.save")   
        print(f"Push To: {self.backup_path} \nFrom: {self.game_path}")
        self.target_text_area.append(f"Push To: {self.backup_path} \nFrom: {self.game_path}\n")

    def set_game(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.List)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.game_path = selected_files[0]
                print(f"Selected Game Folder: {self.game_path}")
                self.target_text_area.append(f"Selected Game Folder: {self.game_path}\n")

    def set_backup(self):
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setViewMode(QFileDialog.List)
        if folder_dialog.exec_():
            selected_folder = folder_dialog.selectedFiles()
            if selected_folder:
                self.backup_path = selected_folder[0]
                print(f"Selected Backup Destination: {self.backup_path}")
                self.target_text_area.append(f"Selected Backup Destination: {self.backup_path}\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

