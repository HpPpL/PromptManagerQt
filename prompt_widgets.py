from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, \
    QVBoxLayout, QPushButton, QLayout, QLineEdit, QLabel, QGridLayout, \
    QHBoxLayout, QScrollArea
from PySide6.QtGui import QPixmap
import config as cf
import json


def widget_delete(widget_: QWidget | QLayout) -> None:
    for ch in widget_.children():
        widget_delete(ch)
    widget_.setParent(None)
    widget_.deleteLater()


class MainWindow(QMainWindow):
    def __init__(self, app_: QApplication):
        super().__init__()
        self.app = app_
        self.window_manager = WindowManager(self)
        self.setCentralWidget(self.window_manager)
        self.__window_init()
    
    def __window_init(self) -> None:
        self.setWindowTitle(cf.WINDOW_TITLE)

    def exit(self) -> None:
        self.app.exit()


class WindowManager(QWidget):
    def __init__(self, main_window_):
        super().__init__()
        self.main_window = main_window_
        self.menu_widget = MenuWidget(self)
        self.midjourney_widget = MidjourneyModelWidget(self)
        
        self.active_widget = self.menu_widget
        self._widgets_to_layout()
        self.active_widget.set_active()
    
    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.menu_widget)
        layout.addWidget(self.midjourney_widget)
        
        self.setLayout(layout)

    def __deactive_active_widget(self) -> None:
        self.active_widget.set_active(False)
    
    def __run_widget(self, widget_) -> None:
        self.__deactive_active_widget()
        self.active_widget = widget_
        self.active_widget.set_active()

    def run_midjourney(self) -> None:
        self.__run_widget(self.midjourney_widget)

    def run_menu(self) -> None:
        self.__run_widget(self.menu_widget)
    
    def exit(self) -> None:
        self.main_window.exit()


class WidgetList(QWidget):
    def __init__(self, layout_t_, parent_: QWidget):
        super().__init__(parent_)
        self.setLayout(layout_t_())
        self.widget_list = []
    
    def set_active(self, is_activate_: bool = True) -> None:
        self.setVisible(is_activate_)

    def remove_item(self, index_: int) -> bool: 
        if index_ >= len(self.widget_list):
            return False
        widget_delete(self.widget_list[index_])
        self.widget_list.pop(index_)
        return True
    
    def add_widget(self, widget_: QWidget, *args) -> None:
        self.widget_list.append(widget_)
        self.layout().addWidget(widget_)


class ButtonList(WidgetList):
    def __init__(self, parent_: QWidget):
        super().__init__(QVBoxLayout, parent_)

    def add_button(self,  text_: str, callback_ = None) -> QPushButton:
        button = QPushButton(text_, self)
        button.clicked.connect(callback_)
        self.add_widget(button)
        return button


class ICentralWidget(QWidget):
    def __init__(self, window_manager_):
        super().__init__()
        self.window_manager = window_manager_
        self.set_active(False)
    
    def _widgets_to_layout(self) -> None: ...

    def set_active(self, is_activate_: bool = True) -> None:
        self.setVisible(is_activate_)


class PromptEdit(QLineEdit):
    def __init__(self, parent_: QWidget):
        super().__init__(parent_)
        self.prompt = ""
        self.setText(self.prompt)
        self.textChanged.connect(self.changed_prompt_action)
    
    def add_prompt(self, str_: str) -> None:
        if len(self.prompt) > 0:
            self.setText(self.prompt + " " + str_)
        else:
            self.setText(str_)
    
    def set_prompt(self, new_prompt_: str) -> None:
        self.setText(new_prompt_)

    def remove_prompt(self, str_: str) -> None:
        self.set_prompt(self.prompt.replace(str_, ''))
    
    def changed_prompt_action(self, text_: str) -> None:
        self.prompt = text_
        if self.prompt.count(' ') == len(self.prompt) and len(self.prompt) > 0:
            self.set_prompt('')


class SectionList(WidgetList):
    def __init__(self, parent_: QWidget):
        super().__init__(QGridLayout, parent_)
    
    def add_widget(self, widget_: QWidget, *args) -> None:
        self.widget_list.append(widget_)
        self.layout().addWidget(widget_, *args)


