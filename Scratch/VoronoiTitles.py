import json
import os
import sys

from PyQt5.QtWidgets import *

from Medieval_Europe.Code.CustomObjects import Logger, Person, Place, Title, Reign
from Medieval_Europe.Code.Widgets.Displays import PlaceMap


def get_parent_path():
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)

        return os.path.join(datadir, 'lib/Medieval_Europe/')

    else:
        # The application is not frozen
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Medieval_Europe/')


class MainWindow(QMainWindow):
    def __init__(self, app, *args, **kwargs):
        ## Set up Window layout
        super(MainWindow, self).__init__(*args, **kwargs)

        self.objectLists = {'Person': {},
                            'Title': {},
                            'Reign': {},
                            'Place': {}}

        # A dictionary that maps places to a specific title
        # Format: {<placeID>: <titleColor>}
        self.placeTitleDict = {}

        ###### Logging Functionality
        # Grouped by displayed page
        self.logger = Logger(self.objectLists, True)

        self.pageCallIndex = 0  # Keeps track of the order of pages being displayed
        self.logger.log('Code', 'Init')
        ######

        self.app = app
        screen = self.app.primaryScreen()
        rect = screen.availableGeometry()

        division = 3.0

        width = int(rect.width() * ((division - 1) / division))
        height = int(rect.height() * ((division - 1) / division))

        self.setWindowTitle('Voronoi Map of Titles')
        self.setGeometry(int(rect.width() * (1.0 / (division * 2))), 0, width, height)

        self.logger.log('Code', 'Set Window Size. Height: ' + str(height) + ', Width: ' + str(width))

        # Read Files
        self.read_data()

        mapGroup = QGroupBox('Place Map')
        mapLayout = QVBoxLayout(mapGroup)
        self.setCentralWidget(mapGroup)

        placeMap = PlaceMap(self, multiColor=True)
        mapLayout.addWidget(placeMap)
        self.logger.log('Code', 'Successfully created Place Map')

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
                    self.logger.log('Detailed', 'Adding title: ' + key)
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
                    self.logger.log('Detailed', 'Adding person: ' + key)
                    self.add_object(Person(self.logger, personDict['Gender'], personDict, key))

                    for r in personDict['Reign List']:
                        reignDict = personDict['Reign List'][r]

                        title = self.get_object(reignDict['Connections']['Title'])
                        ruler = self.get_object(key)
                        self.logger.log('Detailed', 'Adding reign: ' + r)
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
                    self.logger.log('Detailed', 'Adding place: ' + key)
                    self.add_object(Place(self.logger, placeDict, key))

                    for r in placeDict['Reign List']:
                        reign = self.get_object(r)
                        reign.addPlace(self.get_object(key))

                self.logger.log('Code', 'Finished reading "places.json"')
            else:
                self.logger.log('Error', '"places.json" is empty or could not be read')

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
        else:
            self.logger.log('Error', 'Cannot get object for ' + str(subjectID) + '. Invalid type')

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