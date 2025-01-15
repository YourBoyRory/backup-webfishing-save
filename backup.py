import zipfile
import json
import os
import sys
from datetime import datetime, timezone
from time import strftime, localtime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from PyQt5.QtWidgets import QMainWindow, QComboBox, QMessageBox, QTextEdit, QApplication, QWidget, QPushButton, QVBoxLayout, QMenuBar, QMenu, QAction, QFileDialog, QLabel

def ResourcePath(folder, file):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, folder, file)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Backup WEBFISHING')
        self.setMinimumSize(400, 300)

        # Create buttons
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(['slot_0', 'slot_1', 'slot_2', 'slot_3'])
        self.combo_box.currentIndexChanged.connect(self.save_config)
        self.pull_button = QPushButton('Download Save')
        self.push_button = QPushButton('Upload Save')

        # Connect buttons to functions
        self.pull_button.clicked.connect(self.pull_function)
        self.push_button.clicked.connect(self.push_function)

        # Create layout and add buttons
        layout = QVBoxLayout()
        layout.addWidget(self.combo_box)
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
        

    def set_UI_Lock(self, boolean):
        self.combo_box.setEnabled(boolean)
        self.pull_button.setEnabled(boolean)
        self.push_button.setEnabled(boolean)

    def pull_function(self):
        self.set_UI_Lock(False)
        self.notify("(Pull) Downloading from Cloud...")
        self.repaint()

        saveslot = self.combo_box.currentText()
        game_path = self.config['save_folder_location']
        save_path = os.path.join(game_path, f"webfishing_save_{saveslot}.sav")
        backup_path =  ResourcePath("download_cache", f"webfishing_backup_{saveslot}.zip")

        try:
            file_list = self.drive.ListFile({'q': f"title = 'webfishing_backup_{saveslot}.zip'"}).GetList()
            if file_list:
                backup_dt = datetime.strptime(file_list[0]['modifiedDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).astimezone(tz=None).timestamp()
                save_dt = os.path.getmtime(save_path)
                #print(datetime.fromtimestamp(backup_dt).strftime('%c'))
                if save_dt >= backup_dt:
                    self.notify("Warning: Sync conflict. User intervention required.")
                    if not self.prompt("Remote files are not newer then Local.\nDo you still want to overwrite local?"):
                        self.notify("Pull Canceled.\n")
                        self.set_UI_Lock(True)
                        return
            file_list = self.drive.ListFile({'q': f"title = 'webfishing_backup_{saveslot}.zip'"}).GetList()
            file_list[0].GetContentFile(backup_path)
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(game_path)
            self.notify("Pull Successful!")
        except Exception as e:
            self.notify("Pull Failed.", e)
        self.notify(" ")
        self.set_UI_Lock(True)

    def push_function(self):
        self.set_UI_Lock(False)
        self.notify("(Push) Uploading to Cloud...")
        self.repaint()

        saveslot = self.combo_box.currentText()
        save_path = os.path.join(self.config['save_folder_location'], f"webfishing_save_{saveslot}.sav")
        backup_path =  ResourcePath("download_cache",f"webfishing_backup_{saveslot}.zip")

        try:
            file_list = self.drive.ListFile({'q': f"title = 'webfishing_backup_{saveslot}.zip'"}).GetList()
            if file_list:
                backup_dt = datetime.strptime(file_list[0]['modifiedDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).astimezone(tz=None).timestamp()
                save_dt = os.path.getmtime(save_path)
                if save_dt <= backup_dt:
                    self.notify("Warning: Sync conflict. User intervention required.")
                    if not self.prompt("Local files are not newer then remote.\nDo you still want to overwrite remote?"):
                        self.notify("Push Canceled.\n")
                        self.set_UI_Lock(True)
                        return
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(save_path, arcname=saveslot)
            self.notify("Push Successful!")
            if file_list:
                file_list[0].Delete()

            file2 = self.drive.CreateFile({'title': f'webfishing_backup_{saveslot}.zip'})
            file2.SetContentFile(backup_path)
            file2.Upload()
        
        except Exception as e:
            self.notify("Push Failed.", e)
        self.notify(" ")
        self.set_UI_Lock(True)


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
                "last_slot": "slot_0",
                "save_folder_location": "/home/rory/.local/share/Steam/steamapps/compatdata/3146520/pfx/drive_c/users/steamuser/AppData/Roaming/Godot/app_userdata/webfishing_2_newver"
            }
        if 'last_slot' in self.config:
            self.combo_box.setCurrentText(self.config['last_slot'])
        if 'save_folder_location' not in self.config:
            self.set_game()
            return
        if not os.path.exists(self.config['save_folder_location']):
            self.set_game()
            return

    def save_config(self):
        self.config["last_slot"] = self.combo_box.currentText()
        with open("config.json", "w") as file:
            json.dump(self.config, file)

    def notify(self, string, e=""):
        print(string, e)
        self.target_text_area.append(string)

    def prompt(self, promt):
        reply = QMessageBox.question(self, 'Sync Conflict', promt, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        return False

    def init_google(self):
        try:
            gauth = GoogleAuth(ResourcePath("etc","settings.yaml"))
            gauth.LocalWebserverAuth()
            self.drive = GoogleDrive(gauth)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Failed to authenticate the Google API\n{e}")
            msg.setInformativeText('Make sure you have placed your client_secrets.json in the _internal folder.')
            msg.setWindowTitle("Error")
            msg.exec_()
            exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    window.init_google()
    sys.exit(app.exec_())

