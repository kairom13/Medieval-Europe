"""
Created on Aug 1, 2022

@author: kairom13
"""
import math

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import shapefile
from pyproj import Transformer
import uuid

from Medieval_Europe import get_parent_path
import os


## Widget for choosing/viewing person from list
class ObjectLabelWidget(QWidget):
    def __init__(self, obj, objectType, button):
        super(ObjectLabelWidget, self).__init__()

        self.widgets = [self]

        self.button = button
        self.placeCheckbox = None

        if objectType == 'Person':
            self.info = obj.getName() + ' (' + obj.getAttribute('Birth Date') + ' - ' + obj.getAttribute('Death Date') + ')'

        elif objectType == 'Title':
            self.info = obj.getFullRealmTitle()

        elif objectType == 'Place':
            self.info = obj.getAttribute('Name') + ' (' + obj.getAttribute('Latitude') + ', ' + obj.getAttribute('Longitude') + ')'

        elif objectType == 'Reign':
            self.info = obj.getConnectedReign('Ruler').getAttribute('Name') + ' ' + obj.getDateString()

            if self.button.connection in ('Predecessor', 'Successor'):
                self.placeCheckbox = QCheckBox('Transfer Places?')
                self.placeCheckbox.setChecked(True)

                self.placeCheckbox.stateChanged.connect(self.checkedPlace)

        else:
            self.info = 'missing info'

        infoLabel = QLabel(self.info)
        self.widgets.append(infoLabel)

        infoLabel.layout = QHBoxLayout()
        infoLabel.layout.addWidget(infoLabel)

        if self.placeCheckbox is not None:
            self.widgets.append(self.placeCheckbox)
            infoLabel.layout.addWidget(self.placeCheckbox)

        self.widgets.append(self.button)

        infoLabel.layout.addStretch(1)
        infoLabel.layout.addWidget(self.button)

        self.setLayout(infoLabel.layout)

    def show(self):
        for w in self.widgets:
            w.setVisible(True)

    def hide(self):
        for w in self.widgets:
            w.setVisible(False)

    def checkedPlace(self, checked):
        if checked > 0:
            self.button.checkedPlace = True
        else:
            self.button.checkedPlace = False


