#!/usr/bin/env python

# ui.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Kano Burner UI back-end
#
# The UI base class handles all the PyQt front-end and uses a VerticalContainer
# as a layout manager.
#
# The application's window contains two such VerticalContainers. The first holds
# only the header, footer and a spacer between the two. The second holds the
# widgets needed on that specific screen.


import os
from PyQt4 import QtGui
from src.common.widgets import VerticalContainer
from src.common.utils import load_css_for_widget, BURNER_VERSION
from src.common.paths import images_path, anim_path, css_path


# App dimensions constants
APP_WIDTH = 500
APP_HEIGHT = 330
CONTAINER_HEIGHT = 140

# These are used as object names for labels within the application
# and are used to differentiate between CSS styles - see res/CSS/label.css
LABEL_CSS_TITLE = 'title'
LABEL_CSS_DESCRIPTION = 'description'
LABEL_CSS_FOOTER = 'footer'


class UI(QtGui.QWidget):
    '''
    This base class handles all the PyQt front-end.

    The application then has the freedom of defining its behaviour by implementing
    the event stubs provided without being concerned about Qt api.

    It uses a custom layout manager to build the front-end which again hides
    Qt api in order to make the code more readable and avoid duplication.

    The notion of 'screen' is used here to encapsulate the widgets used in
    the different stages of the application, e.g. Downloading: Title, Status, ProgressBar.

    We switch between different screens by hiding all of them
    and showing only the one we want.
    '''

    def __init__(self):
        super(UI, self).__init__()
        self.success = False # To allow the chance to offer feedback if the burn fails
        self.initUI()

    def initUI(self):
        # initialise the UI - set title, size, center, set theme, app frames etc
        # and finally display it
        self.setWindowTitle('Kano OS Burner v{}'.format(BURNER_VERSION))
        self.resize(APP_WIDTH, APP_HEIGHT)
        self.center()
        self.setTheme()
        self.createScreens()
        self.showScreen(self.dependencyScreen)
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
        self.container.addImage(os.path.join(images_path, 'header.png'))
        self.container.addSpacer(CONTAINER_HEIGHT)
        footer = self.container.addLabel("Questions? Visit help.kano.me", objectName=LABEL_CSS_FOOTER)
        load_css_for_widget(footer, os.path.join(css_path, 'label.css'))

    def createScreens(self):
        # the screens will be positioned on the spacer of the main VerticalContainer
        self.dependencyScreen = self.createDependencyScreen(0, 120)
        self.diskScreen = self.createDiskScreen(0, 120)
        self.progressScreen = self.createProgressScreen(0, 120)
        self.finishScreen = self.createFinishScreen(0, 120)
        self.errorScreen = self.createErrorScreen(0, 120)

    def createDependencyScreen(self, x, y):
        container = self.createContainer(x, y)

        self.statusTitleLabel = container.addLabel("Checking for dependencies..", LABEL_CSS_TITLE)
        self.statusDescriptionLabel = container.addLabel("looking for resources, tools, and free space", LABEL_CSS_DESCRIPTION)
        container.addSpacer(20)
        self.spinnerAnimation = container.addAnimation(os.path.join(anim_path, 'spinner_2_lines.gif'))
        container.addSpacer(10)
        return container

    def createDiskScreen(self, x, y):
        container = self.createContainer(x, y)

        self.disksComboBox = container.addComboBox(self.onComboBoxClick, defaultItem='Select device')
        self.startButton = container.addButton("BURN!", self.onStartClick)
        self.startButton.setEnabled(False)  # disable the BURN! button
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
        self.finishDescriptionLabel = container.addLabel('description', LABEL_CSS_DESCRIPTION)
        self.FinishButton = container.addButton("FINISH", self.onFinishClick)
        return container

    def createErrorScreen(self, x, y):
        container = self.createContainer(x, y)

        self.errorTitleLabel = container.addLabel('title', LABEL_CSS_TITLE)
        self.errorDescriptionLabel = container.addLabel('description', LABEL_CSS_DESCRIPTION)
        container.addSpacer(20)
        self.FinishButton = container.addButton("TRY AGAIN", self.onRetryClick)
        return container

    def createContainer(self, x, y):
        # this is used when creating the app screens
        container = VerticalContainer(self)
        container.hide()
        container.setGeometry(x, y, APP_WIDTH, CONTAINER_HEIGHT)
        return container

    def showScreen(self, screen):
        self.dependencyScreen.hide()
        self.diskScreen.hide()
        self.progressScreen.hide()
        self.finishScreen.hide()
        self.errorScreen.hide()
        screen.show()

    def showError(self, error):
        self.errorTitleLabel.setText(error['title'])
        self.errorDescriptionLabel.setText(error['description'])
        self.showScreen(self.errorScreen)

    def showFinishScreen(self, message=None):
        if 'title' in message:
            self.finishLabel.setText(message['title'])
        if 'description' in message:
            self.finishDescriptionLabel.setText(message['description'])
        self.showScreen(self.finishScreen)

    def setProgress(self, progress):
        self.progressBar.setValue(progress)

    def setStatusTitle(self, text):
        self.statusTitleLabel.setText(text)

    def setStatusDescription(self, text):
        self.statusDescriptionLabel.setText(text)

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
