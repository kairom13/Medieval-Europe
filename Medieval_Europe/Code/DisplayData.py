
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QScrollArea
import json

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
