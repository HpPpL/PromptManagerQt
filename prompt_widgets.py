import pyperclip
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, \
    QVBoxLayout, QPushButton, QLayout, QLineEdit, QLabel, QGridLayout, \
    QHBoxLayout, QScrollArea, QSizePolicy, QCheckBox, QSlider
from PySide6.QtGui import QPixmap, QIntValidator
from PySide6.QtCore import Qt
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
        self.setStyleSheet(cf.DEFAULT_APP_STYLE_SHEET)
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
        self.dream_studio_widget = DreamStudioModelWidget(self)
        self.stable_diffusion_widget = StableDiffusionModelWidget(self)
        
        self.active_widget = self.menu_widget
        self._widgets_to_layout()
        self.active_widget.set_active()
    
    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.menu_widget)
        layout.addWidget(self.midjourney_widget)
        layout.addWidget(self.dream_studio_widget)
        layout.addWidget(self.stable_diffusion_widget)
        
        self.setLayout(layout)

    def __deactivate_widget(self) -> None:
        self.active_widget.set_active(False)
    
    def __run_widget(self, widget_) -> None:
        self.__deactivate_widget()
        self.active_widget = widget_
        self.active_widget.set_active()

    def run_midjourney(self) -> None:
        self.__run_widget(self.midjourney_widget)

    def run_dream_studio(self) -> None:
        self.__run_widget(self.dream_studio_widget)

    def run_stable_diffusion(self) -> None:
        self.__run_widget(self.stable_diffusion_widget)

    def run_menu(self) -> None:
        self.__run_widget(self.menu_widget)
    
    def exit(self) -> None:
        self.main_window.exit()


class WidgetList(QWidget):
    def __init__(self, layout_t_, parent_: QWidget = None):
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

    def add_button(self,  text_: str, callback_=None, **kwargs) -> QPushButton:
        button = QPushButton(text_, self)
        button.setStyleSheet(cf.DEFAULT_BUTTON_STYLE_SHEET)
        button.clicked.connect(callback_)
        button.setFixedHeight(40)
        button.setMaximumWidth(400)
        if 'fsize' in kwargs:
            button.setFixedSize(kwargs['fsize'])
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
        i = self.prompt.find(str_)
        while i != -1:
            if i != 0 and self.prompt[i - 1] != ' ':
                i = self.prompt[i + len(str_):].find(str_)
                continue
            j = i + len(str_)
            if j >= len(self.prompt):
                self.set_prompt(self.prompt[:i])
                return
            while j < len(self.prompt) and (self.prompt[j].isdigit() or self.prompt[j] == ':'):
                j += 1
            self.prompt = self.prompt[:i] + self.prompt[j:]
            i = self.prompt.find(str_)
        self.set_prompt(self.prompt)
        # self.set_prompt(self.prompt.replace(str_, ''))
    
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
    def __init__(self, name_: str, prompt_edit_, img_path_: str = cf.DEFAULT_IMG_PATH, hint_: str = cf.DEFAULT_HINT, parent_: QWidget = None):
        super().__init__(parent_)
        self.name = name_
        self.weight = 1
        self.prompt_edit = prompt_edit_
        self.hint = hint_
        self.setToolTip(self.hint)
        self.setStyleSheet('QToolTip {color: black;}')
        self.label = QLabel(self.name, self)
        self.img = QLabel(self)
        pixmap = QPixmap(img_path_)
        self.img.setPixmap(pixmap.scaled(cf.DEFAULT_MAXIMUM_IMG_SIZE * 0.9, Qt.KeepAspectRatio))

        self.remove_prompt_btn = QPushButton("X", self)
        self.add_to_prompt_btn = QPushButton("Add", self)
        self.__init_buttons()

        self.weight_editor = QLineEdit(self)
        self.weight_editor.setValidator(QIntValidator())
        self.weight_editor.setText(str(self.weight))
        self.weight_editor.textChanged.connect(self.weight_edit_action)

        self.setFixedSize(cf.DEFAULT_MAXIMUM_IMG_SIZE)
        self._widgets_to_layout()

    def __init_buttons(self) -> None:
        self.remove_prompt_btn.clicked.connect(self.remove_prompt_action)
        self.remove_prompt_btn.setVisible(False)
        self.remove_prompt_btn.setStyleSheet(cf.DEFAULT_BUTTON_STYLE_SHEET)

        self.add_to_prompt_btn.setStyleSheet(cf.DEFAULT_BUTTON_STYLE_SHEET)
        self.add_to_prompt_btn.clicked.connect(self.add_to_prompt_action)
    
    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.img)
        layout.addWidget(self.label)
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(self.weight_editor)
        tmp_layout.addWidget(self.remove_prompt_btn)
        tmp_layout.addWidget(self.add_to_prompt_btn)
        layout.addLayout(tmp_layout)
        self.setLayout(layout)

    def mousePressEvent(self, event_) -> None:
        self.add_to_prompt_action()

    def remove_prompt_action(self) -> None:
        self.add_to_prompt_btn.setVisible(True)
        self.remove_prompt_btn.setVisible(False)
        self.prompt_edit.remove_prompt(self.name)

    def weight_edit_action(self, text_: str) -> None:
        self.weight = 0 if len(text_) < 1 else int(text_)
        if self.weight < 0:
            self.weight = 0

    def add_to_prompt_action(self) -> None:
        self.add_to_prompt_btn.setVisible(False)
        self.remove_prompt_btn.setVisible(True)
        prompt = self.name
        if self.weight != 1:
            prompt = prompt + '::' + str(self.weight)
        self.prompt_edit.add_prompt(prompt)


