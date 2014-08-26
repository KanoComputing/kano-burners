
# widgets.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


import os
from PyQt4 import QtCore, QtGui
from src.common.utils import load_css_for_widget
from src.common.paths import images_path, css_path


class HoverButton(QtGui.QPushButton):

    # @Override
    def enterEvent(self, event):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        return super(HoverButton, self).enterEvent(event)

    # @Override
    def leaveEvent(self, event):
        QtGui.QApplication.restoreOverrideCursor()
        return super(HoverButton, self).leaveEvent(event)


class ComboBox(QtGui.QComboBox):

    # these signals are emitted when the user clicks the
    # widget and the popup list is shown or closed
    clicked = QtCore.pyqtSignal()
    resized = QtCore.pyqtSignal()

    def __init__(self, parent, defaultItem=None):
        QtGui.QComboBox.__init__(self, parent)

        self.defaultItem = defaultItem
        if self.defaultItem:
            self.addItem(self.defaultItem)

    def restore(self):
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
        progressBar.setTextVisible(False)
        load_css_for_widget(progressBar, os.path.join(css_path, 'progressbar.css'))
        self.widgets.append(progressBar)
        return progressBar

    def addLabel(self, text, objectName=""):
        label = QtGui.QLabel(text, self)
        label.setObjectName(objectName)
        load_css_for_widget(label, os.path.join(css_path, 'label.css'))
        self.widgets.append(label)
        return label

    def addImage(self, imagePath):
        image = QtGui.QLabel(self)
        image.setPixmap(QtGui.QPixmap(imagePath))
        self.widgets.append(image)
        return image

    def addComboBox(self, onClick, defaultItem=None):
        comboBox = ComboBox(self, defaultItem)
        comboBox.clicked.connect(onClick)
        comboBox.resized.connect(self.centerWidgets)
        comboBox.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        load_css_for_widget(comboBox, os.path.join(css_path, 'combobox.css'), images_path)
        self.widgets.append(comboBox)
        return comboBox

    def addSpacer(self, height):
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
