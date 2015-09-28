#!/usr/bin/env python

# widgets.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Custom PyQt widgets
#
# We customise and/or extend standard PyQt widgets in this file such
# that they suit our needs. For the most part, these widgets may be
# extended further and used in other projects.


import os
from PyQt4 import QtCore, QtGui
from src.common.utils import load_css_for_widget, read_file_contents, debugger
from src.common.paths import images_path, css_path, base_path


class HoverButton(QtGui.QPushButton):
    '''
    This extended Button widget simply changes the mouse cursor
    when it is inside and restores it otherwise.
    '''

    # @Override
    def enterEvent(self, event):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        return super(HoverButton, self).enterEvent(event)

    # @Override
    def leaveEvent(self, event):
        QtGui.QApplication.restoreOverrideCursor()
        return super(HoverButton, self).leaveEvent(event)


class ComboBox(QtGui.QComboBox):
    '''
    This extended ComboBox widget has two additional signals, change
    the mouse cursor on hover, and can have a default item.

    This item is simply some text we display on the widget until
    the user selects an item from the menu.
    '''

    # custom signals for when the user clicks the widget and
    # when the widget resizes
    clicked = QtCore.pyqtSignal()
    resized = QtCore.pyqtSignal()

    def __init__(self, parent, defaultItem=None):
        QtGui.QComboBox.__init__(self, parent)

        self.defaultItem = defaultItem
        if self.defaultItem:
            self.addItem(self.defaultItem)

    def restore(self):
        # this method should be used when removing all the items
        # and the default item should be restored
        self.clear()
        if self.defaultItem:
            self.addItem(self.defaultItem)

    # @Override
    def resizeEvent(self, event):
        self.resized.emit()
        dropdown = self.view()
        dropdown.setMinimumWidth(self.width())
        return super(ComboBox, self).resizeEvent(event)

    # @Override
    def mousePressEvent(self, event):
        self.clicked.emit()
        return super(ComboBox, self).mousePressEvent(event)

    # @Override
    def enterEvent(self, event):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        return super(ComboBox, self).enterEvent(event)

    # @Override
    def leaveEvent(self, event):
        QtGui.QApplication.restoreOverrideCursor()
        return super(ComboBox, self).leaveEvent(event)


class MultistageProgressBar(QtGui.QProgressBar):
    '''
    This progress bar reports overall progress for a given number
    of processes using it.

    The processes report in their own frame of reference (0-100%) by setting that
    value on the widget, we then calculate and display the overall progress.

    WARNING: It is assumed that all processes report in an ascending manner ONLY!
             If process X retries, the widget assumes the next process is reporting!
    '''

    def __init__(self, parent, stages=1):
        QtGui.QProgressBar.__init__(self, parent)

        self.stages = stages
        self.stages_completed = 0
        self.current_stage_progress = 0

    # @Override
    def reset(self):
        self.stages_completed = 0
        self.current_stage_progress = 0
        return super(MultistageProgressBar, self).reset()

    # @Override
    def setValue(self, progress):
        # a simplistic approach to check if a new process is reporting its progress
        if self.current_stage_progress > progress:
            self.stages_completed += 1

        # calculate the overall progress
        self.current_stage_progress = progress
        overall_progress = (1.0 / self.stages) * (progress + 100.0 * self.stages_completed)

        return super(MultistageProgressBar, self).setValue(overall_progress)


