
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QScrollArea
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QPen

import json
import networkx as nx
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class DisplayData(QWidget):
    def __init__(self, window, action):
        super().__init__()
        self.window = window

        logger = self.window.logger

        app = self.window.app
        screen = app.primaryScreen()
        rect = screen.availableGeometry()

        division = 7.0

        width = int(rect.width() * ((division - 5) / division))
        #height = int(rect.height() * ((div\ision - 1.5) / division))
        height = width

        self.setWindowTitle(action)
        self.setGeometry(int((rect.width() - width)/2), 100, width, height)

        self.setLayout(QVBoxLayout())

        # Mapping actions to lists
        action_map = {'People': 'Person',
                      'Titles': 'Title',
                      'Places': 'Place'}

        ## Create scrolling mechanics
        scroll = QScrollArea()

        displayList = {}

        if action in ('People', 'Titles', 'Places'):
            for s_id in self.window.objectLists[action_map[action]]:
                subject = self.window.get_object(s_id)
                displayList.update(subject.getDict())
        elif action in ('Code', 'Warning', 'Error'):
            displayList = logger.logDict[action]['Log']
        else:
            logger.log('Error', str(action) + ' is not a valid action to display')

        displayText = QTextEdit()
        displayText.setText(json.dumps(displayList, indent=4, sort_keys=True))

        scroll.setWidget(displayText)
        scroll.setWidgetResizable(True)

        self.layout().addWidget(scroll)


class DisplayRelationGraph(QWidget):
    def __init__(self, window, personList):
        super().__init__()

        self.window = window

        app = self.window.app
        screen = app.primaryScreen()
        rect = screen.availableGeometry()

        division = 7.0

        width = int(rect.width() * ((division - 5) / division))
        #height = int(rect.height() * ((div\ision - 1.5) / division))
        height = width

        self.setWindowTitle('Relation Graph')
        self.setGeometry(int((rect.width() - width)/2), 100, width, height)

        self.setLayout(QVBoxLayout())
        self.installEventFilter(self)

        G = nx.DiGraph()
        labels = {}

        for p, person in personList.items():
            edge = False
            parents = person.getParents()
            if parents[0] is not None:
                # dad = personList[person.father]
                G.add_edge(parents[0], p, color='r')
                edge = True

            if parents[1] is not None:
                # mom = personList[person.mother]
                G.add_edge(parents[1], p, color='b')
                edge = True

            for s in person.spouses:
                if s != 'unknown_spouse':
                    G.add_edge(p, s, color='g')
                    edge = True

            if not edge:
                G.add_node(p)

            labels[p] = person.getAttribute('Name')

        colors = nx.get_edge_attributes(G, 'color').values()
        self.pos = nx.kamada_kawai_layout(G)

        #nx.draw_kamada_kawai(G, with_labels=False, edge_color=colors, node_size=15, width=0.5, font_size=7, ax=self.axes)
        #nx.draw_networkx_labels(G, pos, labels, font_size=6, alpha=.7, ax=self.axes)

        #nx.draw(G, pos=pos, with_labels=False, edge_color=colors, node_size=10, width=0.5)
        #nx.draw_networkx_labels(G, pos, labels, font_size=8, alpha=1)

        self.window.logger.log('Code', 'Finish Display Relation Graph Init')

        self.update()

    def paintEvent(self, event):
        self.window.logger.log('Code', 'Start Painting')
        painter = QPainter(self)
        painter.setRenderHints(painter.Antialiasing)

        # Paint Style
        painter.setPen(QPen(Qt.black, .5, Qt.SolidLine))

        for p_id in self.pos:
            x_pos = int(self.pos[p_id][0]*100) + 100
            y_pos = int(self.pos[p_id][1]*100) + 100

            painter.drawEllipse(x_pos, y_pos, 15, 15)

        self.window.logger.log('Code', 'Painting Graph')