class SectionItem(QWidget):
    def __init__(self, name_: str, prompt_edit_, 
                 img_path_: str = cf.DEFAULT_IMG_PATH, parent_: QWidget = None):
        super().__init__(parent_)
        self.name = name_
        self.prompt_edit = prompt_edit_
        self.label = QLabel(self.name, self)
        self.img = QLabel(self)
        pixmap = QPixmap(img_path_)
        self.img.setPixmap(pixmap)
        self.add_to_prompt_btn = QPushButton("+", self)
        self.add_to_prompt_btn.clicked.connect(self.add_to_prompt_action)

        self.remove_prompt_btn = QPushButton("-", self)
        self.remove_prompt_btn.clicked.connect(self.remove_prompt_action)

        self._widgets_to_layout()
    
    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.img)
        layout.addWidget(self.label)
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(self.remove_prompt_btn)
        tmp_layout.addWidget(self.add_to_prompt_btn)
        layout.addLayout(tmp_layout)
        self.setLayout(layout)

    def add_to_prompt_action(self) -> None:
        self.prompt_edit.add_prompt(self.name)

    def remove_prompt_action(self) -> None:
        self.prompt_edit.remove_prompt(self.name)
        

class SettingsSectionWidget(QWidget):
    def __init__(self, name_: str, prompt_edit_, parent_: QWidget):
        super().__init__(parent_)
        self.prompt_edit = prompt_edit_
        self.button = QPushButton(name_, self)
        self.is_active = True
        self.button.clicked.connect(self.open_section_action)
        self.section_list = SectionList(self)
        self.max_items_in_row = 4
        self.open_section_action()

        self._widgets_to_layout()
    
    def add_widget(self, widget_: QWidget) -> None:
        row = len(self.section_list.widget_list) // self.max_items_in_row
        column = len(self.section_list.widget_list) % self.max_items_in_row + 1
        self.section_list.add_widget(widget_, row, column, 1, 1)

    def add_item(self, name_: str, img_path_: str = cf.DEFAULT_IMG_PATH) -> None:
        self.add_widget(SectionItem(name_, self.prompt_edit, img_path_, self))

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.section_list)
        self.setLayout(layout)

    def open_section_action(self) -> None:
        self.is_active = not self.is_active
        self.section_list.set_active(self.is_active)


class IModelWidget(ICentralWidget):
    def __init__(self, window_manager_):
        super().__init__(window_manager_)
        self.prompt_edit = PromptEdit(self)
        self.back_btn = QPushButton("Назад", self)
        self.back_btn.clicked.connect(self._to_menu)
        self.settings_list = WidgetList(QVBoxLayout, self)

    def _init_settings(self) -> None: ...

    def _to_menu(self) -> None:
        self.window_manager.run_menu()


class SettingsBuilder:
    def __init__(self, filename_: str, model_widget_: IModelWidget):
        self.data_dict = dict()
        self.model = model_widget_
        with open(filename_) as file:
            self.data_dict = json.load(file)

    def __configure_to_section(self, name_: str, data_: list) -> SettingsSectionWidget:
        section = SettingsSectionWidget(name_, self.model.prompt_edit, self.model)
        for item in data_:
            if item['type'] == "section":
                section.add_widget(self.__configure_to_section(item['name'], item['params']))
            elif item['type'] == "parameter":
                section.add_item(item['name'], item['imgPath'])
        return section

    def build(self) -> None:
        for item in self.data_dict['params']:
            if item['type'] == "section":
                self.model.settings_list.add_widget(self.__configure_to_section(item['name'], item['params']))


class MidjourneyModelWidget(IModelWidget):
    def __init__(self, window_manager_):
        super().__init__(window_manager_)
        self._init_settings()
        self._widgets_to_layout()
    
    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(self.prompt_edit)
        tmp_layout.addWidget(self.back_btn)
        layout.addLayout(tmp_layout)
        layout.addWidget(self.settings_list)
        self.setLayout(layout)
        scroll_area = QScrollArea()

    def _init_settings(self) -> None:
        settings_builder = SettingsBuilder("midjourney_settings.json", self)
        settings_builder.build()

        # name_setting = SettingsSectionWidget("name 1", self.prompt_edit, self)
        # ss = SettingsSectionWidget("section 1", self.prompt_edit, self)
        # ss.add_item("prompt name 1")
        # ss.add_item("prompt name 2")
        # ss.add_item("prompt name 3")
        # ss.add_item("prompt name 4")
        # ss.add_item("prompt name 5")
        # name_setting.add_widget(ss)
        # name_setting.add_item("prompt name 2")
        # self.settings_list.add_widget(name_setting)
        # name_setting = SettingsSectionWidget("name 2", self.prompt_edit, self)
        # name_setting.add_item("prompt name 1")
        # name_setting.add_item("prompt name 2")
        # self.settings_list.add_widget(name_setting)


class MenuWidget(ICentralWidget):
    def __init__(self, window_manager_):
        super().__init__(window_manager_)
        self.button_list = ButtonList(self)

        self.button_list.add_button("Midjourney", self.midjourney_action)
        self._widgets_to_layout()
    
    def midjourney_action(self) -> None:
        self.window_manager.run_midjourney()
    
    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.button_list)
        self.setLayout(layout)