class SettingsSectionWidget(QWidget):
    def __init__(self, name_: str, prompt_edit_, parent_: QWidget = None):
        super().__init__(parent_)
        self.prompt_edit = prompt_edit_
        self.is_active = True
        self.button = QPushButton(name_, self)
        self.button.setFixedHeight(40)
        self.button.setMaximumWidth(300)
        self.button.setStyleSheet(cf.DEFAULT_BUTTON_STYLE_SHEET)
        self.button.clicked.connect(self.open_section_action)
        self.section_list = SectionList(self)
        self.max_items_in_row = 5
        self.max_sections_in_row = 1

        self.open_section_action()
        self._widgets_to_layout()

    def __get_minimum_height(self) -> int:
        max_height = 0
        for widget in self.section_list.widget_list:
            max_height = max(max_height, widget.size().height())
        print(self.button.text(), max_height)
        return max_height
    
    def add_widget(self, widget_: QWidget) -> None:
        row = len(self.section_list.widget_list) // self.max_sections_in_row
        column = len(self.section_list.widget_list) % self.max_sections_in_row + 1
        self.section_list.add_widget(widget_, row, column, 1, 1)

    def add_item(self, name_: str, img_path_: str = cf.DEFAULT_IMG_PATH, hint_: str = cf.DEFAULT_HINT) -> None:
        row = len(self.section_list.widget_list) // self.max_items_in_row
        column = len(self.section_list.widget_list) % self.max_items_in_row + 1
        self.section_list.add_widget(SectionItem(name_, self.prompt_edit, img_path_, hint_, self), row, column, 1, 1)

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.section_list)
        self.setLayout(layout)

    def open_section_action(self) -> None:
        self.is_active = not self.is_active
        self.section_list.set_active(self.is_active)


class BaseImage(QWidget):
    def __init__(self, name_: str, img_path_: str, base_image_selector_):
        super().__init__(base_image_selector_)
        self.base_image_selector = base_image_selector_
        self.label = QLabel(name_, self)
        self.label.setStyleSheet("font-size: 25px; font-weight: bold;")
        self.img = QLabel(self)
        pixmap = QPixmap(img_path_)
        self.img.setPixmap(pixmap)
        self.set_active(False)
        self._widgets_to_layout()

    def mousePressEvent(self, event_) -> None:
        self.base_image_selector.select(self.label.text())

    def set_active(self, is_active_: bool = True) -> None:
        if is_active_:
            self.setFixedSize(cf.DEFAULT_MAXIMUM_IMG_SIZE * 1.8)
        else:
            self.setFixedSize(cf.DEFAULT_MAXIMUM_IMG_SIZE)

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        tmp = QHBoxLayout()
        tmp.addStretch()
        tmp.addWidget(self.label)
        tmp.addStretch()
        layout.addLayout(tmp)
        layout.addWidget(self.img)
        self.setLayout(layout)


