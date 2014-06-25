
# ui.py
# 
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from Tkinter import *


APP_WIDTH  = 450
APP_HEIGHT = 280


# [Class description]
class UI(Frame):

	# [Method description]
	def __init__(self, parent=None):
		Frame.__init__(self, parent)

		# set the title for the application window
		self.parent = parent		
		self.parent.title("Kano OS Burner")

		# get the screen dimensions and center the window geometry
		appX = (parent.winfo_screenwidth() - APP_WIDTH) / 2
		appY = (parent.winfo_screenheight() - APP_HEIGHT) / 2
		self.parent.geometry("%dx%d+%d+%d" % (APP_WIDTH, APP_HEIGHT, appX, appY))

		# set the background and app graphics
		self.parent.config(bg = "#ff8c00")

		# set the app header and footer images
		Label(self.parent, image=PhotoImage(file="images/header.gif")).pack()
		Label(self.parent, image=PhotoImage(file="images/footer.gif")).pack()
		
		# 
		#activeWidgets = []
		#activeWidgetsCount = 0


	# [Method description]
	def createFrame(self):
		return AppFrame(self.parent)


# [Class description]
class AppFrame(Frame):

	# [Method description]
	def __init__(self, parent=None):
		Frame.__init__(self, parent)

		# set the parent window for this frame
		self.config(bg = "#555555")
		self.place(x = 0, y = 0, anchor = NW)


	# [Method description]
	def show(self):
		self.pack(fill=BOTH)


	# [Method description]
	def hide(self):
		self.place_forget()
		#for widget in activeWidgets:
		#	widget.

	
	# [Method description]
	def addImageButton(self, onClick, imageName, x, y):

		image = PhotoImage(imageName)
		#imageButton = Label(self, text="Hello World!")
		imageButton = Label(self, image=image)
		imageButton.bind("<Button-1>", onClick)
		#imageButton.place(x = x, y = y, anchor = NW)
		imageButton.pack()
		#activeWidgets.add(imageButton)


	# [Method description]
	def addProgressBar(self):
		return None
		#progress


	# [Method description]
	def addDropDown(self, onClick):
		return None