class PlaceMap(QWidget):
    def __init__(self, window, placeList):
        super().__init__()

        self.window = window

        transformer = Transformer.from_crs(4326, 3035, always_xy=True)

        self.placeList = []
        for p, place in placeList.items():
            self.placeList.append({'Coordinates': (transformer.transform(float(place.getAttribute('Longitude')), float(place.getAttribute('Latitude')))),
                                   'Object': place})

        self.adjustCoords = {}  # Global values to adjust shapefile to desired dimensions
        self.polygons = []  # Array of shapefile polygons
        self.shapes = None  # Shapefile shape list object
        self.river_shp = None
        self.rivers = []

        self.dragMapFlag = False
        self.setMouseTracking(True)
        self.selectedPlace = None
        self.initialized = False

        self.zoom = 1
        self.cursorPos = None

        self.setLayout(QVBoxLayout())

        # There are two coordinates to describe positions:
        # 1) Map position: the coordinates of a point relative to the Earth using the projection transformation
        # 2) Display position: the coordinates of a point relative to the display on the screen
        #   - the origin of the display is the top left corner of the display

        # Values for the dimensions and origin of the map on the display
        # Change with zoom and position
        self.disp_dim = None

        # Constant values for the dimensions and origin of the map in map coordinates (i.e. projection)
        self.map_dim = {'width': -1, 'height': -1}
        self.map_origin = None
        self.buffer = -1

        self.installEventFilter(self)

        self.eventNameDict = {}
        for name in vars(QEvent):
            attribute = getattr(QEvent, name)
            if type(attribute) == QEvent.Type:
                self.eventNameDict[attribute] = name

        with shapefile.Reader(os.path.join(get_parent_path(), 'Files/Shapefiles/Territories/Europe_1_Simplified')) as shp:
            self.shapes = shp.shapes()
        #
        # file_name = '/Users/kairom13/Shapefiles/Europe/Nature/European Rivers/European Rivers Simplified'
        # with shapefile.Reader(file_name) as shp:
        #     self.river_shp = shp.shapes()

    def initialize(self):
        # Set initial cursor position
        self.cursorPos = QPoint(int(self.width() / 2), int(self.height() / 2))

        # Set initial display dimensions
        self.disp_dim = {'width': self.width(), 'height': self.height()}

        # Adjust shapefile to fit in application
        self.get_shapefile_dimensions()

        if self.placeList:
            self.get_focus_area()

        # print(str(self.width()) + ', ' + str(self.height()))

        # Move polygons to list to be drawn
        #self.drawShapefile()

        self.initialized = True

    def paintEvent(self, event):
        if not self.initialized:
            self.initialize()

        painter = QPainter(self)
        painter.setRenderHints(painter.Antialiasing)

        # Paint Style
        painter.setPen(QPen(Qt.black, .5, Qt.SolidLine))

        painter.drawRect(self.rect())
        radius = 5

        for s in self.shapes:
            poly_points = []

            points = s.points

            part_index = 0  ## Index of point in shape
            for p in points:
                if part_index in s.parts:  ## 'Parts' lists index of first point of part.
                    if len(poly_points) > 0:  ## Only append when there are points to append
                        painter.drawPolygon(QPolygon(poly_points))

                    poly_points = []

                # Coordinates of map points shifted to display origin (based on zoom) and adjusted to correct size
                map_coords = {'x': self.adjustCoords['X Origin'] + (p[0] - self.adjustCoords['Left']) * self.adjustCoords['Ratio'],
                    'y': self.adjustCoords['Y Origin'] + (self.adjustCoords['Top'] - p[1]) * self.adjustCoords['Ratio']}

                poly_points.append(QPoint(round(map_coords['x'], 0), round(map_coords['y'], 0)))

                part_index += 1

            painter.drawPolygon(QPolygon(poly_points))

        for p in self.placeList:
            xPos = p['Coordinates'][0]
            yPos = p['Coordinates'][1]

            p.update({'Map Coords': (self.adjustCoords['X Origin'] + (xPos - self.adjustCoords['Left']) * self.adjustCoords['Ratio'],
                                     self.adjustCoords['Y Origin'] + (self.adjustCoords['Top'] - yPos) * self.adjustCoords['Ratio'])})

            if self.selectedPlace is not None and p['Object'].getID() == self.selectedPlace.getID():
                painter.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
                painter.drawEllipse(p['Map Coords'][0] - radius, p['Map Coords'][1] - radius, radius * 2, radius * 2)
                painter.drawText(p['Map Coords'][0] + radius, p['Map Coords'][1] - radius, p['Object'].getAttribute('Name'))
            else:
                painter.setPen(QPen(Qt.black, .5, Qt.SolidLine))
                painter.drawEllipse(p['Map Coords'][0] - radius, p['Map Coords'][1] - radius, radius * 2, radius * 2)

    def eventFilter(self, object, event):
        #print(self.eventNameDict[event.type()])
        if self.initialized:
            if event.type() == QEvent.Wheel:  # Wheel Event
                # print('Pixel Delta: ' + str(event.pixelDelta().y()))
                pixelScroll = event.pixelDelta().y() / 15

                self.cursorPos = event.position()

                old_factor = 2 ** (self.zoom - 1)

                self.zoom += pixelScroll

                if self.zoom < 1:
                    self.zoom = 1
                elif self.zoom > 10:
                    self.zoom = 10

                new_factor = 2 ** (self.zoom - 1)
                factor_ratio = new_factor / old_factor

                #### To get the right location for the map relative to the display:
                ## Always know the cursor's normalized position (i.e. where height and width are 1)
                ## Use zoom value to determine actual height and width of the map
                ## Apply the normalized cursor position to the map height and width to get position on map
                ## Subtract from the cursor's position on the display.

                # 3 step process:
                # 1) Get cursor's normalized position on the map before zooming
                #print('1: ' + str(self.disp_dim))
                cursor_pos_norm = {'x': (self.cursorPos.x() - self.adjustCoords['X Origin']) / self.disp_dim['width'], 'y': (self.cursorPos.y() - self.adjustCoords['Y Origin']) / self.disp_dim['height']}

                # 2) Update the display dimensions to the new zoom level
                #self.disp_dim = {'width': self.width * (2 ** (self.zoom - 1)), 'height': self.height * (2 ** (self.zoom - 1))}
                self.disp_dim = {'width': self.disp_dim['width'] * factor_ratio, 'height': self.disp_dim['height'] * factor_ratio}

                # 3) Apply the normalized position to the new display dimensions to get the cursor's new map position
                #print('New Display: ' + str(self.disp_dim))
                cursor_pos_map = {'x': cursor_pos_norm['x'] * self.disp_dim['width'], 'y': cursor_pos_norm['y'] * self.disp_dim['height']}
                self.adjustCoords['X Origin'] = self.cursorPos.x() - cursor_pos_map['x']
                self.adjustCoords['Y Origin'] = self.cursorPos.y() - cursor_pos_map['y']

                self.update_ratio()

                self.update()

                return True
            elif event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    if self.selectedPlace is not None:
                        self.window.page_factory('display_place_page', {'Place': self.selectedPlace})
                    else:
                        self.dragMapFlag = True
                        self.cursorPos = event.pos()

                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.dragMapFlag = False

                return True
            elif event.type() == QEvent.MouseMove:
                self.selectedPlace = None
                for p in self.placeList:
                    map_coords = p['Map Coords']

                    if self.withinDistance(map_coords, (event.pos().x(), event.pos().y()), 10):
                        self.selectedPlace = p['Object']
                        break

                if self.dragMapFlag:
                    # print('Shift: (' + str(event.pos().x() - self.cursorPos.x()) + ','
                    #       + str(event.pos().y() - self.cursorPos.y()) + ')')
                    shift = {'x': event.pos().x() - self.cursorPos.x(), 'y': event.pos().y() - self.cursorPos.y()}
                    self.cursorPos = event.pos()

                    self.adjustCoords['X Origin'] += shift['x']
                    self.adjustCoords['Y Origin'] += shift['y']

                self.update()
                return True
        else:
            #print('ERROR: Could not register event, map not yet initialized')
            return False
        return False

    def withinDistance(self, ptOne, ptTwo, dist):
        d = math.sqrt(math.pow(ptOne[0] - ptTwo[0], 2) + math.pow(ptOne[1] - ptTwo[1], 2))

        if d < dist:
            return True
        else:
            return False

    def get_focus_area(self):
        # Get bounding box of whole shapefile by iterating through shapes and finding maximas
        map_edges = {}

        map_edges.update({'left': self.placeList[0]['Coordinates'][0]})
        map_edges.update({'bottom': self.placeList[0]['Coordinates'][1]})
        map_edges.update({'right': self.placeList[0]['Coordinates'][0]})
        map_edges.update({'top': self.placeList[0]['Coordinates'][1]})

        for p in self.placeList:
            p = p['Coordinates']
            if p[0] < map_edges['left']:
                map_edges['left'] = p[0]
            if p[1] < map_edges['bottom']:
                map_edges['bottom'] = p[1]
            if p[0] > map_edges['right']:
                map_edges['right'] = p[0]
            if p[1] > map_edges['top']:
                map_edges['top'] = p[1]

        self.buffer = 50

        if map_edges['top'] == map_edges['bottom']:
            self.zoom = 10
            map_edges['left'] = p[0] - (2 ** (self.zoom - 1))
            map_edges['bottom'] = p[1] - (2 ** (self.zoom - 1))
            map_edges['right'] = p[0] + (2 ** (self.zoom - 1))
            map_edges['top'] = p[1] + (2 ** (self.zoom - 1))

        else:
            zoom_factor = self.map_dim['height'] / (map_edges['top'] - map_edges['bottom'])
            self.zoom = 1+math.log2(zoom_factor)

        self.update_map_scaling(map_edges)

        #self.disp_dim = {'width': self.width * zoom_factor, 'height': self.height * zoom_factor}

        #print('Focus: ' + str(self.disp_dim))

        #self.update_ratio()

    def get_shapefile_dimensions(self):
        # Get bounding box of whole shapefile by iterating through shapes and finding maximas
        map_edges = {}

        map_edges.update({'left': self.shapes[0].bbox[0]})
        map_edges.update({'bottom': self.shapes[0].bbox[1]})
        map_edges.update({'right': self.shapes[0].bbox[2]})
        map_edges.update({'top': self.shapes[0].bbox[3]})

        for s in self.shapes:
            if s.bbox[0] < map_edges['left']:
                map_edges['left'] = s.bbox[0]
            if s.bbox[1] < map_edges['bottom']:
                map_edges['bottom'] = s.bbox[1]
            if s.bbox[2] > map_edges['right']:
                map_edges['right'] = s.bbox[2]
            if s.bbox[3] > map_edges['top']:
                map_edges['top'] = s.bbox[3]

        self.buffer = 10

        # self.adjustCoords['Left'] = map_edges['left']
        # self.adjustCoords['Top'] = map_edges['top']
        #
        # self.map_dim['width'] = map_edges['right'] - map_edges['left']
        # self.map_dim['height'] = map_edges['top'] - map_edges['bottom']

        self.update_map_scaling(map_edges)

    def update_map_scaling(self, map_edges):
        # Get dimensions of the map's bounding box=
        self.map_dim['width'] = map_edges['right'] - map_edges['left']
        self.map_dim['height'] = map_edges['top'] - map_edges['bottom']

        self.adjustCoords['Left'] = map_edges['left']
        self.adjustCoords['Top'] = map_edges['top']

        st_x = self.buffer
        st_y = self.buffer

        # Aspect Ratios for the map and the display
        mapRatio = self.map_dim['height'] / self.map_dim['width']
        dispRatio = self.disp_dim['height'] / self.disp_dim['width']

        #print('Map: ' + str(self.map_dim))
        #print('Display: ' + str(self.disp_dim))

        # Adjust start points based on which axis is better
        if mapRatio > dispRatio:
            ratio = (self.disp_dim['height'] - 2*self.buffer) / self.map_dim['height']
            st_x += (self.disp_dim['width'] - self.map_dim['width'] * ratio) / 2
        else:
            ratio = (self.disp_dim['width'] - 2*self.buffer) / self.map_dim['width']
            st_y += (self.disp_dim['height'] - self.map_dim['height'] * ratio) / 2

        # Global scalars to adjust shapefile to application dimensions
        self.adjustCoords.update({'X Origin': st_x,  # X position of the top left corner of the map in the display
                                  'Y Origin': st_y,  # Y position of the top left corner of the map in the display
                                  'Ratio': ratio})  # Shrinkage factor to make map fit display

    def update_ratio(self):
        # Aspect Ratios for the map and the display
        mapRatio = self.map_dim['height'] / self.map_dim['width']
        dispRatio = self.disp_dim['height'] / self.disp_dim['width']

        # Adjust start points based on which axis is better
        if mapRatio > dispRatio:
            ratio = self.disp_dim['height'] / self.map_dim['height']
        else:
            ratio = self.disp_dim['width'] / self.map_dim['width']

        # Global scalars to adjust shapefile to application dimensions
        self.adjustCoords.update({'Ratio': ratio})  # Shrinkage factor to make map fit display

        # print(self.adjustCoords)