class BaseImageSelector(QWidget):
    def __init__(self, model_type_: str, parent_: QWidget = None):
        super().__init__(parent_)
        self.image_dict = {
            'Face': BaseImage('Face', f"resource\\All-Images\\{model_type_}\\Face\\Add Some Details\\Art Medium\\Drawing\\Illustration.webp", self),
            'Sphere': BaseImage('Sphere', f"resource\\All-Images\\{model_type_}\\Sphere\\Add Some Details\\Art Medium\\Drawing\\Illustration.webp", self),
            'Landscape': BaseImage('Landscape', f"resource\\All-Images\\{model_type_}\\Landscape\\Add Some Details\\Art Medium\\Drawing\\Illustration.webp", self),
        }
        self.base_image_dict = dict()
        self.selected = None
        self._widgets_to_layout()

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        tmp_layout = QHBoxLayout()
        for image_name in self.image_dict.keys():
            tmp_layout.addWidget(self.image_dict[image_name])
        layout.addLayout(tmp_layout)
        self.setLayout(layout)

    def select(self, name_: str) -> None:
        if name_ == self.selected:
            return
        if self.selected is not None:
            self.base_image_dict[self.selected].setVisible(False)
            self.image_dict[self.selected].set_active(False)
        if name_ in self.base_image_dict:
            self.selected = name_
            self.base_image_dict[self.selected].setVisible(True)
            self.image_dict[self.selected].set_active(True)

    def add_widget(self, where_: str, widget_: QWidget, *args) -> None:
        if where_ in self.base_image_dict:
            self.base_image_dict[where_].add_widget(widget_, *args)

    def add_base_image(self, name_: str) -> None:
        if name_ in self.base_image_dict:
            return
        widget_list = WidgetList(QVBoxLayout)
        widget_list.setVisible(False)
        self.layout().addWidget(widget_list)
        self.base_image_dict[name_] = widget_list
        if self.selected is None:
            self.select(name_)


class IModelWidget(ICentralWidget):
    def __init__(self, model_type_: str, window_manager_):
        super().__init__(window_manager_)
        self.model_type = model_type_
        self.prompt_edit = PromptEdit(self)

        self.copy_btn = QPushButton("Копировать", self)
        self.back_btn = QPushButton("Назад", self)
        self.__init_buttons()

        self.base_image_selector = BaseImageSelector(self.model_type, self)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.base_image_selector)
        self.__scroll_init()

        self._init_settings()

    def __init_buttons(self) -> None:
        self.copy_btn.clicked.connect(self.copy_action)
        self.copy_btn.setStyleSheet(cf.DEFAULT_BUTTON_STYLE_SHEET)
        self.back_btn.clicked.connect(self._to_menu)
        self.back_btn.setStyleSheet(cf.DEFAULT_BUTTON_STYLE_SHEET)

    def __scroll_init(self) -> None:
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(self.prompt_edit)
        tmp_layout.addWidget(self.copy_btn)
        tmp_layout.addWidget(self.back_btn)
        layout.addLayout(tmp_layout)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def _init_settings(self) -> None:
        settings_builder = SettingsBuilder(f"resource/{self.model_type}.json", self)
        settings_builder.build()

    def copy_action(self) -> None:
        pyperclip.copy(self.prompt_edit.prompt)
        # pyperclip.paste()

    def _to_menu(self) -> None:
        self.window_manager.run_menu()


