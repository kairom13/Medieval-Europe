import sys

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox, QVBoxLayout
from PyQt5.QtCore import *

from Medieval_Europe.Code.Widgets.Buttons import RemoveConnectionButton, UnmergeButton
from Medieval_Europe.Code.Widgets.Displays import ObjectLabel
from Medieval_Europe.Code.Widgets.Interactives import AttributeWidget

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

        self.title = self.reign.getConnectedReign('Title')  # The title associated with this reign
        self.ruler = self.reign.getConnectedReign('Person')  # The ruler associated with this reign

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

        if self.edit:
            self.logger.log('Code', 'Editing reign as ' + self.title.getFullRulerTitle(self.ruler.gender))

            layout.addLayout(EditTitleWidget(self.window, self.reign), 0, 0, 1, 3)  # add at row 0, column 0, and stretch over 1 rows, and 3 columns

            ## Make Reign "widget"
            preLabelLayout = QHBoxLayout()
            preLabelLayout.addStretch(1)

            preButtonVBox = QVBoxLayout()

            addPreButton = QPushButton('')
            preButtonVBox.addWidget(addPreButton)

            if self.reign.hasConnectedReign('Predecessor'):  ## Use change and remove buttons when predecessor exists
                predecessorObject = self.window.get_object(self.reign.getConnectedReign('Predecessor'))
                self.logger.log('Code', 'Reign has predecessor: ' + predecessorObject.getConnectedReign('Person').getName(), True)

                addPreButton.setText('Change')

                preButtonVBox.addWidget(RemoveConnectionButton(self.window, self.reign, predecessorObject))
                preLabelLayout.addLayout(preButtonVBox)

                predecessorLabel = QLabel(predecessorObject.getConnectedReign('Person').getAttribute('Name'))
                preLabelLayout.addWidget(predecessorLabel)

            else:  ## Use Add button when no existing predecessor
                self.logger.log('Code', 'Reign has no predecessor', True)
                addPreButton.setText('Add')
                preLabelLayout.addLayout(preButtonVBox)

            valid_pre = {}

            for r in self.title.reignDict:
                potential_reign = self.window.get_object(r)
                if r != self.reign.getID() and not potential_reign.hasConnectedReign('Successor'):
                    valid_pre.update({r: potential_reign})

            # Get potential predecessor reigns from this title's successor
            if self.title.predecessor is not None:
                pre_title = self.window.get_object(self.title.predecessor)

                for r in pre_title.reignDict:
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
                self.logger.log('Code', 'Reign has successor: ' + successorObject.getConnectedReign('Person').getName(), True)

                #successorLabel = QLabel(successorObject.getConnectedReign('Person').getAttribute('Name'))
                successorLabel = QLabel(successorObject.getName('Linker Object'))
                sucLabelLayout.addWidget(successorLabel)

                addSucButton.setText('Change')

                sucButtonVBox.addWidget(RemoveConnectionButton(self.window, self.reign, successorObject))
                sucLabelLayout.addLayout(sucButtonVBox)

            else:  ## Use Add button when no existing successor
                self.logger.log('Code', 'Reign has no Successor', True)
                addSucButton.setText('Add')
                sucLabelLayout.addLayout(sucButtonVBox)

            valid_suc = {}

            for r in self.title.reignDict:
                potential_reign = self.window.get_object(r)
                if r != self.reign.getID() and not potential_reign.hasConnectedReign('Predecessor'):
                    valid_suc.update({r: potential_reign})

            # Get potential predecessor reigns from this title's successor
            if self.title.successor is not None:
                suc_title = self.window.get_object(self.title.successor)

                for r in suc_title.reignDict:
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

                self.logger.log('Code', 'Add ' + str(juniorObject.getConnectedReign('Title').getName('Page Title')) + ' as junior reign', True)

                juniorHBox = QHBoxLayout()
                juniorHBox.addStretch(1)
                juniorHBox.addWidget(QLabel(juniorObject.getConnectedReign('Title').getName('Page Title')))

                unmergeButton = UnmergeButton(self.window, juniorObject)
                unmergeButton.setEnabled(False)
                unmergeButton.setToolTip('Merge functionality to be added in a later update')

                juniorHBox.addWidget(unmergeButton)
                juniorHBox.addStretch(1)

                juniorVBox.addLayout(juniorHBox)

            layout.addLayout(juniorVBox, 2, 1)

        else:
            ## Widget for each section of reigns
            # If person page:
            #    Title Name
            #    list of reigns
            #
            # If title page:
            #    Person Name
            #    their reign

            juniorLayout = QHBoxLayout()
            juniorLayout.setSpacing(0)

            if self.objectType == 'Person':
                targetObjectType = 'Title'
            elif self.objectType == 'Title':
                targetObjectType = 'Person'

                if self.reign.isJunior:
                    seniorReign = self.window.get_object(self.reign.mergedReigns['Senior'])
                    self.logger.log('Code', 'Is junior to {' + seniorReign.getID() + '}', True)
                    juniorLayout.addWidget(QLabel('(Junior to '))
                    juniorLayout.addWidget(ObjectLabel(self.window, seniorReign.getConnectedReign('Title'), 'Page Title'))
                    juniorLayout.addWidget(QLabel(')'))
            else:
                self.logger.log('Error', str(self.objectType) + ' is an invalid object type to display a reign for')

            subject = self.reign.getConnectedReign(targetObjectType)
            self.logger.log('Code', 'Viewing reign of {' + subject.getID() + '}')
            label = ObjectLabel(self.window, subject, 'Page Title')

            labelLayout = QHBoxLayout()
            labelLayout.addStretch(1)
            labelLayout.addWidget(label)
            labelLayout.addLayout(juniorLayout)
            labelLayout.addStretch(1)

            layout.addLayout(labelLayout, 0, 0, 1, 3)  # add at row 0, column 0, and stretch over 1 rows, and 3 columns

            if self.reign.hasConnectedReign('Predecessor'):  ## Only display the predecessor label if there is one
                predecessorObject = self.window.get_object(self.reign.getConnectedReign('Predecessor'))
                self.logger.log('Code', 'Has predecessor: {' + predecessorObject.getID() + '}', True)
                #self.logger.log('Code', 'Predecessor: ' + predecessorObject.getConnectedReign('Person').getName())

                layout.addLayout(DisplayConnectedReignWidget(self.window, 'Predecessor', predecessorObject), 1, 0, 2, 1)  # add at row 1, column 0, spans 2 rows and 1 column

            centerLayout = QHBoxLayout()
            centerLayout.addWidget(QLabel('\u25C0'))  ## Left Arrow
            centerLayout.addWidget(QLabel(self.reign.getDateString()))
            centerLayout.addWidget(QLabel('\u25b6'))  ## Right Arrow
            layout.addLayout(centerLayout, 1, 1)  # add at row 1, column 2

            if self.reign.hasConnectedReign('Successor'):  ## Only display the successor label if there is one
                successorObject = self.window.get_object(self.reign.getConnectedReign('Successor'))
                self.logger.log('Code', 'Has successor: {' + successorObject.getID() + '}', True)

                layout.addLayout(DisplayConnectedReignWidget(self.window, 'Successor', successorObject), 1, 2, 2, 1)  # add at row 0, column 2, spans 2 rows and 1 column

            self.logger.log('Code', 'Date of Reign: ' + self.reign.getDateString(), True)

            if self.objectType == 'Person':
                juniorVBox = QVBoxLayout()
                juniorVBox.setAlignment(Qt.AlignCenter)

                juniorLabel = QLabel('Junior Reigns:')
                juniorLabel.setAlignment(Qt.AlignCenter)
                layout.addWidget(juniorLabel, 2, 1)

                for j in self.reign.mergedReigns['Junior']:
                    reignObject = self.window.get_object(j)
                    title = reignObject.getConnectedReign('Title')
                    self.logger.log('Code', 'Add {' + title.getID() + '} as junior reign', True)
                    juniorVBox.addWidget(ObjectLabel(self.window, title, 'Page Title'))

                layout.addLayout(juniorVBox, 3, 1)

        self.setLayout(layout)


