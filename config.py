from PySide6.QtCore import QSize


WINDOW_TITLE = "Prompt Manager"

DEFAULT_IMG_PATH = "resource/illustration.png"

DEFAULT_MAXIMUM_IMG_SIZE = QSize(150, 240)

DEFAULT_HINT = "Maybe it will help you"

DEFAULT_APP_STYLE_SHEET = "background-color: rgb(71, 73, 76);"\
                           "color: white;"
DEFAULT_BUTTON_STYLE_SHEET = "background-color: rgb(61, 63, 66)"
DEFAULT_SLIDER_STYLE_SHEET = """
        QSlider::groove:horizontal {
    border: 1px solid #565a5e;
    height: 10px;
    background: rgb(100, 100, 100);
    margin: 0px;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: rgb(127, 0, 255);
    border: 1px solid #565a5e;
    width: 24px;
    height: 8px;
    border-radius: 4px;
}
        """