class VerticalContainer(QtGui.QWidget):
    '''
    This is a custom layout manager which can only have certain types of
    widgets inside, added via their respective functions.

    The widgets are positined vertically one after the other (in the order
    they have been added), centered, and equally distanced from one another.

    Methods which add widgets to the container will also set CSS styling.
    '''

    # TODO: include addVerticalContainer() - to be used by UI instead of a spacer

    def __init__(self, parent):
        super(VerticalContainer, self).__init__(parent)
        self.widgets = list()

    def addButton(self, text, onClick):
        button = HoverButton(text, self)
        button.clicked.connect(onClick)
        load_css_for_widget(button, os.path.join(css_path, 'button.css'))
        self.widgets.append(button)
        return button

    def addProgressBar(self, stages=1):
        progressBar = MultistageProgressBar(self, stages)
        progressBar.setTextVisible(False)  # hide a default % completion text
        load_css_for_widget(progressBar, os.path.join(css_path, 'progressbar.css'))
        self.widgets.append(progressBar)
        return progressBar

    def addLabel(self, text, objectName=""):
        label = QtGui.QLabel(text, self)
        label.setObjectName(objectName)  # set a class ID for CSS styling
        load_css_for_widget(label, os.path.join(css_path, 'label.css'))
        self.widgets.append(label)
        return label

    def addImage(self, imagePath):
        image = QtGui.QLabel(self)
        image.setPixmap(QtGui.QPixmap(imagePath))
        self.widgets.append(image)
        return image

    def addAnimation(self, gifPath):
        gifAnimation = QtGui.QLabel(self)
        gifAnimation.setObjectName('animation')
        load_css_for_widget(gifAnimation, os.path.join(css_path, 'label.css'))
        gif = QtGui.QMovie(gifPath)
        gifAnimation.setMovie(gif)
        gif.start()
        self.widgets.append(gifAnimation)
        return gifAnimation

    def addComboBox(self, onClick, defaultItem=None):
        comboBox = ComboBox(self, defaultItem)
        comboBox.clicked.connect(onClick)
        comboBox.resized.connect(self.centerWidgets)

        # the resizing policy will allow the combobox to resize depending on its contents
        comboBox.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        load_css_for_widget(comboBox, os.path.join(css_path, 'combobox.css'), images_path)
        self.widgets.append(comboBox)
        return comboBox

    def addSpacer(self, height):
        # to be used when customising spacing between widgets
        spacer = QtGui.QWidget(self)
        spacer.resize(self.width(), height)
        self.widgets.append(spacer)

    # @Override
    # This method is called automatically when the widget is displayed with show()
    def showEvent(self, event):
        self.centerWidgets()

    # It centers all vertically added widgets, in this container, horizontally
    def centerWidgets(self):
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


class DisclaimerDialog(QtGui.QDialog):
    '''
    This is a custom popup dialog which contains a title, textedit,
    a checkbox, and two buttons to accept or cancel.

    We show a disclaimer before starting the burning process, informing
    the user again about the dangers of overwriting disks.
    '''

    def __init__(self, parent):
        super(DisclaimerDialog, self).__init__(parent)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))
        self.setPalette(palette)

        self.setWindowTitle("Are you sure?")
        heading = QtGui.QLabel("Hey! Are you sure?")
        heading.setObjectName("dialogTitle")
        load_css_for_widget(heading, os.path.join(css_path, 'label.css'))

        textview = self.addTextEdit()

        self.checkbox = QtGui.QCheckBox('I still want to do this', self)
        self.checkbox.clicked.connect(self.enableButton)
        load_css_for_widget(self.checkbox, os.path.join(css_path, 'checkbox.css'))

        self.okButton = QtGui.QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.okButton.setEnabled(False)
        self.okButton.setObjectName("dialogOk")
        load_css_for_widget(self.okButton, os.path.join(css_path, 'button.css'))

        cancelButton = QtGui.QPushButton("CANCEL")
        cancelButton.clicked.connect(self.reject)
        cancelButton.setObjectName("dialogCancel")
        load_css_for_widget(cancelButton, os.path.join(css_path, 'button.css'))

        mainLayout = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        hbox.addSpacing(80)
        hbox.addWidget(self.okButton)
        hbox.addSpacing(20)
        hbox.addWidget(cancelButton)
        hbox.addSpacing(80)

        mainLayout.setSpacing(20)
        mainLayout.addWidget(heading)
        mainLayout.addWidget(textview)
        mainLayout.addWidget(self.checkbox, alignment=QtCore.Qt.AlignHCenter)
        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

    def enableButton(self):
        self.okButton.setEnabled(self.checkbox.isChecked())

    def addTextEdit(self):
        textEdit = QtGui.QTextEdit()
        load_css_for_widget(textEdit, os.path.join(css_path, 'textedit.css'))

        disclaimer_path = os.path.join(base_path, "DISCLAIMER")
        disclaimer_text = read_file_contents(disclaimer_path)

        textEdit.setText(disclaimer_text)
        textEdit.setReadOnly(True)
        textEdit.setGeometry(100, 100, 800, 600)

        return textEdit

    def accepted(self):
        '''
        This method is used by the BurnerGUI when the user clicks BURN!

        We popup the dialog, wait for the user to click one of the buttons,
        and return whether the user accepted the disclaimer.
        '''

        response = self.exec_()
        return response == QtGui.QDialog.Accepted


