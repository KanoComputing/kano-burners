
# widgets.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from PyQt4 import QtCore, QtGui


class ImageHoverButton(QtGui.QLabel):

    # this signal is sent when the user clicks and releases whilst still inside the widget
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent, imagePath):
        QtGui.QLabel.__init__(self, parent)
        self.setPixmap(QtGui.QPixmap(imagePath))

    # @Override
    def mouseReleaseEvent(self, event):
        self.clicked.emit()
    '''
    # @Override
    def enterEvent(self, event):
        print 'enter'

    # @Override
    def leaveEvent(self, event):
        print 'leave'
    '''

class ComboBox(QtGui.QComboBox):

    # this signal is sent when the user clicks the widget and the popup list is shown
    opened = QtCore.pyqtSignal()

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
    def mousePressEvent(self, event):
        self.opened.emit()
        return super(ComboBox, self).mousePressEvent(event)


class MultistageProgressBar(QtGui.QProgressBar):

    def __init__(self, parent, processes=1):
        QtGui.QProgressBar.__init__(self, parent)

        self.processes = processes
        self.processes_done = 0
        self.current_process_progress = 0

    # @Override
    def reset(self):
        self.processes_done = 0
        self.current_process_progress = 0
        return super(MultistageProgressBar, self).reset()

    # @Override
    def setValue(self, progress):
        # check if a new process is reporting its progress
        if self.current_process_progress > progress:
            self.processes_done += 1

        # calculate the overall progress
        self.current_process_progress = progress
        overall_progress = (1.0 / self.processes) * (progress + 100.0 * self.processes_done)

        return super(MultistageProgressBar, self).setValue(overall_progress)
