
# ui.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from PyQt4 import QtCore, QtGui
from src.common.widgets import ImageHoverButton, MultistageProgressBar, ComboBox


APP_WIDTH = 500
APP_HEIGHT = 330
CONTAINER_HEIGHT = 140

PROGRESS_BAR_WIDTH = 350
PROGRESS_BAR_HEIGHT = 30

LABEL_WIDTH = 460
LABEL_HEIGHT = 25

COMBO_BOX_WIDTH = 300
COMBO_BOX_HEIGHT = 30

CSS_TEXT_BOLD = "{font-family : Bariol; font-style : bold; font-size : 15px; color : #FFFFFF;}"
CSS_TEXT = "{font-family : Bariol; font-size : 13px; color : #FFE3CF;}"

res_path = "res/images/"


class UI(QtGui.QWidget):

    def __init__(self):
        super(UI, self).__init__()
        self.initUI()

    def initUI(self):
        # initialise the UI - set title, size, center, set theme, app frames
        # and finally display it
        self.setWindowTitle('Kano OS Burner')
        self.resize(APP_WIDTH, APP_HEIGHT)
        self.center()
        self.setTheme()
        self.createScreens()
        self.showScreen(self.introScreen)
        self.show()
        self.onStart()

    # @Override
    # gets called when the main window is closed - we clean up here
    def closeEvent(self, event):
        self.onFinish()

    def center(self):
        # centers the window on the screen
        window = self.frameGeometry()
        screen_center = QtGui.QDesktopWidget().availableGeometry().center()
        window.moveCenter(screen_center)
        self.move(window.topLeft())

    def setTheme(self):
        # changing the background color of the main window
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor(255, 132, 42))  # FF842A
        self.setPalette(palette)

        header = QtGui.QLabel(self)
        header.move(44, 35)
        header.setPixmap(QtGui.QPixmap(res_path + 'header.png'))

        footer = QtGui.QLabel(self)
        footer.move(163, 275)
        footer.setPixmap(QtGui.QPixmap(res_path + 'footer.png'))

    def createScreens(self):
        self.introScreen = self.createIntroScreen(0, 120)
        self.progressScreen = self.createProgressScreen(0, 120)
        self.finishScreen = self.createFinishScreen(0, 120)
        self.errorScreen = self.createErrorScreen(0, 120)

    def createIntroScreen(self, x, y):
        container = self.createContainer(x, y)

        self.disksComboBox = container.addComboBox(COMBO_BOX_WIDTH, COMBO_BOX_HEIGHT, self.onComboBoxClick, 'Select device')
        self.startButton = container.addImageButton(self.onStartClick, res_path + 'burn.png')
        return container

    def createProgressScreen(self, x, y):
        container = self.createContainer(x, y)

        self.statusTitleLabel = container.addLabel(LABEL_WIDTH, LABEL_HEIGHT, 'Status title', CSS_TEXT_BOLD)
        self.statusDescriptionLabel = container.addLabel(LABEL_WIDTH, LABEL_HEIGHT, 'Status description', CSS_TEXT)
        container.addSpacer(5)
        self.progressBar = container.addProgressBar(PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT, 2)
        container.addSpacer(20)
        return container

    def createFinishScreen(self, x, y):
        container = self.createContainer(x, y)

        self.finishLabel = container.addLabel(LABEL_WIDTH, LABEL_HEIGHT, "Kano OS has successfully been burned. Let's go!", CSS_TEXT_BOLD)
        self.FinishButton = container.addImageButton(self.onFinishClick, res_path + 'finish.png')
        return container

    def createErrorScreen(self, x, y):
        container = self.createContainer(x, y)

        self.errorTitleLabel = container.addLabel(LABEL_WIDTH, LABEL_HEIGHT, 'Error title', CSS_TEXT_BOLD)
        self.errorDescriptionLabel = container.addLabel(LABEL_WIDTH, LABEL_HEIGHT, 'Error description', CSS_TEXT)
        container.addSpacer(20)
        self.FinishButton = container.addImageButton(self.onRetryClick, res_path + 'retry.png')
        return container

    def createContainer(self, x, y):
        container = VerticalContainer(self)
        container.hide()
        container.setGeometry(x, y, APP_WIDTH, CONTAINER_HEIGHT)
        return container

    def showScreen(self, screen):
        self.introScreen.hide()
        self.progressScreen.hide()
        self.finishScreen.hide()
        self.errorScreen.hide()
        screen.show()

    def setProgress(self, progress):
        self.progressBar.processes
        self.progressBar.setValue(progress)

    def setStatusTitle(self, text):
        self.statusTitleLabel.setText(text)

    def setStatusDescription(self, text):
        self.statusDescriptionLabel.setText(text)

    def setError(self, error):
        self.errorTitleLabel.setText(error['title'])
        self.errorDescriptionLabel.setText(error['description'])
        self.showScreen(self.errorScreen)

    def setComboBox(self, item_list):
        self.disksComboBox.removeItem('Device')
        for item in item_list:
            self.disksComboBox.addItem(item)

    def onStart(self):
        pass

    def onFinish(self):
        pass

    def onStartClick(self):
        pass

    def onRetryClick(self):
        pass

    def onFinishClick(self):
        pass

    def onComboBoxClick(self):
        pass


class VerticalContainer(QtGui.QWidget):

    def __init__(self, parent):
        super(VerticalContainer, self).__init__(parent)
        self.widgets = list()

    def addImageButton(self, onClick, imagePath):
        button = ImageHoverButton(self, imagePath)
        button.clicked.connect(onClick)
        self.widgets.append(button)
        return button

    def addProgressBar(self, width, height, processes=1, styling=''):
        progress_bar = MultistageProgressBar(self, processes)
        progress_bar.resize(width, height)
        progress_bar.setStyleSheet('QProgressBar ' + styling)
        self.widgets.append(progress_bar)
        return progress_bar

    def addLabel(self, width, height, text, styling=''):
        label = QtGui.QLabel(text, self)
        label.resize(width, height)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet('QLabel ' + styling)
        self.widgets.append(label)
        return label

    def addComboBox(self, width, height, onClick, defaultItem=None):
        combo_box = ComboBox(self, defaultItem)
        combo_box.resize(width, height)
        combo_box.opened.connect(onClick)
        self.widgets.append(combo_box)
        return combo_box

    def addSpacer(self, height):
        spacer = QtGui.QWidget(self)
        spacer.resize(self.width(), height)
        self.widgets.append(spacer)

    # @Override
    # This method is called automatically when the widget is displayed with show()
    # It centers all vertically added widgets in this container horizontally
    def showEvent(self, event):
        widget_cummulated_height = 0
        for widget in self.widgets:
            widget_cummulated_height += widget.height()

        # calculate an equal spacing between the widgets
        spacing = (self.height() - widget_cummulated_height) / (len(self.widgets) + 1)
        current_height = 0

        # add the widgets centrally in X and equally distanced in Y
        for widget in self.widgets:
            current_height += spacing
            widget.move((self.width() - widget.width()) / 2, current_height)
            current_height += widget.height()