## Interactive Object Label for Relations and Titles
class ObjectLabel(QLabel):
    def __init__(self, window, objectID, objectType, gender=-1):
        super(ObjectLabel, self).__init__()

        self.window = window
        self.objectType = objectType

        if self.objectType == 'Person':
            self.obj = self.window.get_object(objectID)
            self.name = self.obj.getAttribute('Name') + ' ' + self.obj.getAttribute('Nickname')
        elif self.objectType == 'Title':
            self.obj = self.window.get_object(objectID)
            self.name = self.obj.getFullRulerTitle(gender)

        self.setText(self.name)

        self.setStyleSheet('QLabel {color : black; text-decoration: underline}')

        self.label = QLabel(self.name)
        self.label.adjustSize()
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.installEventFilter(self)

    # Override
    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.setCursor(QCursor(Qt.PointingHandCursor))
            self.setStyleSheet('QLabel {color: blue; text-decoration: underline}')
            return True
        elif event.type() == QEvent.Leave:
            self.setCursor(QCursor(Qt.PointingHandCursor))
            self.setStyleSheet('QLabel {color : black; text-decoration: underline}')
            return True
        elif event.type() == QEvent.MouseButtonRelease:
            if self.objectType == 'Person':
                self.window.page_factory('display_person_page', {'Person': self.obj})
            elif self.objectType == 'Title':
                self.window.page_factory('display_title_page', {'Title': self.obj, 'Page Type': 'View'})
            return True
        return False