class SettingsBuilder:
    def __init__(self, filename_: str, model_widget_: IModelWidget):
        self.data_dict = dict()
        self.model = model_widget_
        with open(filename_) as file:
            self.data_dict = json.load(file)

    def __configure_to_section(self, name_: str, data_: list) -> SettingsSectionWidget:
        section = SettingsSectionWidget(name_, self.model.prompt_edit, self.model.base_image_selector)
        for item in data_:
            if item['type'] == "section":
                section.add_widget(self.__configure_to_section(item['name'], item['params']))
            elif item['type'] == "parameter":
                section.add_item(item['name'], item['imgPath'], item['hint'] if 'hint' in item else cf.DEFAULT_HINT)
        return section

    def build(self) -> None:
        for bases in self.data_dict['params']:
            self.model.base_image_selector.add_base_image(bases['name'])
            for item in bases['params']:
                if item['type'] == "section":
                    self.model.base_image_selector.add_widget(bases['name'], self.__configure_to_section(item['name'], item['params']))


class IParameterCheckBox(QWidget):
    def __init__(self, name_: str, prompt_: str, prompt_edit_, help_info_: str, parent_: QWidget = None):
        super().__init__(parent_)
        self.name = name_
        self.prompt = prompt_
        self.prompt_edit = prompt_edit_
        self.help_info = help_info_

        self.checkbox = QCheckBox(name_, self)
        self.checkbox.setMaximumWidth(220)
        self.checkbox.stateChanged.connect(self.select_checkbox_action)

        self.prompt_label = QLabel(self.prompt, self)
        self.prompt_label.setMaximumWidth(220)
        self.prompt_label.setStyleSheet("background-color: rgb(51, 53, 56)")

        self.info_label = QLabel(self.help_info, self)
        self.info_label.setStyleSheet("color: rgb(161, 163, 166)")

    def set_active(self, is_active_: bool = True) -> None:
        self.setVisible(is_active_)

    def _widgets_to_layout(self) -> None:
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def select_checkbox_action(self, state_) -> None:
        if state_:
            self.add_to_prompt_action()
        else:
            self.remove_prompt_action()

    def remove_prompt_action(self) -> None:
        self.prompt_edit.remove_prompt(self.prompt)

    def add_to_prompt_action(self) -> None:
        self.prompt_edit.add_prompt(self.prompt)


class ParameterCheckBox(IParameterCheckBox):
    def __init__(self, name_: str, prompt_: str, prompt_edit_, help_info_: str, parent_: QWidget = None):
        super().__init__(name_, prompt_, prompt_edit_, help_info_, parent_)
        self._widgets_to_layout()


class ParameterCheckBoxSlider(IParameterCheckBox):
    def __init__(self, name_: str, prompt_: str, prompt_edit_, help_info_: str, minmaxdef_: list, parent_: QWidget = None):
        super().__init__(name_, prompt_, prompt_edit_, help_info_, parent_)
        self.minmaxdef = minmaxdef_

        self.slider = QSlider(Qt.Horizontal, self)
        self.__init_slider()

        self.value_editor = QLineEdit(self)
        self.__init_editor()

        self._widgets_to_layout()

    def __init_slider(self) -> None:
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setRange(self.minmaxdef[0], self.minmaxdef[1])
        self.slider.setValue(self.minmaxdef[2])
        self.slider.valueChanged.connect(self.slider_changed_action)
        self.setStyleSheet(cf.DEFAULT_SLIDER_STYLE_SHEET)

    def __init_editor(self) -> None:
        self.value_editor.setMaximumWidth(100)
        self.value_editor.setAlignment(Qt.AlignLeft)
        self.value_editor.setValidator(QIntValidator())
        self.value_editor.setText(str(self.minmaxdef[2]))
        self.value_editor.textChanged.connect(self.value_edit_action)

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        tmp = QHBoxLayout()
        tmp.addWidget(self.checkbox)
        tmp.addWidget(self.prompt_label)
        tmp.addWidget(self.info_label)
        layout.addLayout(tmp)
        tmp = QHBoxLayout()
        tmp.addWidget(self.slider)
        tmp.addWidget(self.value_editor)
        layout.addLayout(tmp)
        self.setLayout(layout)

    def remove_prompt_action(self) -> None:
        self.prompt_edit.remove_prompt(self.prompt + '::' + str(self.slider.value()))

    def add_to_prompt_action(self) -> None:
        self.prompt_edit.add_prompt(self.prompt + '::' + str(self.slider.value()))

    def slider_changed_action(self) -> None:
        self.value_editor.setText(str(self.slider.value()))

    def value_edit_action(self, text_: str) -> None:
        iminus = text_.find('-')
        if iminus != -1:
            if self.minmaxdef[0] < 0:
                text_ = text_.replace('-', '')
            else:
                text_ = text_[:iminus + 1] + '0' + text_[iminus + 1:]
        value = self.minmaxdef[0] if len(text_) <= 0 or int(text_) < self.minmaxdef[0] else int(text_)
        if value > self.minmaxdef[1]:
            value = self.minmaxdef[1]
        self.slider.setValue(value)


