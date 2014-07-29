
# ui.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from PyQt4 import QtGui
from src.common.widgets import VerticalContainer
from src.common.utils import load_css_for_widget, images_path, css_path


APP_WIDTH = 500
APP_HEIGHT = 330
CONTAINER_HEIGHT = 140

# These are used as object names for labels within the application
# and are used to differentiate between CSS styles - see res/CSS/label.css
LABEL_CSS_TITLE = 'title'
LABEL_CSS_DESCRIPTION = 'description'
LABEL_CSS_FOOTER = 'footer'


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
        # centers the application on the screen
        window = self.frameGeometry()
        screen_center = QtGui.QDesktopWidget().availableGeometry().center()
        window.moveCenter(screen_center)
        self.move(window.topLeft())

    def setTheme(self):
        # the application window only has a vertical container which contains
        # exactly 3 items: a header image, a spacer for the active screen, and a footer
        self.container = VerticalContainer(self)
        self.container.setGeometry(0, 0, APP_WIDTH, APP_HEIGHT)

        # changing the background color of the main window
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor(255, 132, 42))  # FF842A
        self.setPalette(palette)

        # adding the 3 items to the application container
        self.container.addImage(images_path + "header.png")
        self.container.addSpacer(CONTAINER_HEIGHT)
        footer = self.container.addLabel("Questions? help@kano.me", objectName=LABEL_CSS_FOOTER)
        load_css_for_widget(footer, css_path + "label.css")

    def createScreens(self):
        self.introScreen = self.createIntroScreen(0, 120)
        self.progressScreen = self.createProgressScreen(0, 120)
        self.finishScreen = self.createFinishScreen(0, 120)
        self.errorScreen = self.createErrorScreen(0, 120)

    def createIntroScreen(self, x, y):
        container = self.createContainer(x, y)

        self.disksComboBox = container.addComboBox(self.onComboBoxClick, defaultItem='Select device')
        self.startButton = container.addButton("BURN!", self.onStartClick)
        self.startButton.setEnabled(False)
        return container

    def createProgressScreen(self, x, y):
        container = self.createContainer(x, y)

        self.statusTitleLabel = container.addLabel("Status title", LABEL_CSS_TITLE)
        self.statusDescriptionLabel = container.addLabel("Status description", LABEL_CSS_DESCRIPTION)
        container.addSpacer(5)
        self.progressBar = container.addProgressBar(stages=2)
        container.addSpacer(20)
        return container

    def createFinishScreen(self, x, y):
        container = self.createContainer(x, y)

        self.finishLabel = container.addLabel("Kano OS has successfully been burned. Let's go!", LABEL_CSS_TITLE)
        self.FinishButton = container.addButton("FINISH", self.onFinishClick)
        return container

    def createErrorScreen(self, x, y):
        container = self.createContainer(x, y)

        self.errorTitleLabel = container.addLabel('Error title', LABEL_CSS_TITLE)
        self.errorDescriptionLabel = container.addLabel('Error description', LABEL_CSS_DESCRIPTION)
        container.addSpacer(20)
        self.FinishButton = container.addButton("TRY AGAIN", self.onRetryClick)
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

    def showError(self, error):
        self.errorTitleLabel.setText(error['title'])
        self.errorDescriptionLabel.setText(error['description'])
        self.showScreen(self.errorScreen)

    def setProgress(self, progress):
        self.progressBar.setValue(progress)

    def setStatusTitle(self, text):
        self.statusTitleLabel.setText(text)

    def setStatusDescription(self, text):
        self.statusDescriptionLabel.setText(text)

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
