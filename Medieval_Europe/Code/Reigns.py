import sys

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox, QVBoxLayout
from PyQt5.QtCore import *

from Medieval_Europe.Code.Widgets.Buttons import RemoveConnectionButton
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

        self.title = self.reign.getConnection('Title')  # The title associated with this reign
        self.ruler = self.reign.getConnection('Person')  # The ruler associated with this reign

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

            # Add widget to edit predecessor
            layout.addLayout(EditConnectedReignWidget(self.window, 'Predecessor', self.reign), 1, 0)

            # Create center layout of reign dates
            centerLayout = QHBoxLayout()

            centerLayout.addWidget(QLabel('\u25C0'))  ## Left Arrow

            reignVBox = QVBoxLayout()

            reignVBox.addWidget(AttributeWidget(self.window, True, 'Start Date', self.reign))
            reignVBox.addWidget(AttributeWidget(self.window, True, 'End Date', self.reign))

            centerLayout.addLayout(reignVBox)

            centerLayout.addWidget(QLabel('\u25b6'))  ## Right Arrow

            layout.addLayout(centerLayout, 1, 1)

            # Add widget to edit successor
            layout.addLayout(EditConnectedReignWidget(self.window, 'Successor', self.reign), 1, 2)

            juniorVBox = QVBoxLayout()
            juniorLabel = QLabel('Junior Reigns:')
            juniorLabel.setAlignment(Qt.AlignCenter)
            juniorVBox.addWidget(juniorLabel)

            for j in self.reign.mergedReigns['Junior']:
                juniorObject = self.window.get_object(j)

                self.logger.log('Code', 'Add ' + str(juniorObject.getConnection('Title').getName('Page Title')) + ' as junior reign', True)

                juniorHBox = QHBoxLayout()
                juniorHBox.addStretch(1)
                juniorHBox.addWidget(QLabel(juniorObject.getConnection('Title').getName('Page Title')))

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
                    juniorLayout.addWidget(ObjectLabel(self.window, seniorReign.getConnection('Title'), 'Page Title'))
                    juniorLayout.addWidget(QLabel(')'))
            else:
                targetObjectType = 'None'
                self.logger.log('Error', str(self.objectType) + ' is an invalid object type to display a reign for')

            subject = self.reign.getConnection(targetObjectType)
            self.logger.log('Code', 'Viewing reign of {' + subject.getID() + '}')
            label = ObjectLabel(self.window, subject, 'Page Title')

            labelLayout = QHBoxLayout()
            labelLayout.addStretch(1)
            labelLayout.addWidget(label)
            labelLayout.addLayout(juniorLayout)
            labelLayout.addStretch(1)

            layout.addLayout(labelLayout, 0, 0, 1, 3)  # add at row 0, column 0, and stretch over 1 rows, and 3 columns

            if self.reign.hasConnection('Predecessor'):  ## Only display the predecessor label if there is one
                predecessorObject = self.window.get_object(self.reign.getConnection('Predecessor'))
                self.logger.log('Code', 'Has predecessor: {' + predecessorObject.getID() + '}', True)

                layout.addLayout(DisplayConnectedReignWidget(self.window, 'Predecessor', predecessorObject), 1, 0, 2, 1)  # add at row 1, column 0, spans 2 rows and 1 column

            centerLayout = QHBoxLayout()
            centerLayout.addWidget(QLabel('\u25C0'))  ## Left Arrow
            centerLayout.addWidget(QLabel(self.reign.getDateString()))
            centerLayout.addWidget(QLabel('\u25b6'))  ## Right Arrow
            layout.addLayout(centerLayout, 1, 1)  # add at row 1, column 2

            if self.reign.hasConnection('Successor'):  ## Only display the successor label if there is one
                successorObject = self.window.get_object(self.reign.getConnection('Successor'))
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
                    title = reignObject.getConnection('Title')
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
    def __init__(self, window, subject):
        super().__init__('Merge')

        self.window = window
        self.subject = subject  # The reign that is looking for a senior reign

        self.seniorReigns = self.subject.getConnection('Person').seniorReigns

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.window.logger.log('Detailed', 'Clicked to find senior reign for {' + self.subject.getID() + '}')

            choose_params = {'Object Type': 'Reign', 'Object List': self.seniorReigns, 'Search Text': '', 'Subject': self.subject, 'Connection': 'Merge'}
            self.window.page_factory('choose_object_list', choose_params)

            return True
        return False


