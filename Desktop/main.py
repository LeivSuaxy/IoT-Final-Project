import sys
from PyQt6.QtWidgets import QApplication

from ui import RFIDInterface
from ui.styles import DARK_THEME


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet(DARK_THEME)

    window = RFIDInterface()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()