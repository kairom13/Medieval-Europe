import json
import os
import sys
import uuid

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pyproj import Transformer

from Medieval_Europe.Code.CustomObjects import Person, Title, Reign, Place, Logger
from foronoi import Voronoi, Polygon, Visualizer, VoronoiObserver

from Medieval_Europe.Code.Widgets.Displays import PlaceMap


def get_parent_path():
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)

        return os.path.join(datadir, 'lib/Medieval_Europe/')

    else:
        # The application is not frozen
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Medieval_Europe/')


class VoronoiTest(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.width = 1000
        self.height = 800

        self.objectLists = {'Person': {},
                            'Title': {},
                            'Reign': {},
                            'Place': {}}

        ###### Logging Functionality
        # Grouped by displayed page
        self.logger = Logger(self.objectLists, True)

        self.pageCallIndex = 0  # Keeps track of the order of pages being displayed
        self.logger.log('Code', 'Initializing ' + self.__class__.__name__)
        ######

        self.app = app
        screen = self.app.primaryScreen()
        rect = screen.availableGeometry()

        division = 3.0

        width = int(rect.width() * ((division - 1) / division))
        height = int(rect.height() * ((division - 1) / division))

        self.setWindowTitle('Medieval European Database')
        self.setGeometry(int(rect.width() * (1.0 / (division * 2))), 0, width, height)

        # Read Files
        self.read_data()

        self.voronoiDiagram = None
        # Create Voronoi Diagram for Places
        self.voronoiInfo = self.create_voronoi_diagram()

        #placeMap = PlaceMap(self, vPolygons=self.vPolygons)

        # Configure Window Layout
        self.setCentralWidget(VoronoiMap(self.voronoiInfo))

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

    # Create Voronoi Diagram for Places
    def create_voronoi_diagram(self):
        transformer = Transformer.from_crs(4326, 3035, always_xy=True)

        vPoints = []
        boundingBox = {}
        pointFinder = {}

        for p, place in self.objectLists['Place'].items():
            point = (float(place.getAttribute('Longitude')), float(place.getAttribute('Latitude')))
            vPoints.append(point)

            if point[1] in pointFinder:
                yDict = pointFinder[point[1]]
                if point[0] in yDict:
                    print(place.getName() + ' has the same coordinate as ' + yDict[point[0]].getName())
                else:
                    yDict.update({point[0]: place})
            else:
                pointFinder.update({point[1]: {point[0]: place}})

            if boundingBox:
                if point[0] < boundingBox['Left']:
                    boundingBox.update({'Left': point[0]})
                elif point[1] < boundingBox['Bottom']:
                    boundingBox.update({'Bottom': point[1]})
                elif point[0] > boundingBox['Right']:
                    boundingBox.update({'Right': point[0]})
                elif point[1] > boundingBox['Top']:
                    boundingBox.update({'Top': point[1]})
            else:
                boundingBox.update({'Left': point[0],
                                    'Bottom': point[1],
                                    'Right': point[0],
                                    'Top': point[1]})

        vPolygon = Polygon([
            (boundingBox['Left']-1, boundingBox['Top']+1),
            (boundingBox['Left']-1, boundingBox['Bottom']-1),
            (boundingBox['Right']+1, boundingBox['Bottom']-1),
            (boundingBox['Right']+1, boundingBox['Top']+1)])

        self.voronoiDiagram = Voronoi(vPolygon)
        self.voronoiDiagram.create_diagram(points=vPoints)

        def getQPoint(vPoint):
            #ratio = self.width / (boundingBox['Right'] - boundingBox['Left'] + 2)
            ratio = 85

            xPos = vPoint.x * ratio
            yPos = (boundingBox['Top'] + 1 - vPoint.y) * ratio

            return QPoint(int(round(xPos, 0)), int(round(yPos, 0)))

        voronoiDisplay = []
        dummyTitle = Title(self.logger, None, None)

        def getMaxTitle(placeObject):
            maxTitleCount = {}
            maxTitle = ''

            for r in placeObject.reignList:  # Go through each reign for this place
                reignObject = self.get_object(r)
                titleObject = reignObject.getConnection('Title')
                if titleObject.getID() in maxTitleCount:
                    maxTitleCount[titleObject.getID()] += 1  # Increase the count by one if the title already exists
                else:
                    maxTitleCount.update({titleObject.getID(): 1})  # Add new title with count of 1
                    if maxTitle == '':
                        maxTitle = titleObject.getID()  # Set the max title if the new title is the first title

                if maxTitleCount[titleObject.getID()] > maxTitleCount[maxTitle]:  # Compare the updated title to the max title to find new max
                    maxTitle = titleObject.getID()

            if maxTitle == '':
                self.logger.log('Detailed', place.getName() + ': Dummy Title')
                return dummyTitle
            else:
                self.logger.log('Detailed', place.getName() + ': {' + maxTitle + '}')
                return self.get_object(maxTitle)

        for pSite in self.voronoiDiagram.sites:
            #print('\nPoint: (' + str(pSite.x) + ', ' + str(pSite.y) + ')')
            edge = pSite.first_edge
            first_origin = edge.get_origin(max_y=boundingBox['Top']-1)
            poly_points = [getQPoint(first_origin)]

            edge = edge.next
            edgeCt = 1
            while edge != pSite.first_edge:
                #print('\tEdge: ' + str(edge))
                #print('\tNext Edge: ' + str(edge.next))

                next_origin = edge.get_origin(max_y=boundingBox['Top']-1)
                poly_points.append(getQPoint(next_origin))
                #print('\t\t' + str(poly_points[-1]))

                edge = edge.next
                edgeCt += 1

            #print('\t\t' + str(poly_points[-1]))

            placeSite = pointFinder[pSite.y][pSite.x]
            title = getMaxTitle(placeSite)
            titleHex = title.getAttribute('Color')

            voronoiDisplay.append({'Polygon': QPolygon(poly_points),
                                   'Point': getQPoint(pSite),
                                   'Color': QColor('#' + titleHex)})

        return voronoiDisplay

class VoronoiMap(QWidget):
    def __init__(self, voronoiInfo):
        super().__init__()

        self.voronoiInfo = voronoiInfo

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(painter.Antialiasing)

        # Paint Style
        painter.setPen(QPen(Qt.black, .5, Qt.SolidLine))

        painter.drawRect(self.rect())
        radius = 2

        for vInfo in self.voronoiInfo:
            vColor = vInfo['Color']
            vPoly = vInfo['Polygon']
            if isinstance(vPoly, QPolygon):
                #painter.setBrush(QBrush(QColor('#' + uuid.uuid4().hex[:6]), Qt.SolidPattern))
                painter.setBrush(QBrush(vColor, Qt.SolidPattern))
                painter.drawPolygon(vPoly)
            else:
                print(str(vPoly) + ' is not a QPolygon')

            vPoint = vInfo['Point']
            if isinstance(vPoint, QPoint):
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(Qt.black, .5, Qt.SolidLine))
                painter.drawEllipse(vPoint, radius, radius)
            else:
                print(str(vPoint) + ' is not a QPoint')

app = QApplication(sys.argv)

## Creates a window
window = VoronoiTest(app)

## Shows the window
window.show()

Visualizer(window.voronoiDiagram, canvas_offset=1) \
    .plot_sites(show_labels=False) \
    .plot_edges(show_labels=False) \
    .show()

app.exec_()