## Display widget for events (actual editing within separate event widget
class EventsWidget(QGroupBox):
    def __init__(self, window, edit, subject):
        super().__init__('Events')

        from Medieval_Europe.Code.Widgets.Interactives import EventWidget

        self.window = window
        self.setLayout(QVBoxLayout())

        self.subject = subject  # The object that the event is attached to
        event_list = self.subject.getEventList()  # The dict of events, key: uuid, data: date, content

        header_layout = QHBoxLayout()
        dateLabel = QLabel('Date')
        dateLabel.setAlignment(Qt.AlignCenter)
        if edit:
            dateLabel.setFixedWidth(120)

        else:
            dateLabel.setFixedWidth(95)

        header_layout.addWidget(dateLabel)
        header_layout.addWidget(QLabel('Content'))

        self.layout().addLayout(header_layout)

        scrollWidget = QWidget()
        scrollWidget.layout = QVBoxLayout()
        scrollWidget.setLayout(scrollWidget.layout)

        for e in event_list:
            scrollWidget.layout.addWidget(EventWidget(self.window, edit, e, self.subject))

        if edit:
            addButton = QPushButton('Add')
            addButton.clicked.connect(self.addEvent)

            scrollWidget.layout.addWidget(addButton, alignment=Qt.AlignCenter)

        scrollWidget.layout.addStretch(1)

        ## Create scrolling mechanics
        scroll = QScrollArea()

        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)

        self.layout().addWidget(scroll)

    def addEvent(self):
        self.subject.updateEvent(uuid.uuid4().hex[:8], {'Date': '', 'Content': ''})

        self.window.write_data()
        if self.subject.getObjectType() == 'Person':
            self.window.page_factory('edit_person_page', {'Person': self.subject})
        elif self.subject.getObjectType() == 'Title':
            self.window.page_factory('edit_title_page', {'Title': self.subject})
        elif self.subject.getObjectType() == 'Place':
            self.window.page_factory('edit_place_page', {'Place': self.subject})

    # def paintEvent(self, event):
    #     left_width = 75
    #
    #     print('Painting Widget')
    #
    #     painter = QPainter(self)
    #     painter.setRenderHints(painter.Antialiasing)
    #
    #     # Paint Style
    #     painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
    #
    #     stPt = QPoint(left_width, 0)
    #     endPt = QPoint(left_width, self.height())
    #
    #     painter.drawLine(QLine(stPt, endPt))