class DisplayConnectedReignWidget(QHBoxLayout):
    def __init__(self, window, connection, subject):
        super().__init__()

        midLayout = QVBoxLayout()
        if connection == 'Predecessor':
            self.addStretch(1)
            midLayout.addWidget(ObjectLabel(window, subject, 'Linker Object'))
            midLayout.addStretch(1)
            self.addLayout(midLayout)
        elif connection == 'Successor':
            midLayout.addWidget(ObjectLabel(window, subject, 'Linker Object'))
            midLayout.addStretch(1)
            self.addLayout(midLayout)
            self.addStretch(1)
        else:
            window.logger.log('Error', str(connection) + ' is an invalid connection to create a label for')


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
class MergeButton(QPushButton):
    def __init__(self, window, edit, connection, subject):
        super().__init__()


class EditConnectedReignWidget(QHBoxLayout):
    def __init__(self, window, connection, reign):
        super().__init__()
        self.window = window

        self.reign = reign

        title = self.reign.getConnectedReign('Title')

        if connection == 'Predecessor':
            opp_connect = 'Successor'
        elif connection == 'Successor':
            opp_connect = 'Predecessor'
        else:
            self.window.logger.log('Error', str(connection) + ' is not a valid connection for a reign.')

        self.connectedReign = self.reign.getConnectedReign(connection)

        ## No Connected Reign
        if self.connectedReign is None:
            chooseConnectionButton = QPushButton('Add')

        else:
            chooseConnectionButton = QPushButton('Change')

        potential_connections = {}

        for r in title.reignDict:
            potential_reign = self.window.get_object(r)
            if r != self.reign.getID() and not potential_reign.hasConnectedReign(opp_connect):
                potential_connections.update({r: potential_reign})

        # Get potential predecessor reigns from this title's successor
        if title.getConnection(connection) is not None:
            suc_title = self.window.get_object(title.getConnection(connection))

            for r in suc_title.reignDict:
                potential_reign = self.window.get_object(r)
                if r != self.reign.getID() and not potential_reign.hasConnectedReign(opp_connect):
                    potential_connections.update({r: potential_reign})

        choose_params = {'Object Type': 'Reign', 'Object List': potential_connections, 'Search Text': '', 'Subject': self.reign, 'Connection': connection}
        chooseConnectionButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', choose_params))


