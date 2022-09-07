"""
Created on Jul 22, 2020

@author: kairom13
"""

import sys

from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QApplication

from Medieval_Europe.Code.CustomObjects import *
from Medieval_Europe.Code.DisplayData import DisplayData
from Medieval_Europe.Code.Widgets.Interactives import ChooseGenderDialog
from Medieval_Europe.Code.page_generator import PageGenerator
from Medieval_Europe import get_parent_path

# Main Window to display application
class MainWindow(QMainWindow):
    def __init__(self, app, *args, **kwargs):
        ## Set up Window layout
        super(MainWindow, self).__init__(*args, **kwargs)

        self.objectLists = {'Person': {},
                            'Title': {},
                            'Reign': {},
                            'Place': {}}

        ###### Logging Functionality
        # Grouped by displayed page
        self.logger = Logger(self.objectLists)

        self.pageCallIndex = 0  # Keeps track of the order of pages being displayed
        self.logger.log('Code', 'Init')
        ######

        self.app = app
        screen = self.app.primaryScreen()
        rect = screen.availableGeometry()

        division = 3.0

        width = int(rect.width() * ((division - 1) / division))
        height = int(rect.height() * ((division - 1) / division))

        self.setWindowTitle('Medieval European Database')
        self.setGeometry(int(rect.width() * (1.0 / (division * 2))), 0, width, height)
        # self.showMaximized()

        self.logger.log('Code', 'Set Window Size. Height: ' + str(height) + ', Width: ' + str(width))

        # Configure Window Layout
        self.setCentralWidget(QWidget())

        # Menu Bar
        menuBar = self.menuBar()
        self.logger.log('Code', 'Creating Menu Bar')

        files = menuBar.addMenu("Files")
        data = files.addMenu('Data')
        data.addAction('People')
        data.addAction('Titles')
        data.addAction('Places')

        files.addAction('Shapefile')

        logs = menuBar.addMenu("Logs")
        logs.addAction("Code")
        logs.addAction("Error")
        logs.addAction("Warning")

        logs.triggered[QAction].connect(self.processTrigger)
        data.triggered[QAction].connect(self.processTrigger)

        self.dataDisplay = None

        # Read Files
        self.read_data()

        # Ensure Reigns are in the correct order
        self.ensureCorrectReignOrder()

        ## Create page generator
        # generates the layouts of each page, called from page_factory method
        self.page_generator = PageGenerator(self)

        ## Go to First Page
        self.page_factory('view_object_list', {'Object Type': 'Person', 'Search Text': '', 'Page Type': 'View'})

    def processTrigger(self, q):
        self.logger.log('Code', 'Activated ' + q.text() + ' from the menu bar')
        self.dataDisplay = DisplayData(self, q.text())

        self.dataDisplay.show()

    ## Read Files()
    # Gets the person data from 'people.json'
    # Creates Person objects for each entry
    # Stores each person in dictionary (personList)
    def read_data(self):
        self.logger.log('Code', 'Reading Files')

        with open(os.path.join(get_parent_path(), 'Files/Data/titles.json'), 'r') as stream:
            self.logger.log('Code', 'Opened "titles.json"')

            init_list = json.loads(stream.read())

            if init_list is not None:
                for key in init_list:
                    titleDict = init_list[key]
                    self.add_object(Title(self.logger, titleDict, key))

                self.logger.log('Code', 'Finished reading "titles.json"')
            else:
                self.logger.log('Error', '"titles.json" is empty or could not be read')

        with open(os.path.join(get_parent_path(), 'Files/Data/people.json'), 'r') as stream:
            self.logger.log('Code', 'Opened "people.json"')
            init_list = json.loads(stream.read())

            if init_list is not None:
                for key in init_list:
                    personDict = init_list[key]
                    self.add_object(Person(self.logger, personDict['Gender'], personDict, key))

                    for r in personDict['Reign List']:
                        reignDict = personDict['Reign List'][r]

                        title = self.get_object(reignDict['Connections']['Title'])
                        ruler = self.get_object(key)
                        self.add_object(Reign(self.logger, ruler, title, reignDict, r))

                self.logger.log('Code', 'Finished reading "people.json"')
            else:
                self.logger.log('Error', '"people.json" is empty or could not be read')

        with open(os.path.join(get_parent_path(), 'Files/Data/places.json'), 'r') as stream:
            self.logger.log('Code', 'Opened "places.json"')
            init_list = json.loads(stream.read())

            if init_list is not None:
                for key in init_list:
                    placeDict = init_list[key]
                    self.add_object(Place(self.logger, placeDict, key))

                    for r in placeDict['Reign List']:
                        reign = self.get_object(r)
                        reign.addPlace(self.get_object(key))

                self.logger.log('Code', 'Finished reading "places.json"')
            else:
                self.logger.log('Error', '"places.json" is empty or could not be read')

    ## Go through the reign list to make sure reigns are in the correct order for their title
    # Only run at the start, when all reigns are unordered
    # When ordering, do all connected reigns
    # If a reign already has an order, skip
    # Use the title's available order (which is updated once a run of reigns is ordered) to ensure separate runs are kept separated

    def ensureCorrectReignOrder(self):
        self.logger.log('Code', 'Correcting Reign Order')

        for r, reignObject in self.objectLists['Reign'].items():
            if reignObject.order == -1:
                titleObject = reignObject.getConnectedReign('Title')
                reignObject.setOrder(titleObject.availableOrder)  # Default order number

                ## Set all predecessor reigns
                currentReign = reignObject
                while currentReign.hasConnectedReign('Predecessor'):
                    predecessorObject = self.get_object(currentReign.getConnectedReign('Predecessor'))
                    predecessorObject.setOrder(currentReign.order - 1)  # Set the predecessor reign as one less than the current reign's order
                    currentReign = predecessorObject  # Set the current reign as the predecessor and repeat

                ## Set all successor reigns
                currentReign = reignObject
                while currentReign.hasConnectedReign('Successor'):
                    successorObject = self.get_object(currentReign.getConnectedReign('Successor'))
                    successorObject.setOrder(currentReign.order + 1)  # Set the successor reign as one greater than the current reign's order
                    currentReign = successorObject  # Set the current reign as the successor and repeat

                titleObject.availableOrder = currentReign.order + 200  # Set the title's available order to be 200 greater than the last successor

    def add_object(self, subject):
        addObject = False
        for o_key, o_list in self.objectLists.items():
            if subject.__class__.__name__ == o_key:
                if subject.getID() in o_list:
                    self.logger.log('Warning', '{' + subject.getID() + '} is already in ' + o_key + ' list')

                o_list.update({subject.getID(): subject})
                addObject = True
                break

        if not addObject:
            self.logger.log('Error', 'Cannot add ' + str(subject) + '. ' + str(subject.__class__.__name__) + ' is not a valid object type')

    # Get the object for the ID from the correct list
    def get_object(self, subjectID):
        if isinstance(subjectID, str):
            for o_key, o_list in self.objectLists.items():
                if subjectID in o_list:
                    return o_list[subjectID]

            self.logger.log('Error', 'Cannot get object for ' + str(subjectID) + '. Not a valid object ID')
            return None
        else:
            self.logger.log('Error', 'Cannot get object for ' + str(subjectID) + '. Invalid type')
            return None

    # Get the name of object (i.e. map from id to name)
    def get_object_name(self, subjectID):
        if isinstance(subjectID, str):
            for o_key, o_list in self.objectLists.items():
                if subjectID in o_list:
                    return o_list[subjectID].getName()

            self.logger.log('Error', 'Cannot get object name for ' + str(subjectID) + '. Not a valid object ID')
            return None
        else:
            self.logger.log('Error', 'Cannot get object name for ' + str(subjectID) + '. Invalid type')
            return None

    ## Page Factory(Tab Index, Parameters)
    # Generic function for removing current content and adding new content based on the page at tab_index
    # Parameters is a dictionary of variable parameters necessary for the page
    def page_factory(self, methodChoice, parameters):
        self.logger.log('Code', 'Generating ' + methodChoice)

        ## Get Current content and delete it
        tempPage = self.layout().itemAt(0).widget()
        tempPage.deleteLater()

        self.pageCallIndex += 1
        self.logger.page_key = f'{self.pageCallIndex:03d}_' + methodChoice

        ## Based on the tab index, get the desired function and then run it with the desired parameters
        # Must always return the tab object and the tab layout object
        tempPage = self.page_generator.get_page(methodChoice, parameters)

        self.setCentralWidget(tempPage)

    ## Preparing GUI for adding new object
    # Choose gender for new person
    def prepareNewObject(self, parameters):
        self.logger.log('Code', 'Creating new ' + parameters['Object Type'])

        if parameters['Object Type'] == 'Person':
            dlg = ChooseGenderDialog(self)

            ## Get gender of new person
            gen = dlg.exec_()

            self.logger.log('Code', 'Gender Choice: ' + str(gen))

            ## Create new person
            person = Person(self.logger, gen, None, None)
            self.add_object(person)

            if 'Connection' in parameters:
                self.logger.log('Code', 'New Person will be ' + str(parameters['Connection']) + ' of {' + parameters['Subject'].getID() + '}')
                if 'Spouse' in parameters:
                    spouse = parameters['Spouse'].getSelectedSpouse()
                    #self.logger.log('Code', 'New Person will be ' + str(parameters['Connection']) + ' of {' + parameters['Subject'].getID() + '} with {' + spouse.getID() + '}')
                    self.add_connection(parameters['Subject'], parameters['Connection'], person, spouse)
                else:
                    #self.logger.log('Code', 'New Person will be ' + str(parameters['Connection']) + ' of {' + parameters['Subject'].getID() + '}')
                    self.add_connection(parameters['Subject'], parameters['Connection'], person)

            ## Edit new person's characteristics
            self.page_factory('edit_person_page', {'Person': person})

        elif parameters['Object Type'] == 'Title':
            # Create new title
            title = Title(self.logger, None, None)
            self.add_object(title)

            if 'Connection' in parameters:
                self.logger.log('Code', 'New Title for {' + parameters['Subject'].getID() + '}')
                self.add_connection(parameters['Subject'], parameters['Connection'], title)

                # Edit new title's characteristics
                self.page_factory('edit_title_page', {'Title': title, 'Subject': parameters['Subject'], 'Connection': parameters['Connection']})

            else:
                self.page_factory('edit_title_page', {'Title': title})

        elif parameters['Object Type'] == 'Place':
            # Create new title
            place = Place(self.logger, None, None)
            self.add_object(place)

            # Edit new title's characteristics
            self.page_factory('edit_place_page', {'Place': place})

        elif parameters['Object Type'] == 'Reign':
            self.logger.log('Code', 'Creating new ' + parameters['Connection'] + ' for {' + parameters['Subject'].getID() + '}')

            self.page_factory('choose_object_list', {'Object Type': 'Person', 'Search Text': '', 'Subject': parameters['Subject'], 'Connection': parameters['Connection']})

        else:
            self.logger.log('Error', str(parameters['Object Type']) + ' is not a valid object type')

    # Adds the target as a connection of subject
    # subject: The object that is looking for a connection
    # connection:The connection being sought
    # target: The object that will be connected
    def add_connection(self, subject, connection, target, spouse=None):
        #print('Spouse ID: ' + str(spouse))
        self.logger.log('Code', 'Setting {' + target.getID() + '} as ' + str(connection) + ' for {' + subject.getID() + '}')

        if connection in ['Father', 'Mother']:
            targetParent, otherParent = subject.getParents(connection)

            ## Scenarios:
            # 1) Person has no parents: addParent and reciprocate addChild
            # 2) Person already has one parent, adding another: addParent, make both parents spouses, addChild to both parents with each other as spouse
            # 3) Person already has one parent and new parent is already their spouse: addParent, removeChild from unknown, and addChild for both parents with each other as spouses
            # 4) Person replacing only parent: removeChild from unknown, addParent and reciprocate addChild (addParent overrides original parent relationship)
            # 5) Person has both parents; replacing one with person who is already another spouse:
            #           removeChild from both old parents, addChild to both new parents with each other as spouse, addParent with spouse (addParent overrides original parent relationship)
            # 6) Person has both parents; replacing one with person who is not already a spouse:
            #           removeChild from both old parents, set both new parents as spouses, addChild to both new parents with each other as spouse, addParent (addParent overrides original parent relationship)

            if targetParent is None:  # Does not already have a target parent connection
                subject.addParent(target, connection)  # Add target as new target parent
                if otherParent is None:  # No other parent connection either (1)
                    self.logger.log('Code', '{' + str(subject.getID()) + '} has no parents')
                    target.addChild(subject, None)  # Add subject as new child with unknown spouse
                else:
                    if target.getID() not in self.get_object(otherParent).spouses:  # The target is not already a spouse of other parent (2)
                        self.logger.log('Code', '{' + str(subject.getID()) + '} has another parent who is not a spouse of {' + str(target.getID()) + '}')
                        target.addSpouse(otherParent)  # Add other parent as spouse of target
                        self.get_object(otherParent).addSpouse(target)  # Add target as spouse of other parent
                    else:  # The target is already a spouse of other parent (3)
                        self.logger.log('Code', '{' + str(subject.getID()) + '} has another parent who is already a spouse of {' + str(target.getID()) + '}')
                    self.get_object(otherParent).removeChild(subject)  # Remove subject as child of other parent (with unknown spouse)
                    self.get_object(otherParent).addChild(subject, target)  # Add subject as child of other parent with target
                    target.addChild(subject, otherParent)  # Add subject as child of target with other parent
            else:  # Currently have a target parent connection
                self.get_object(targetParent).removeChild(subject)  # Remove subject as child from current target parent
                if otherParent is None:  # No other parent connection (4)
                    self.logger.log('Code', '{' + str(subject.getID()) + '} has one parent, who is being replaced')
                    subject.addParent(target, connection)  # Add target as new target parent
                    target.addChild(subject, None)  # Add subject as new child with unknown spouse
                else:  # Have both parents (required to be spouses)
                    self.get_object(otherParent).removeChild(subject)  # Remove subject as child from current other parent
                    if target.getID() not in self.get_object(otherParent).spouses:  # The target is not already a spouse of other parent (6)
                        self.logger.log('Code', '{' + str(subject.getID()) + '} has both parents and {' + str(otherParent) + '} is not a spouse')
                        target.addSpouse(otherParent)  # Add other parent as spouse of target
                        self.get_object(otherParent).addSpouse(target)  # Add target as spouse of other parent
                    else:  # The target is already a spouse of other parent (3)
                        self.logger.log('Code', '{' + str(subject.getID()) + '} has both parents and {' + str(otherParent) + '} is a spouse')
                    self.get_object(otherParent).addChild(subject, target)  # Add subject as child of other parent with target
                    target.addChild(subject, otherParent)  # Add subject as child of target with other parent
                    subject.addParent(target, connection)  # Add target as new target parent

        elif connection == 'Spouse':
            if target in subject.spouses:
                print('Already a spouse')
            elif subject in target.spouses:
                print('Should not happen, as reciprocal spouse relationship is missing')
            else:
                subject.addSpouse(target)  # Set the target as this person's spouse
                target.addSpouse(subject)  # Have the target set this person as their spouse

            jointChildrenList = []

            ## Iterate through unknown spouse list and get all joint children
            for c in target.spouses['unknown_spouse']:
                if c in subject.spouses['unknown_spouse']:
                    jointChildrenList.append(c)

            ## Add joint children to both spouse lists
            for c in jointChildrenList:
                target.removeChild(c)
                target.addChild(self.get_object(c), subject)

                subject.removeChild(c)
                subject.addChild(self.get_object(c), target)

        elif connection == 'Child':
            if subject.gender == 0:  # Set subject as father of target
                targetParent, otherParent = target.getParents('Father')
                reciprocalConnection = 'Father'
                otherConnection = 'Mother'
            else:  # Set subject as mother of target
                targetParent, otherParent = target.getParents('Mother')
                reciprocalConnection = 'Mother'
                otherConnection = 'Father'

            # When choosing a child with a specific spouse, it's only important when the child has neither parent.
            # This already handles the scenario where the child has the other parent
            # When adding this secondary connection, need to add spouse as parent of target and add target as child of spouse
            # Valid Scenarios:
            #   - otherParent is not the spouse

            if targetParent is None:  # Target does not have a target parent
                if otherParent is None:  # Target has no parents
                    self.logger.log('Code', '{' + str(target.getID()) + '} has no parents')
                    subject.addChild(target, spouse)
                    if spouse is not None:
                        spouse.addChild(target, subject.getID())
                        target.addParent(spouse, otherConnection)

                else:  # Target has other parent already
                    self.get_object(otherParent).removeChild(target)
                    if otherParent not in subject.spouses:  # Target's other parent is not a spouse of subject
                        self.logger.log('Code', '{' + str(target.getID()) + '} has other parent with no spouse')
                        self.get_object(otherParent).addSpouse(subject)
                        subject.addSpouse(otherParent)

                    else:  # Target's other parent is not a spouse of subject
                        self.logger.log('Code', '{' + str(target.getID()) + '} has other parent who is spouse of {' + str(subject.getID()) + '}')
                    self.get_object(otherParent).addChild(target, subject)
                    subject.addChild(target, otherParent)
                target.addParent(subject, reciprocalConnection)
            else:  # Target has a target parent already
                self.get_object(targetParent).removeChild(target)
                if otherParent is None:  # Target doesn't have the other parent though
                    self.logger.log('Code', '{' + str(target.getID()) + '} has only the target parent')
                    subject.removeChild(target)
                    target.addParent(subject, reciprocalConnection)
                else:  # Target has both parents already
                    self.get_object(otherParent).removeChild(target)
                    if otherParent not in subject.spouses:  # Target's other parent is not already subject's spouse
                        self.logger.log('Code', '{' + str(target.getID()) + '} has both parents and other parent is not spouse of subject')
                        self.get_object(otherParent).addSpouse(subject)
                        subject.addSpouse(otherParent)
                    else:  # Target's other parent is not already subject's spouse
                        self.logger.log('Code', '{' + str(target.getID()) + '} has both parents, but other parent is spouse of subject')
                    self.get_object(otherParent).addChild(target, subject)
                    subject.addChild(target, otherParent)
                    target.addParent(subject, reciprocalConnection)

        elif connection == 'Title':
            newReign = subject.addTitle(target)  # Add the target as a new reign-title for the subject
            self.add_object(newReign)

        elif connection in ('Predecessor', 'Successor'):
            if connection == 'Predecessor':
                targetConnection = connection
                oppConnection = 'Successor'
            else:
                targetConnection = connection
                oppConnection = 'Predecessor'

            # Target is the reign to be connected
            # Subject is the reign looking for a connection
            subject.setConnectedReign(target.getID(), targetConnection)
            target.setConnectedReign(subject.getID(), oppConnection)

            # If the target reign has junior reigns, create new junior reigns for this reign
            for j in target.mergedReigns['Junior']:
                juniorObject = self.get_object(j)

                # Create new reign with this reign's ruler
                newJunior = Reign(self.logger, subject.getConnectedReign('Ruler'), subject.getConnectedReign('Title'), None)

                # Connect these junior reigns to the target's junior reigns
                newJunior.setConnectedReign(juniorObject.getID(), targetConnection)  # Set the predecessor junior as the predecessor of this reign
                juniorObject.setConnectedReign(newJunior.getID(), oppConnection)  ## Set this reign as the successor of the predecessor junior reign

                # Ensure the start and end dates of the junior reign are the same as the senior (subject) reign
                newJunior.updateAttribute('Start Date', subject.getAttribute('Start Date'))
                newJunior.updateAttribute('End Date', subject.getAttribute('End Date'))

                juniorObject.getConnectedReign('Title').addReign(newJunior)

                subject.mergeReign(newJunior, 'Junior')
                newJunior.mergeReign(subject, 'Senior')

                subject.reignList.update({newJunior.getID(): newJunior})
                self.add_object(newJunior)

        elif connection == 'Merge':
            # Target is the senior reign
            # Subject is the reign being linked

            ## Scenarios:
            # 1) Neither reign has any predecessors or successors: make target the senior reign to the subject's junior

            person = subject.getConnectedReign('Ruler')
            person.mergeReigns(subject, target, self)

        # Get reign from title in target for place in subject
        elif connection == 'Reign':
            # Narrow down to one title
            if isinstance(target, Title):
                potential_object_list = {}

                for r in target.reignDict:
                    potential_reign = self.get_object(r)
                    if r != subject.getID():
                        potential_object_list.update({r: potential_reign})

                self.page_factory('choose_object_list', {'Object Type': 'Reign', 'Object List': potential_object_list, 'Search Text': '', 'Subject': subject, 'Connection': 'Reign', 'Title': target})
                #self.page_factory('display_title_page', {'Title': target, 'Page Type': 'Choose', 'Subject': subject, 'Connection': 'Reign', 'Reign': None})

            # Add the reign to the reign list for the place
            elif isinstance(target, Reign):
                subject.addReign(target)
                target.addPlace(subject)

                targetReign = target

                # Propagate connection to reign throughout it's successors
                while targetReign.hasConnectedReign('Successor'):
                    targetReign = self.get_object(targetReign.getConnectedReign('Successor'))

                    # Stop propagation once a successor is already in the list
                    if subject.hasReign(targetReign):
                        break
                    else:
                        subject.addReign(targetReign)
                        targetReign.addPlace(subject)

        elif connection == 'Place':
            subject.addReign(target)
            target.addPlace(subject)

            targetReign = target

            # Propagate connection to reign throughout it's successors
            while targetReign.hasConnectedReign('Successor'):
                targetReign = self.get_object(targetReign.getConnectedReign('Successor'))

                # Stop propagation once a successor is already in the list
                if subject.hasReign(targetReign):
                    break
                else:
                    subject.addReign(targetReign)
                    targetReign.addPlace(subject)

        elif connection == 'Title Predecessor':
            subject.predecessor = target.getID()
            target.successor = subject.getID()

        elif connection == 'Title Successor':
            subject.successor = target.getID()
            target.predecessor = subject.getID()

        else:
            print(str(connection) + ' is not a valid connection to attempt')

        self.write_data()

    def write_data(self):
        #self.logger.log('Code', 'Writing Files')

        ## Get data for each person and collect in a single list
        writePeopleList = {}

        for p_id in self.objectLists['Person']:
            person = self.get_object(p_id)
            writePeopleList.update(person.getDict())

        with open(os.path.join(get_parent_path(), 'Files/Data/Temps/temp_people.json'), 'w') as outfile:
            json.dump(writePeopleList, outfile, indent=4)

        with open(os.path.join(get_parent_path(), 'Files/Data/Temps/temp_people.json'), 'r') as stream, open(os.path.join(get_parent_path(), 'Files/Data/people.json'), 'w') as outfile:
            write_people_json = json.loads(stream.read())

            json.dump(write_people_json, outfile, indent=4)

        #self.logger.log('Code', 'People Written')

        ## Get data for each title and collect in a single list
        writeTitlesList = {}

        for t_id in self.objectLists['Title']:
            title = self.get_object(t_id)
            writeTitlesList.update(title.getDict())

        with open(os.path.join(get_parent_path(), 'Files/Data/Temps/temp_titles.json'), 'w') as outfile:
            json.dump(writeTitlesList, outfile, indent=4)

        with open(os.path.join(get_parent_path(), 'Files/Data/Temps/temp_titles.json'), 'r') as stream, open(os.path.join(get_parent_path(), 'Files/Data/titles.json'), 'w') as outfile:
            write_titles_json = json.loads(stream.read())

            json.dump(write_titles_json, outfile, indent=4)

        #self.logger.log('Code', 'Titles Written')

        ## Get data for each place and collect in a single list
        writePlacesList = {}

        for p_id in self.objectLists['Place']:
            place = self.get_object(p_id)
            writePlacesList.update(place.getDict())

        with open(os.path.join(get_parent_path(), 'Files/Data/Temps/temp_places.json'), 'w') as outfile:
            json.dump(writePlacesList, outfile, indent=4)

        with open(os.path.join(get_parent_path(), 'Files/Data/Temps/temp_places.json'), 'r') as stream, open(os.path.join(get_parent_path(), 'Files/Data/places.json'), 'w') as outfile:
            write_places_json = json.loads(stream.read())

            json.dump(write_places_json, outfile, indent=4)

        #self.logger.log('Code', 'Places Written')


def main():
    ## Creates a QT Application
    app = QApplication(sys.argv)

    ## Creates a window
    window = MainWindow(app)

    ## Shows the window
    window.show()

    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