class MidjourneyModelWidget(IModelWidget):
    def __init__(self, window_manager_):
        super().__init__('Midjourney', window_manager_)
        self.__init_checkbox_settings()
        self._widgets_to_layout()

    def __init_model_parameters(self) -> SettingsSectionWidget:
        parameters_widget = SettingsSectionWidget("Midjourney parameters", self.prompt_edit, self.base_image_selector)
        parameters_widget.add_widget(ParameterCheckBox("Test model", "--test", self.prompt_edit,
                                                       'Use the new general purpose artistic test mode. You get two images using a square aspect ratio; or just one with a non-square aspect ratio',
                                                       parameters_widget))
        parameters_widget.add_widget(ParameterCheckBox("Photo-realism", "--testp", self.prompt_edit,
                                                       'Use the new photo-realism test mode. You get two images using a square aspect ratio; or just one with a non-square aspect ratio',
                                                       parameters_widget))
        parameters_widget.add_widget(ParameterCheckBoxSlider("Image weight", "--iw", self.prompt_edit,
                                                             ' The default image weight is 0.25. Midjourney only supports a single image weight parameter, and you must have at least one image prompt',
                                                             [-10, 10, 0.25], parameters_widget))
        parameters_widget.add_widget(ParameterCheckBoxSlider("Algorithm", "--v", self.prompt_edit,
                                                             'Set the version of the Midjourney engine. In older versions faces, scenes, and creatures are more distorted, and everything is more abstract.',
                                                             [1, 3, 2], parameters_widget))
        parameters_widget.add_widget(ParameterCheckBoxSlider("Quality", "--q", self.prompt_edit,
                                                             'lets you give the algorithm more or less time to think. It also changes the cost of your images. Supported values: 0.25, 0.5, 1, 2, and 5',
                                                             [0.25, 5, 1], parameters_widget))
        parameters_widget.add_widget(ParameterCheckBoxSlider("Stylize", "--s", self.prompt_edit,
                                                             '625 turns it off, 1250 is recommended for experienced users, 2500 is the default, while 20000+ means very strong stylization',
                                                             [625, 60000, 2500], parameters_widget))
        parameters_widget.add_widget(ParameterCheckBoxSlider("Chaos", "--chaos", self.prompt_edit,
                                                             'the level of abstraction. 0 is the default meaning a very literal prompt, while 100 is the maximum, to let chaos reign supreme',
                                                             [0, 100, 0], parameters_widget))
        parameters_widget.add_widget(ParameterCheckBoxSlider("Stop", "--stop", self.prompt_edit,
                                                             'Stop the process earlier. Use lower percentages to avoid adding too much detail, or set it to 100% to finish rendering as usual',
                                                             [10, 100, 100], parameters_widget))
        parameters_widget.add_widget(ParameterCheckBox("Creative mode", "--creative", self.prompt_edit,
                                                       'Will make the results more creative and usually more chaotic as wel', parameters_widget))
        parameters_widget.add_widget(ParameterCheckBox("Seamless texture", "--tile", self.prompt_edit,
                                                       'Will create a tileable texture that can be placed next to itself without creating an obvious seam, join or boundary between the copies of the image', parameters_widget))
        parameters_widget.add_widget(ParameterCheckBox("Save a progress video", "--video", self.prompt_edit,
                                                       'you must react with ✉️ (envelope) to get the video link', parameters_widget))
        parameters_widget.add_widget(ParameterCheckBox("Beta upscaler", "--upbeta", self.prompt_edit,
                                                       'Clean, smooth, and subtle high-resolution upscaling. Works in /relax mode', parameters_widget))
        parameters_widget.add_widget(ParameterCheckBox("Light upscaler", "--uplight", self.prompt_edit,
                                                                   'Upscale results will be closer to the original because the upscaler adds fewer details', parameters_widget))
        return parameters_widget

    def __init_image_size_helper(self) -> SettingsSectionWidget:
        image_size_helper_widget = SettingsSectionWidget("Image size helper", self.prompt_edit, self.base_image_selector)
        image_size_helper_widget.add_widget(ParameterCheckBox("16:9", "--ar 16:9", self.prompt_edit,
                                                                   'today’s standard ratio for film and display', image_size_helper_widget))
        image_size_helper_widget.add_widget(ParameterCheckBox("16:9", "--ar 16:9", self.prompt_edit,
                                                                   'used for mobile first images, such as Instagram stories or Snapchat', image_size_helper_widget))
        image_size_helper_widget.add_widget(ParameterCheckBox("9:16", "--ar 9:16", self.prompt_edit,
                                                                   'Midjourney community favorite for portraits', image_size_helper_widget))
        image_size_helper_widget.add_widget(ParameterCheckBox("4:3", "--ar 4:3", self.prompt_edit,
                                                                   'used to be the aspect ratio of 35mm celluloid film, TVs and monitors', image_size_helper_widget))
        image_size_helper_widget.add_widget(ParameterCheckBox("4:5", "--ar 4:5", self.prompt_edit,
                                                                   'Instagram portrait', image_size_helper_widget))
        image_size_helper_widget.add_widget(ParameterCheckBox("2:1", "--ar 2:1", self.prompt_edit,
                                                                   'The Univisium ratio. Introduced by Vittorio Storaro in the 90s as a compromise between cinema screens and TV screens. Now famous in video streaming', image_size_helper_widget))
        return image_size_helper_widget

    def __init_checkbox_settings(self) -> None:
        for base_image in self.base_image_selector.base_image_dict.keys():
            self.base_image_selector.add_widget(base_image, self.__init_model_parameters())
            self.base_image_selector.add_widget(base_image, self.__init_image_size_helper())