# Layout for editing the title for a reign
# 4 components:
# - Title Name
# - Remove Button
# - Merge Button
# - Primary Checkbox
class EditTitleWidget(QHBoxLayout):
    def __init__(self, window, reign):
        super().__init__()
        self.window = window
        self.logger = self.window.logger

        self.reign = reign
        self.title = self.reign.getConnectedReign('Title')
        self.ruler = self.reign.getConnectedReign('Person')

        self.addStretch(1)
        self.addWidget(QLabel(self.title.getFullRulerTitle(self.ruler.gender)))

        removeButton = QPushButton('Remove')
        removeButton.clicked.connect(self.removeReign)
        self.addWidget(removeButton)

        mergeButton = QPushButton('Merge')
        mergeButton.setEnabled(False)
        mergeButton.setToolTip('Merge functionality to be added in a later update')
        self.addWidget(mergeButton)

        ## Check box for marking as primary reign
        def checkedPrimary(checked):
            if checked > 0:
                self.reign.setPrimary(True)
            else:
                self.reign.setPrimary(False)

            self.window.page_factory('edit_person_page', {'Person': self.ruler})

        if len(self.ruler.reignList) == 1:
            # print(self.person.getName() + ' has only one reign')
            self.reign.setPrimary(True)

        primaryCheckBox = QCheckBox('Primary')
        primaryCheckBox.setChecked(self.reign.isPrimary)
        if self.reign.isPrimary:
            self.logger.log('Code', 'This is the primary reign', True)
        if self.ruler.primary_title('Has') and not self.reign.isPrimary:
            primaryCheckBox.setEnabled(False)

        primaryCheckBox.stateChanged.connect(checkedPrimary)

        self.addWidget(primaryCheckBox)
        self.addStretch(1)

    def removeReign(self):
        ## Remove this reign from the title's list
        ## Remove this reign from the person's list
        ## Remove this reign from the global reign list
        ## Remove all junior reigns as well
        ## Remove this reign from the predecessor or successor, if applicable

        globalReignList = self.window.objectLists['Reign']

        self.logger.log('Code', 'Removing ' + str(self.reign.getID()))
        self.title.removeReign(self.reign.getID())
        self.ruler.removeReign(self.reign.getID())

        globalReignList.pop(self.reign.getID())

        for j in self.reign.mergedReigns['Junior']:
            juniorReign = self.window.get_object(j)
            self.logger.log('Code', 'Removing ' + str(juniorReign.getID()))

            self.title.removeReign(juniorReign.getID())
            self.ruler.removeReign(juniorReign.getID())

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

        self.window.page_factory('edit_person_page', {'Person': self.ruler})