class LogReportDialog(QtGui.QDialog):
    '''
    This is a custom popup dialog which contains a title, textedit,
    a checkbox, and two buttons to accept or cancel.

    We show a disclaimer before starting the burning process, informing
    the user again about the dangers of overwriting disks.
    '''

    def __init__(self, parent, logtext):
        super(LogReportDialog, self).__init__(parent)

        self.log = logtext

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))
        self.setPalette(palette)

        self.setWindowTitle("Sorry we didn't get to finish burning your SD card")
        heading = QtGui.QLabel("Want to send us the logs to allow us to improve?")
        heading.setObjectName("dialogTitle")
        load_css_for_widget(heading, os.path.join(css_path, 'label.css'))

        self.emailMessage = "Optionally enter email address"

        emailentry = self.addTextEdit(text=self.emailMessage, readOnly=False, oneLine=True)
        textview = self.addTextEdit(self.log, startsVisible=False)
        self.textview = textview
        self.emailentry = emailentry

        self.logButton = QtGui.QPushButton("View Log")
        self.logButton.clicked.connect(self.toggleLog)
        self.logButton.setObjectName("dialogOk")
        load_css_for_widget(self.logButton, os.path.join(css_path, 'button.css'))

        self.okButton = QtGui.QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.okButton.setObjectName("dialogOk")
        load_css_for_widget(self.okButton, os.path.join(css_path, 'button.css'))

        cancelButton = QtGui.QPushButton("CANCEL")
        cancelButton.clicked.connect(self.reject)
        cancelButton.setObjectName("dialogCancel")
        load_css_for_widget(cancelButton, os.path.join(css_path, 'button.css'))

        mainLayout = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        hbox.addSpacing(20)
        hbox.addWidget(self.logButton)
        hbox.addSpacing(80)
        hbox.addWidget(self.okButton)
        hbox.addSpacing(20)
        hbox.addWidget(cancelButton)
        hbox.addSpacing(80)

        mainLayout.setSpacing(20)
        mainLayout.addWidget(heading)
        mainLayout.addWidget(emailentry)
        mainLayout.addWidget(textview)
        mainLayout.addLayout(hbox)


        self.setLayout(mainLayout)
        cancelButton.setFocus()

    def toggleLog(self):
        self.textview.setVisible(not self.textview.isVisible())

    def getEmail(self):
        return self.emailentry.text()

    def addTextEdit(self, text, readOnly=True, startsVisible=True, oneLine=False):
        if oneLine:
            textEdit = QtGui.QLineEdit()
        else:
            textEdit = QtGui.QTextEdit()
        load_css_for_widget(textEdit, os.path.join(css_path, 'textedit.css'))

        if readOnly:
            textEdit.setText(text)
        else:
            textEdit.setPlaceholderText(text)

        textEdit.setReadOnly(readOnly)
        textEdit.setGeometry(100, 100, 800, 600)
        textEdit.setVisible(startsVisible)

        return textEdit

    def accepted(self):
        '''
        This method is used by the BurnerGUI when the user quits the app.

        We popup the dialog, wait for the user to click one of the buttons,
        and return whether the user accepted the disclaimer.
        '''

        response = self.exec_()
        return response == QtGui.QDialog.Accepted