class DreamStudioModelWidget(IModelWidget):
    def __init__(self, window_manager_):
        super().__init__('DreamStudio', window_manager_)
        self._widgets_to_layout()


class StableDiffusionModelWidget(IModelWidget):
    def __init__(self, window_manager_):
        super().__init__('Stable Diffusion', window_manager_)
        self._widgets_to_layout()


class ButtonIconWidget(QWidget):
    def __init__(self, name_: str, img_path_: str, action_, parent_: QWidget = None):
        super().__init__(parent_)
        self.button = QPushButton(name_, self)
        self.button.clicked.connect(action_)
        self.button.setFixedHeight(50)
        self.button.setMinimumWidth(350)
        self.button.setStyleSheet(cf.DEFAULT_BUTTON_STYLE_SHEET)

        self.setMaximumWidth(500)

        self.img = QLabel(self)
        pixmap = QPixmap(img_path_)
        self.img.setPixmap(pixmap)

        self._widgets_to_layout()

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.img)
        layout.addWidget(self.button)
        self.setLayout(layout)


class MenuWidget(ICentralWidget):
    def __init__(self, window_manager_):
        super().__init__(window_manager_)
        self.button_list = WidgetList(QHBoxLayout, self)

        self.button_list.add_widget(ButtonIconWidget("Midjourney", "resource/midjourney-logo.webp", self.midjourney_action))
        self.button_list.add_widget(ButtonIconWidget("DreamStudio", "resource/dreamstudio-logo.webp", self.dream_studio_action))
        self.button_list.add_widget(ButtonIconWidget("Stable Diffusion", "resource/stablediffusion-logo.webp", self.stable_diffusion_action))

        self._widgets_to_layout()
    
    def midjourney_action(self) -> None:
        self.window_manager.run_midjourney()

    def dream_studio_action(self) -> None:
        self.window_manager.run_dream_studio()

    def stable_diffusion_action(self) -> None:
        self.window_manager.run_stable_diffusion()
    
    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.button_list)
        layout.addStretch()
        self.setLayout(layout)
