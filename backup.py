import zipfile
import json
import os
import sys
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTextEdit, QApplication, QWidget, QPushButton, QVBoxLayout, QMenuBar, QMenu, QAction, QFileDialog, QLabel

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Backup WEBFISHING')
        self.setMinimumSize(400, 300)

        # Create buttons
        self.pull_button = QPushButton('Download Save')
        self.push_button = QPushButton('Upload Save')

        # Connect buttons to functions
        self.pull_button.clicked.connect(self.pull_function)
        self.push_button.clicked.connect(self.push_function)

        # Create layout and add buttons
        layout = QVBoxLayout()
        layout.addWidget(self.push_button)
        layout.addWidget(self.pull_button)

        # Set up central widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set up menu bar
        self.menu_bar = self.menuBar()
        options_menu = self.menu_bar.addMenu('File')

        # Create actions for menu
        add_target_action = QAction('Select Save File', self)
        add_target_action.triggered.connect(self.set_game)
        options_menu.addAction(add_target_action)

        add_destination_action = QAction('Set Backup Folder', self)
        add_destination_action.triggered.connect(self.set_backup)
        options_menu.addAction(add_destination_action)

        self.target_text_area = QTextEdit()
        self.target_text_area.setReadOnly(True)
        layout.addWidget(self.target_text_area)

        self.load_config()
        self.game_path = self.config['save_folder_location']
        self.backup_path = self.config['backup_path']

    def pull_function(self):
        self.notify("Pulling from Cloud...")

        saveslot = "webfishing_save_slot_0.sav"
        game_path = self.config['save_folder_location']
        backup_path =  os.path.join(self.config['backup_path'],"webfishing_backup.zip")

        if backup_path == None:
            if not self.set_backup():
                self.notify("Pull Canceled.\n")
                return
        try:
            if os.path.getmtime(os.path.join(game_path, saveslot)) >= os.path.getmtime(backup_path):
                self.notify("Warning: Sync conflict. User intervention required.")
                if not self.prompt("Remote files are not newer then Local.\nDo you still want to overwrite local?"):
                    self.notify("Pull Canceled.\n")
                    return
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(game_path)
            self.notify("Pull Successful!")
        except:
            self.notify("Pull Failed.")
        self.notify(" ")

    def push_function(self):
        self.notify("Pushing to Cloud...")

        saveslot = "webfishing_save_slot_0.sav"
        save_path = os.path.join(self.config['save_folder_location'], saveslot)
        backup_path =  os.path.join(self.config['backup_path'],"webfishing_backup.zip")

        if backup_path == None:
            if not self.set_backup():
                self.notify("Push Canceled.\n")
                return
        try:
            if os.path.getmtime(save_path) <= os.path.getmtime(backup_path):
                self.notify("Warning: Sync conflict. User intervention required.")
                if not self.prompt("Local files are not newer then remote.\nDo you still want to overwrite remote?"):
                    self.notify("Push Canceled.\n")
                    return
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(save_path, arcname=saveslot)
            self.notify("Push Successful!")
        except:
            self.notify("Push Failed.")
        self.notify(" ")


    def set_game(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.List)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                game_path = selected_files[0]
                self.config['save_folder_location'] = game_path
                self.notify(f"Selected Game Folder: {game_path}")
                self.save_config()
                return True
        return False

    def set_backup(self):
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setViewMode(QFileDialog.List)
        if folder_dialog.exec_():
            selected_folder = folder_dialog.selectedFiles()
            if selected_folder:
                backup_path = selected_folder[0]
                self.config['backup_path'] = backup_path
                self.notify(f"Selected Backup Destination: {backup_path}")
                self.save_config()
                return True
        return False

    def load_config(self):
        try:
            with open("config.json") as file:
                self.config = json.load(file)
        except:
            self.config = {
                "save_folder_location": "/home/rory/.local/share/Steam/steamapps/compatdata/3146520/pfx/drive_c/users/steamuser/AppData/Roaming/Godot/app_userdata/webfishing_2_newver"
            }
        if 'save_folder_location' not in self.config:
            self.set_game()

    def save_config(self):
        with open("config.json", "w") as file:
            json.dump(self.config, file)

    def notify(self, string):
        print(string)
        self.target_text_area.append(string)

    def prompt(self, promt):
        reply = QMessageBox.question(self, 'Sync Conflict', promt, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

