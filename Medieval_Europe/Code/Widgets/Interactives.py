"""
Created on Aug 1, 2022

@author: kairom13
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Medieval_Europe.Code.Widgets.Displays import ObjectLabel
from Medieval_Europe.Code.Widgets.Buttons import RemoveConnectionButton, UnmergeButton


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

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel('Search:'))

        self.searchBar = QLineEdit(searchText)
        self.searchBar.setFixedWidth(250)
        self.searchBar.textChanged.connect(self.check_text)
        self.layout.addWidget(self.searchBar)

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

            self.logger.log('Code', 'Can edit ' + str(attribute) + ': ' + str(self.info))

            def updateInfo():
                self.info = infoTextBox.text()
                self.subject.updateAttribute(attribute, self.info)

                self.subject.setName()

                self.window.write_data()

            self.layout.addWidget(infoTextBox)
            infoTextBox.textChanged.connect(updateInfo)
        else:
            self.logger.log('Code', 'Displaying ' + str(attribute) + ': ' + str(self.info))
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
        parentID = self.child.getParent(self.connection)

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

                self.logger.log('Code', 'Can add ' + str(self.connection))
            else:
                changeButton = QPushButton('Change')
                changeButton.clicked.connect(self.addConnection)
                self.layout.addWidget(changeButton)

                self.layout.addWidget(RemoveConnectionButton(self.window, self.child, self.parent))

                self.layout.addWidget(QLabel(str(self.connection) + ': ' + str(self.parent.getAttribute('Name'))))

                self.logger.log('Code', 'Can modify ' + str(self.connection) + ': {' + parentID + '}')
        else:
            if self.parent is None:
                self.layout.addWidget(QLabel(str(self.connection) + ': '))
            else:
                self.layout.addWidget(QLabel(str(self.connection) + ': '))
                self.layout.addWidget(ObjectLabel(self.window, self.parent, 'Person', -1))

    def addConnection(self):
        self.window.write_data()
        self.window.page_factory('choose_object_list', {'Object Type': 'Person', 'Search Text': '', 'Subject': self.child, 'Connection': self.connection})


class ReignConnectionWidget(QWidget):
    def __init__(self, window, editFlag, connection, reignObject):
        super().__init__()
        self.window = window

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.reign = reignObject
        self.connection = connection
        connectedReignID = self.reign.getConnectedReign(self.connection)

        if connectedReignID is None:
            self.connectedReign = None
        else:
            self.connectedReign = self.window.get_object(connectedReignID)

        if editFlag:
            if self.connectedReign is None:
                addButton = QPushButton('Add')
                addButton.clicked.connect(self.addConnection)

                self.layout.addWidget(addButton)
                self.layout.addWidget(QLabel(str(self.connection) + ':'))
            else:
                changeButton = QPushButton('Change')
                changeButton.clicked.connect(self.addConnection)
                self.layout.addWidget(changeButton)

                self.layout.addWidget(RemoveConnectionButton(self.window, self.reign, self.parent))

                self.layout.addWidget(QLabel(str(self.connection) + ': ' + str(self.connectedReign.getAttribute('Name'))))
        else:
            if self.parent is None:
                self.layout.addWidget(QLabel(str(self.connection) + ': '))
            else:
                self.layout.addWidget(QLabel(str(self.connection) + ': '))
                self.layout.addWidget(ObjectLabel(self.window, self.connectedReign, 'Person', -1))

    def addConnection(self):
        self.window.write_data()
        self.window.page_factory('display_title_page',
                                 {'Title': self.reign.getConnectedReign('Title'), 'Page Type': 'Choose', 'Person': self.reign.getConnectedReign('Ruler'), 'Connection': self.connection,
                                  'Reign': self.reign})


## Widget for info of a given reign.
# Displays one reign
# Header depends on object type
# Title: Ruler
# Person: Full Title

## Expected Parameters:
# Window
# Person List
# Person
# Title
# Edit
# Personal Info (to flow through)

class ReignWidget(QWidget):
    def __init__(self, parameters):
        super(ReignWidget, self).__init__()

        self.window = parameters['Window']
        self.reign = parameters['Reign']  ## The reign object being displayed
        self.edit = parameters['Edit']  ## Whether the reign is being edited

        self.objectType = parameters['Object Type']

        self.logger = parameters['Logger']

        # Layout
        # - 3 Rows
        #   First Row (centered HBoxLayout)
        #   - Name
        #   - "Junior to <senior reign>"
        #   Second Row (3 columns)
        #   - Predecessor (if applicable); col 0
        #   - left arrow; col 1
        #   - reign date; col 1
        #   - right arrow; col 1
        #   - Successor(if applicable); col 2
        #   Third Row (centered VBoxLayout)
        #   - Label: "Junior Reigns:"
        #   - List of junior reigns

        layout = QGridLayout()  # Layout will have 2 row and 7 columns
        layout.setSpacing(10)

        # column_widths = [4, 4, 1, 7, 1, 4, 4]
        # for c in range(len(column_widths)):
        #     layout.setColumnStretch(c, column_widths[c])  # column c is stretched to column_widths[c]

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)

        ## Layout for editing the given title
        # If person page:
        #    Display title as label
        #        Button for choosing or removing title
        #    For each reign:
        #        Button for getting predecessor or successor
        #        Text boxes for start and end dates

        title = self.reign.getConnectedReign('Title')  # The title associated with this reign
        ruler = self.reign.getConnectedReign('Ruler')  # The ruler associated with this reign

        if self.edit:
            if title.getID() in self.window.objectLists['Title']:
                self.logger.log('Code', 'Can edit reign: {' + self.reign.getID() + '}')

                ## Make Title Label
                titleLabel = QLabel(title.getFullRulerTitle(ruler.gender))
                removeButton = QPushButton('Remove')

                def removeReign():
                    ## Remove this reign from the title's list
                    ## Remove this reign from the person's list
                    ## Remove this reign from the global reign list
                    ## Remove all junior reigns as well
                    ## Remove this reign from the predecessor or successor, if applicable

                    globalReignList = self.window.objectLists['Reign']

                    self.logger.log('Code', 'Removing ' + str(self.reign.getID()))
                    title.removeReign(self.reign.getID())
                    ruler.removeReign(self.reign.getID())

                    globalReignList.pop(self.reign.getID())

                    for j in self.reign.mergedReigns['Junior']:
                        juniorReign = self.window.get_object(j)
                        self.logger.log('Code', 'Removing ' + str(juniorReign.getID()))

                        title.removeReign(juniorReign.getID())
                        ruler.removeReign(juniorReign.getID())

                        globalReignList.pop(juniorReign.getID())

                        if juniorReign.hasConnectedReign('Predecessor'):
                            predecessorObject = self.window.get_object(juniorReign.getConnectedReign('Predecessor'))
                            predecessorObject.removeConnectedReign('Successor')

                        if juniorReign.hasConnectedReign('Successor'):
                            successorObject = self.window.get_object(juniorReign.getConnectedReign('Successor'))
                            successorObject.removeConnectedReign('Predecessor')

                    # self.lineEditDict.pop(self.reign.id)

                    if self.reign.hasConnectedReign('Predecessor'):
                        predecessorObject = self.window.get_object(self.reign.getConnectedReign('Predecessor'))
                        predecessorObject.removeConnectedReign('Successor')

                    if self.reign.hasConnectedReign('Successor'):
                        successorObject = self.window.get_object(self.reign.getConnectedReign('Successor'))
                        successorObject.removeConnectedReign('Predecessor')

                    self.window.page_factory('edit_person_page', {'Person': ruler})

                removeButton.clicked.connect(removeReign)

                title_layout = QHBoxLayout()
                title_layout.setSpacing(10)

                title_layout.addStretch(1)
                title_layout.addWidget(titleLabel)
                title_layout.addWidget(removeButton)

                ## Merge reign
                ## A button to merge this reign with another reign with the same ruler
                ## Requirements to be a senior reign:
                #   - Must not be the current reign
                #   - Must not be a junior reign
                #   - Must not have a different predecessor/successor
                #       i.e. must already have the same predecessor/successor or have none

                ## Merging only allowed if there is more than one senior reign

                ## When merging
                #   If already have predecessor/successor, set as junior and add to senior's junior
                #   If no predecessor/successor, set as junior, add to senior's junior, set senior's predecessor/successor as junior's predecessor/successor, and propagate
                #   Include toggle to propagate

                ## When unmerging
                #   Go to list of junior reigns
                #   Choose reign to unmerge
                #   Include toggle to propagate


                ## If merged all of the data (dates, predecessor, successor) are merged with the target reign
                ##    This means that both the predecessor and the successor must have the junior title
                ##    If a junior title-reign does not exist for either predecessor or successor, one will be created and linked
                ## The target reign is the main reign and this reign is included in the list
                ## Only applicable when there is more than one reign for the person
                ##    Includes when two reigns of the same title, however when merging, only distinct titles are allowed
                ##    Pseudo bug but a bit annoying to change
                ## When clicked, choose from the list of other reigns for this person
                ## When editing, the list includes a button to unmerge, which transforms it back into the original configuration
                ##               the list will also include a button to remove, which deletes the reign entirely
                ## When setting a successor (or when the senior title sets this senior reign as it's predecessor),
                ##    the new reign includes the merged feature (which can be then unmerged if necessary)
                ## The display of the junior title(s) will still show the reign as separate
                ##    (i.e. the Kings of France as Counts of Auxerre)

                if len(ruler.reignList) > 1:
                    mergeButton = QPushButton('Merge')
                    mergeButton.setEnabled(False)
                    mergeButton.setToolTip('Merging to be added in a later update')

                    potential_object_list = {}

                    for r in ruler.reignList:
                        potential_reign = self.window.get_object(r)
                        if r != self.reign.getID() and not potential_reign.isJunior:
                            potential_object_list.update({r: potential_reign})

                    #mergeButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Reign', 'Object List': potential_object_list, 'Search Text': '', 'Subject': self.reign, 'Connection': 'Merge'}))

                    title_layout.addWidget(mergeButton)

                ## Check box for marking as primary reign
                def checkedPrimary(checked):
                    if checked > 0:
                        self.reign.setPrimary(True)
                    else:
                        self.reign.setPrimary(False)

                    self.window.page_factory('edit_person_page', {'Person': ruler})

                if len(ruler.reignList) == 1:
                    #print(self.person.getName() + ' has only one reign')
                    self.reign.setPrimary(True)

                primaryCheckBox = QCheckBox('Primary')
                primaryCheckBox.setChecked(self.reign.isPrimary)
                if self.reign.isPrimary:
                    self.logger.log('Code', 'This is the primary reign')
                if ruler.primary_title('Has') and not self.reign.isPrimary:
                    primaryCheckBox.setEnabled(False)

                primaryCheckBox.stateChanged.connect(checkedPrimary)

                title_layout.addWidget(primaryCheckBox)

                title_layout.addStretch(1)

                layout.addLayout(title_layout, 0, 0, 1, 3)  # add at row 0, column 0, and stretch over 1 rows, and 3 columns

                ## Make Reign "widget"
                preLabelLayout = QHBoxLayout()
                preLabelLayout.addStretch(1)

                preButtonVBox = QVBoxLayout()

                addPreButton = QPushButton('')
                preButtonVBox.addWidget(addPreButton)

                if self.reign.hasConnectedReign('Predecessor'):  ## Use change and remove buttons when predecessor exists
                    predecessorObject = self.window.get_object(self.reign.getConnectedReign('Predecessor'))
                    self.logger.log('Code', 'Reign has predecessor in: ' + predecessorObject.getConnectedReign('Ruler').getName())

                    addPreButton.setText('Change')

                    preButtonVBox.addWidget(RemoveConnectionButton(self.window, self.reign, predecessorObject))
                    preLabelLayout.addLayout(preButtonVBox)

                    predecessorLabel = QLabel(predecessorObject.getConnectedReign('Ruler').getAttribute('Name'))
                    preLabelLayout.addWidget(predecessorLabel)

                else:  ## Use Add button when no existing predecessor
                    self.logger.log('Code', 'Reign has no predecessor')
                    addPreButton.setText('Add')
                    preLabelLayout.addLayout(preButtonVBox)

                valid_pre = {}

                for r in title.reignDict:
                    potential_reign = self.window.get_object(r)
                    if r != self.reign.getID() and not potential_reign.hasConnectedReign('Successor'):
                        valid_pre.update({r: potential_reign})

                addPreButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Reign', 'Object List': valid_pre, 'Search Text': '', 'Subject': self.reign, 'Connection': 'Predecessor'}))
                layout.addLayout(preLabelLayout, 1, 0)

                centerLayout = QHBoxLayout()

                centerLayout.addWidget(QLabel('\u25C0'))  ## Left Arrow

                reignVBox = QVBoxLayout()

                reignVBox.addWidget(AttributeWidget(self.window, True, 'Start Date', self.reign))
                reignVBox.addWidget(AttributeWidget(self.window, True, 'End Date', self.reign))

                centerLayout.addLayout(reignVBox)

                centerLayout.addWidget(QLabel('\u25b6'))  ## Right Arrow

                layout.addLayout(centerLayout, 1, 1)

                sucLabelLayout = QHBoxLayout()
                sucButtonVBox = QVBoxLayout()

                addSucButton = QPushButton('')
                sucButtonVBox.addWidget(addSucButton)

                if self.reign.hasConnectedReign('Successor'):  ## Use change and remove buttons when successor exists
                    successorObject = self.window.get_object(self.reign.getConnectedReign('Successor'))
                    self.logger.log('Code', 'Reign has successor in: ' + successorObject.getConnectedReign('Ruler').getName())

                    successorLabel = QLabel(successorObject.getConnectedReign('Ruler').getAttribute('Name'))
                    sucLabelLayout.addWidget(successorLabel)

                    addSucButton.setText('Change')

                    sucButtonVBox.addWidget(RemoveConnectionButton(self.window, self.reign, successorObject))
                    sucLabelLayout.addLayout(sucButtonVBox)

                else:  ## Use Add button when no existing successor
                    self.logger.log('Code', 'Reign has no Successor')
                    addSucButton.setText('Add')
                    sucLabelLayout.addLayout(sucButtonVBox)

                valid_suc = {}

                for r in title.reignDict:
                    potential_reign = self.window.get_object(r)
                    if r != self.reign.getID() and not potential_reign.hasConnectedReign('Predecessor'):
                        valid_suc.update({r: potential_reign})

                addSucButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Reign', 'Object List': valid_suc, 'Search Text': '', 'Subject': self.reign, 'Connection': 'Successor'}))

                sucLabelLayout.addStretch(1)
                layout.addLayout(sucLabelLayout, 1, 2)

                juniorVBox = QVBoxLayout()
                juniorLabel = QLabel('Junior Reigns:')
                juniorLabel.setAlignment(Qt.AlignCenter)
                juniorVBox.addWidget(juniorLabel)

                for j in self.reign.mergedReigns['Junior']:
                    juniorObject = self.window.get_object(j)

                    self.logger.log('Code', 'Add ' + str(juniorObject.getConnectedReign('Title').getName()) + ' as junior reign')

                    juniorHBox = QHBoxLayout()
                    juniorHBox.addStretch(1)
                    juniorHBox.addWidget(QLabel(juniorObject.getConnectedReign('Title').getName()))

                    unmergeButton = UnmergeButton(self.window, juniorObject)

                    juniorHBox.addWidget(unmergeButton)
                    juniorHBox.addStretch(1)

                    juniorVBox.addLayout(juniorHBox)

                layout.addLayout(juniorVBox, 2, 1)

            else:
                self.logger.log('Code', 'Can add new reign')
                addButton = QPushButton('Add')
                addButton.layout = QHBoxLayout()
                addButton.layout.addStretch(1)
                addButton.layout.addWidget(addButton)
                addButton.layout.addStretch(1)

                # Choose title to add from list
                addButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Title', 'Search Text': '', 'Subject': ruler, 'Connection': 'Title'}))

                # self.vbox.addLayout(addButton.layout)

        else:
            ## Widget for each section of reigns
            # If person page:
            #    Title Name
            #    list of reigns
            #
            # If title page:
            #    Person Name
            #    their reign

            if self.objectType == 'Person':
                self.logger.log('Code', 'Viewing Reign as part of ' + str(ruler.getAttribute('Name')))
                titleLabel = ObjectLabel(self.window, title.getID(), 'Title', ruler.gender)

                titleLayout = QHBoxLayout()
                titleLayout.addStretch(1)
                # titleLayout.addWidget(QLabel('#' + str(self.reign.order)))
                titleLayout.addWidget(titleLabel)
                titleLayout.addStretch(1)

                layout.addLayout(titleLayout, 0, 0, 1, 3)  # add at row 0, column 0, and stretch over 1 rows, and 3 columns

            elif self.objectType == 'Title':
                self.logger.log('Code', 'Viewing Reign as part of ' + str(title.getFullRealmTitle()))

                personLabel = ObjectLabel(self.window, ruler.getID(), 'Person')

                personLabel.layout = QHBoxLayout()
                personLabel.layout.setSpacing(10)
                personLabel.layout.addStretch(1)
                personLabel.layout.addWidget(personLabel)

                if self.reign.isJunior:
                    seniorReign = self.window.get_object(self.reign.mergedReigns['Senior'])
                    personLabel.layout.addWidget(QLabel('(Junior to ' + str(seniorReign.getConnectedReign('Title').getName() + ')')))
                personLabel.layout.addStretch(1)

                layout.addLayout(personLabel.layout, 0, 0, 1, 3)  # add at row 0, column 0, and stretch over 1 rows, and 3 columns

            if self.reign.hasConnectedReign('Predecessor'):  ## Only display the predecessor label if there is one
                predecessorObject = self.window.get_object(self.reign.getConnectedReign('Predecessor'))
                self.logger.log('Code', 'Predecessor: ' + predecessorObject.getConnectedReign('Ruler').getName())

                preLabel = QHBoxLayout()
                preLabel.addStretch(1)
                preLabel.addWidget(ObjectLabel(self.window, predecessorObject.getConnectedReign('Ruler').getID(), 'Person'))
                layout.addLayout(preLabel, 1, 0) # add at row 1, column 0

            centerLayout = QHBoxLayout()
            centerLayout.addWidget(QLabel('\u25C0'))  ## Left Arrow
            centerLayout.addWidget(QLabel(self.reign.getDateString()))
            centerLayout.addWidget(QLabel('\u25b6'))  ## Right Arrow
            layout.addLayout(centerLayout, 1, 1)  # add at row 1, column 1

            if self.reign.hasConnectedReign('Successor'):  ## Only display the successor label if there is one
                successorObject = self.window.get_object(self.reign.getConnectedReign('Successor'))
                self.logger.log('Code', 'Successor: ' + successorObject.getConnectedReign('Ruler').getName())

                sucLabel = QHBoxLayout()
                sucLabel.addWidget(ObjectLabel(self.window, successorObject.getConnectedReign('Ruler').getID(), 'Person'))
                sucLabel.addStretch(1)
                layout.addLayout(sucLabel, 1, 2)  # add at row 1, column 2

            if self.objectType == 'Person':
                juniorVBox = QVBoxLayout()
                juniorVBox.setAlignment(Qt.AlignCenter)

                juniorLabel = QLabel('Junior Reigns:')
                juniorLabel.setAlignment(Qt.AlignCenter)
                juniorVBox.addWidget(juniorLabel)

                for j in self.reign.mergedReigns['Junior']:
                    reignObject = self.window.get_object(j)
                    self.logger.log('Code', 'Add ' + str(reignObject.getConnectedReign('Title').getName()) + ' as junior reign')
                    juniorVBox.addWidget(ObjectLabel(self.window, reignObject.getConnectedReign('Title').getID(), 'Title', ruler.gender), alignment=Qt.AlignHCenter)

                layout.addLayout(juniorVBox, 2, 1)

        self.setLayout(layout)

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
            self.date.textChanged.connect(lambda: self.updateText(self.date))

            self.content = QLineEdit(eventDetails['Content'])
            self.content.textChanged.connect(lambda: self.updateText(self.content))

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

    def updateText(self, obj):
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