class UnmergeButton(QPushButton):
    def __init__(self, window, juniorReign):
        super(UnmergeButton, self).__init__('Unmerge')
        self.window = window
        self.juniorReign = juniorReign
        self.seniorReign = self.window.get_object(juniorReign.mergedReigns['Senior'])
        self.person = juniorReign.getConnection('Person')

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.window.logger.log('Code', 'Clicked to remove {' + self.juniorReign.getID() + '} as junior to {' + self.seniorReign.getID() + '}')
            self.juniorReign.unmerge(self.seniorReign)

            self.window.page_factory('edit_person_page', {'Person': self.person})

            return True
        return False


class EditConnectedReignWidget(QHBoxLayout):
    def __init__(self, window, connection, reign):
        super().__init__()
        self.window = window

        self.reign = reign

        title = self.reign.getConnection('Title')
        self.connectionID = self.reign.getConnection(connection)

        modifyVBox = QVBoxLayout()
        labelHBox = QHBoxLayout()

        if connection == 'Predecessor':
            opp_connect = 'Successor'

            self.addStretch(1)
            self.addLayout(modifyVBox)
            self.addLayout(labelHBox)

        elif connection == 'Successor':
            opp_connect = 'Predecessor'

            self.addLayout(labelHBox)
            self.addLayout(modifyVBox)
            self.addStretch(1)

        else:
            opp_connect = 'None'
            self.window.logger.log('Error', str(connection) + ' is not a valid connection for a reign.')

        chooseConnectionButton = QPushButton()

        potential_connections = {}

        for r in title.reignDict:
            potential_reign = self.window.get_object(r)
            if r != self.reign.getID() and not potential_reign.hasConnection(opp_connect):
                potential_connections.update({r: potential_reign})

        # Get potential predecessor reigns from this title's successor
        if title.getConnection(connection) is not None:
            suc_title = self.window.get_object(title.getConnection(connection))

            for r in suc_title.reignDict:
                potential_reign = self.window.get_object(r)
                if r != self.reign.getID() and not potential_reign.hasConnection(opp_connect):
                    potential_connections.update({r: potential_reign})

        choose_params = {'Object Type': 'Reign', 'Object List': potential_connections, 'Search Text': '', 'Subject': self.reign, 'Connection': connection}
        chooseConnectionButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', choose_params))

        modifyVBox.addWidget(chooseConnectionButton)

        ## No Connected Reign
        if self.connectionID is None:
            chooseConnectionButton.setText('Add')
        else:
            chooseConnectionButton.setText('Change')
            modifyVBox.addWidget(RemoveConnectionButton(self.window, self.reign, self.window.get_object(self.connectionID)))
            labelHBox.addWidget(QLabel(self.window.get_object(self.connectionID).getName('Linker Object')))


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
        self.title = self.reign.getConnection('Title')
        self.ruler = self.reign.getConnection('Person')

        self.addStretch(1)
        self.addWidget(QLabel(self.title.getFullRulerTitle(self.ruler.gender)))

        removeButton = QPushButton('Remove')
        removeButton.clicked.connect(self.removeReign)
        self.addWidget(removeButton)

        mergeButton = MergeButton(self.window, self.reign)
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

            if juniorReign.hasConnection('Predecessor'):
                predecessorObject = self.window.get_object(juniorReign.getConnection('Predecessor'))
                predecessorObject.removeConnection('Successor')

                if predecessorObject.isJunior:
                    predecessorObject.unmerge(self.window.get_object(predecessorObject.mergedReigns['Senior']))

            if juniorReign.hasConnection('Successor'):
                successorObject = self.window.get_object(juniorReign.getConnection('Successor'))
                successorObject.removeConnection('Predecessor')

                if successorObject.isJunior:
                    successorObject.unmerge(self.window.get_object(successorObject.mergedReigns['Senior']))

        if self.reign.hasConnection('Predecessor'):
            predecessorObject = self.window.get_object(self.reign.getConnection('Predecessor'))
            predecessorObject.removeConnection('Successor')

            if predecessorObject.isJunior:
                predecessorObject.unmerge(self.window.get_object(predecessorObject.mergedReigns['Senior']))

        if self.reign.hasConnection('Successor'):
            successorObject = self.window.get_object(self.reign.getConnection('Successor'))
            successorObject.removeConnection('Predecessor')

            if successorObject.isJunior:
                successorObject.unmerge(self.window.get_object(successorObject.mergedReigns['Senior']))

        self.window.page_factory('edit_person_page', {'Person': self.ruler})
