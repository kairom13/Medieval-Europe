"""
Created on Aug 1, 2022

@author: kairom13
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from Medieval_Europe.Code.Widgets.Displays import ObjectLabel
from Medieval_Europe.Code.Widgets.Buttons import RemoveConnectionButton


## Dropdown for choosing between types of objects:
# Person
# Title
# Place
class ObjectType(QComboBox):
    def __init__(self, parameters):
        super(ObjectType, self).__init__()

        self.value = None
        self.objectList = None
        self.window = parameters['Window']
        self.logger = self.window.logger

        itemList = ['Person', 'Title', 'Place']
        self.addItems(itemList)
        self.objectType = parameters['Object Type']
        self.setCurrentIndex(itemList.index(self.objectType))

        self.currentIndexChanged.connect(self.newChoice)

    def newChoice(self):
        self.value = self.currentText()
        self.logger.log('Code', str(self.value) + ' was chosen')

        self.objectList = self.window.objectLists[self.value]

        self.window.page_factory('view_object_list', {'Object List': self.objectList, 'Object Type': self.value, 'Search Text': '', 'Page Type': 'View'})


class SpouseChoice(QComboBox):
    def __init__(self, parameters):
        super(SpouseChoice, self).__init__()

        self.value = None
        self.objectList = None
        self.window = parameters['Window']
        self.logger = self.window.logger

        self.subject = parameters['Subject']
        self.item_list = {}
        for s in self.subject.spouses:
            if s == 'unknown_spouse':
                self.item_list.update({'Unknown Spouse': s})
            else:
                self.item_list.update({self.window.get_object(s).getAttribute('Name'): s})

        self.addItems(self.item_list.keys())

        if len(self.subject.spouses) == 2:
            for s in self.subject.spouses:
                if s != 'unknown_spouse':
                    self.value = self.window.get_object(s).getAttribute('Name')
                    break
        else:
            self.value = 'Unknown Spouse'

        self.setCurrentIndex(list(self.item_list.keys()).index(self.value))

        self.currentIndexChanged.connect(self.newChoice)

    def newChoice(self):
        self.value = self.currentText()
        self.logger.log('Code', str(self.value) + ' was chosen as the spouse')

    def getSelectedSpouse(self):
        print('Selecting: ' + str(self.value))
        if self.value == 'Unknown Spouse':
            return None
        else:
            return self.window.get_object(self.item_list[self.value])


## Dialog box to choose gender for new person
class ChooseGenderDialog(QMessageBox):
    def __init__(self, *args, **kwargs):
        super(ChooseGenderDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('New Person')

        self.setText('New Person Gender?')

        male_button = QPushButton('Man')
        female_button = QPushButton('Woman')

        self.addButton(male_button, QMessageBox.ActionRole)
        self.addButton(female_button, QMessageBox.ActionRole)


class SearchBar(QWidget):
    def __init__(self, window, searchText):
        super().__init__()
        self.window = window
        self.logger = self.window.logger

        self.setLayout(QHBoxLayout())

        self.layout().addWidget(QLabel('Search:'))

        self.searchBar = QLineEdit(searchText)
        self.searchBar.setFixedWidth(250)
        self.searchBar.textChanged.connect(self.check_text)
        self.layout().addWidget(self.searchBar)

    ## Check Text(search)
    # Modify list of characters based on search text
    def check_text(self):
        text = self.searchBar.text().lower()

        count = 0
        for widget in self.window.widgets:
            if text in widget.info.lower():
                widget.show()
                count += 1
            else:
                widget.hide()

        self.logger.log('Code',  'Found ' + str(count) + ' instances of "' + text + '" in object list')


class AttributeWidget(QWidget):
    def __init__(self, window, editFlag, attribute, subject):
        super().__init__()
        self.window = window
        self.logger = self.window.logger

        self.subject = subject

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.info = subject.getAttribute(attribute)

        if editFlag:
            self.layout.addWidget(QLabel(str(attribute) + ':'))
            infoTextBox = QLineEdit(self.info)
            infoTextBox.setFixedWidth(160)

            self.logger.log('Code', 'Can edit ' + str(attribute) + ': ' + str(self.info), True)

            def updateInfo():
                self.info = infoTextBox.text()
                self.subject.updateAttribute(attribute, self.info)

                self.subject.setName()

                self.window.write_data()

            self.layout.addWidget(infoTextBox)
            infoTextBox.textChanged.connect(updateInfo)
        else:
            self.logger.log('Code', 'Displaying ' + str(attribute) + ': ' + str(self.info), True)
            self.layout.addWidget(QLabel(str(attribute) + ': ' + str(self.info)))

        self.layout.addStretch(1)

    def getData(self):
        return self.info


## Widget to manage connections between objects, including both display and editing
## Applicable connections:
#   - Father
#   - Mother

class ParentWidget(QWidget):
    def __init__(self, window, editFlag, connection, child):
        super().__init__()
        self.window = window
        self.logger = self.window.logger

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.child = child
        self.connection = connection
        parentID = self.child.getParents(self.connection)[0]

        if parentID is None:
            self.parent = None
        else:
            self.parent = self.window.get_object(parentID)

        if editFlag:
            if self.parent is None:
                addButton = QPushButton('Add')
                addButton.clicked.connect(self.addConnection)

                self.layout.addWidget(addButton)
                self.layout.addWidget(QLabel(str(self.connection) + ':'))

                self.logger.log('Code', 'Can add ' + str(self.connection), True)
            else:
                changeButton = QPushButton('Change')
                changeButton.clicked.connect(self.addConnection)
                self.layout.addWidget(changeButton)

                self.layout.addWidget(RemoveConnectionButton(self.window, self.child, self.parent))

                self.layout.addWidget(QLabel(str(self.connection) + ': ' + str(self.parent.getAttribute('Name'))))

                self.logger.log('Code', 'Can modify ' + str(self.connection) + ': {' + parentID + '}', True)
        else:
            if self.parent is None:
                self.layout.addWidget(QLabel(str(self.connection) + ': '))
            else:
                self.layout.addWidget(QLabel(str(self.connection) + ': '))
                self.layout.addWidget(ObjectLabel(self.window, self.parent, 'Linker Object'))

    def addConnection(self):
        self.window.write_data()
        self.window.page_factory('choose_object_list', {'Object Type': 'Person', 'Search Text': '', 'Subject': self.child, 'Connection': self.connection})


class EventWidget(QWidget):
    def __init__(self, window, edit, id, subject):
        super().__init__()
        self.window = window
        self.objectID = id
        self.subject = subject

        eventDetails = self.subject.getEvent(self.objectID)

        self.setLayout(QGridLayout())
        margin = 0
        self.layout().setContentsMargins(margin, margin, margin, margin)

        removeEvent = None

        if edit:
            self.date = QLineEdit(eventDetails['Date'])
            self.date.setFixedWidth(100)
            self.date.setAlignment(Qt.AlignCenter)
            self.date.textChanged.connect(self.updateText)

            self.content = QLineEdit(eventDetails['Content'])
            self.content.textChanged.connect(self.updateText)

            removeEvent = QPushButton('X')

        else:
            self.date = QLabel(eventDetails['Date'])
            self.date.setFixedWidth(75)
            self.date.setAlignment(Qt.AlignCenter)

            self.content = QLabel(eventDetails['Content'])
            self.content.setWordWrap(True)

        self.layout().addWidget(self.date, 0, 0)
        self.layout().addWidget(self.content, 0, 1)
        self.layout().setColumnStretch(1, 1)

        if removeEvent is not None:
            self.layout().addWidget(removeEvent, 0, 2)
            removeEvent.clicked.connect(self.removeEvent)

    def updateText(self):
        updatedDetails = {'Date': self.date.text(), 'Content': self.content.text()}
        self.subject.updateEvent(self.objectID, updatedDetails)
        self.window.write_data()

    def removeEvent(self):
        self.subject.removeEvent(self.objectID)

        self.window.write_data()
        if self.subject.getObjectType() == 'Person':
            self.window.page_factory('edit_person_page', {'Person': self.subject})
        elif self.subject.getObjectType() == 'Title':
            self.window.page_factory('edit_title_page', {'Title': self.subject})
        elif self.subject.getObjectType() == 'Place':
            self.window.page_factory('edit_place_page', {'Place': self.subject})
