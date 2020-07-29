'''
Created on May 7, 2020

@author: kairom13
'''


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
import uuid

## Creates a QT Application
app = QApplication([])

## Creates a layout on which to place other widgets
layout = QVBoxLayout()

'''
Place is a class that holds all the information about a specific place
Variables:
    Name - Name of the place
    Kind - Castle, City, Abbey
    History - Dictionary denoting important events, listed by date
    Misc - Miscellaneous notes about place
'''
class Place():
    def __init__(self, name, kind):
        self.id = uuid.uuid4().hex[:8]
        self.name = name
        self.kind = kind
        self.history = {}
        self.misc = ''
    
    def add_misc(self, m):
        self.misc = m
        
    def add_hist(self, n_hist):
        self.history.update(n_hist)
        
    def get_dict(self):
        return { self.id: { 'Name': self.name, \
                            'Kind': self.kind, \
                            'Misc': self.misc, \
                            'History': self.history } }
        
class MainWindow(QWidget):    
    '''
    Initialize GUI Skeleton
    '''
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowTitle('Place Storage')
        self.setGeometry(1000, 200, 450, 500)
        
        with open("data.yaml", 'r') as stream:
            try:
                self.place_list = yaml.safe_load(stream)
                #print(self.place_list)
            except yaml.YAMLError as exc:
                print(exc)
                
        if self.place_list == None:
            self.place_list = {}
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        
        self.tab_list = []
        
        for i in range(2):
            self.tab_list.append(QWidget())
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab_list[0], 'Place List')
        self.tabs.addTab(self.tab_list[1], 'Add Place')
        
        # Configure tabs
        self.first_tab(self.tab_list[0])
        self.second_tab(self.tab_list[1])
        
        # Add tabs to widget
        layout.addWidget(self.tabs)
        
    def first_tab(self, tab):        
        tab.layout = QVBoxLayout()
        
        search = QLineEdit()
        search.layout = QHBoxLayout()
        search.layout.addStretch(1)
        search.layout.addWidget(QLabel('Search:'))
        search.layout.addWidget(search)
        search.layout.addStretch(1)
        
        tab.layout.addLayout(search.layout)
        
        self.group = QGroupBox()
        self.group.layout = QVBoxLayout()
        self.group.setLayout(self.group.layout)
        
        self.group.layout.addWidget(QWidget())
        
        self.town_factory(self.place_list, self.group.layout, None)()

        search.textEdited.connect(lambda: self.check_text(search))
        
        scroll = QScrollArea()
        
        scroll.setWidget(self.group)
        scroll.setWidgetResizable(True)
        
        tab.layout.addWidget(scroll)
        tab.setLayout(tab.layout)
    
    def check_text(self, search):
        text = search.text().lower()
        
        temp_list = {}
        
        for p_id in self.place_list:
            if text in self.place_list[p_id]['Name'].lower():
                temp_list.update({p_id: self.place_list[p_id]})
                
        self.town_factory(temp_list, self.group.layout, None)()

    def second_tab(self, tab):
        tab.layout = QVBoxLayout()
        
        name_grp = QHBoxLayout()

        name_grp.addStretch(1)
        name_grp.addWidget(QLabel('Name:'))
        name_edit = QLineEdit()
        name_grp.addWidget(name_edit)
        name_grp.addStretch(1)
        
        tab.layout.addLayout(name_grp)
        
        kinds = QComboBox()
        kinds.addItems(['Castle', 'City', 'Abbey', 'March', 'County', 'Duchy', 'Kingdom'])
        
        kinds.layout = QHBoxLayout()
        
        kinds.layout.addStretch(1)
        kinds.layout.addWidget(QLabel('Kind:'))
        kinds.layout.addWidget(kinds)
        kinds.layout.addStretch(1)
        
        tab.layout.addLayout(kinds.layout)
        
        misc_grp = QHBoxLayout()
        
        misc_edit = QLineEdit()
        misc_grp.addStretch(1)
        misc_grp.addWidget(QLabel('Misc:'))
        misc_grp.addWidget(misc_edit)
        misc_grp.addStretch(1)
        
        tab.layout.addLayout(misc_grp)
        
        hist = QHBoxLayout()
        
        hist.addStretch(1)
        hist.addWidget(QLabel('History'))
        hist.addStretch(1)
        
        tab.layout.addLayout(hist)
        
        mid_layout = QVBoxLayout()
        
        mid_layout.addWidget(QWidget())
        
        self.history = []
        
        self.note_factory(mid_layout)()
        
        tab.layout.addLayout(mid_layout)
        tab.layout.addStretch(1)
        
        submit = QPushButton('Submit')
        submit.clicked.connect(lambda: self.submit_place(name_edit, kinds, misc_edit, mid_layout))
        
        tab.layout.addWidget(submit)
        
        tab.setLayout(tab.layout)
    def note_factory(self, mid_layout):
        def configure_notes():
            temp = mid_layout.itemAt(0).widget()
            temp.deleteLater()
            
            temp = QWidget()
            temp.layout = QVBoxLayout()
            temp.setLayout(temp.layout)
            
            grid = QGridLayout()
            
            grid.addWidget(QLabel('Date'), 0, 0)
            grid.addWidget(QLabel('Note'), 0, 1)
            
            self.history.append([QLineEdit(), QLineEdit()])
            
            index = 1
            for l in self.history:
                grid.addWidget(l[0], index, 0)
                grid.addWidget(l[1], index, 1) 
                
                index += 1
            
            temp.layout.addLayout(grid)
            
            add_note = QPushButton('+')
            temp.layout.addWidget(add_note)
            
            mid_layout.addWidget(temp)
            
            add_note.clicked.connect(self.note_factory(mid_layout))
        
        return configure_notes
    def submit_place(self, name, kinds, misc, mid_layout):
        place = Place(name.text(), kinds.currentText())
        
        place.add_misc(misc.text())
        
        print('History Length: ' + str(len(self.history)))
        for l in self.history:
            print(l)
            place.add_hist({l[0].text(): l[1].text()})
            
        self.place_list.update(place.get_dict())
        
        with open('data.yaml', 'w') as outfile:
            yaml.dump(self.place_list, outfile, default_flow_style=False)
            
        name.setText('')
        misc.setText('')
        
        self.history = []
        
        self.note_factory(mid_layout)()
        
        self.town_factory(self.place_list, self.group.layout, None)()
        
        self.tabs.setCurrentWidget(self.tab1)
    
    def town_factory(self, place_list, grp_layout, label):
        def configure_towns():
            temp = grp_layout.itemAt(0).widget()
            temp.deleteLater()
            
            temp = QWidget()
            temp.layout = QVBoxLayout()
            temp.setLayout(temp.layout)
            
            if label != None:
                print(label + ' clicked')
            
            for place in place_list:
                if place_list[place]['Kind'] in ['Abbey', 'Castle']:
                    choice = place_list[place]['Name'] + ' ' + place_list[place]['Kind']
                else:
                    choice = place_list[place]['Kind'] + ' of ' + place_list[place]['Name']
                #print(choice)
                
                p_grp = QHBoxLayout()  
                
                if label == choice:
                    open_lab = Arrow(self, '\u25bc', place_list, grp_layout, None)
                    
                    p_grp.addWidget(open_lab)
                    p_grp.addWidget(QLabel(choice))
                    p_grp.addStretch(1)
                    
                    temp.layout.addLayout(p_grp)
                    
                    grid = QGridLayout()
                    
                    grid.addWidget(QLabel('Date'), 0, 0)
                    grid.addWidget(QLabel('Note'), 0, 1)
                    
                    index = 1
                    
                    for year in place_list[place]['History']:
                        grid.addWidget(QLabel(year), index, 0)
                        note = place_list[place]['History'][year]
                        if '{' in note:
                            start = note.find('{')
                            end = note.find('}')
                            
                            note_lab = QLabel(note[:start] + note[start+1:end] + note[end+1:])
                            full_note = note[:start] + note[start+1:end] + note[end+1:]
                            
                            lab_1 = QLabel(note[:start])
                            width_1 = lab_1.fontMetrics().horizontalAdvance(lab_1.text())
                            #width_1 = full_note.fontMetrics().horizontalAdvance(full_note)
                            lab_1.setFixedWidth(width_1)
                            
                            
                            lab_2 = QLabel(note[start+1:end])
                            width_2 = lab_2.fontMetrics().horizontalAdvance(lab_2.text())
                            lab_2.setFixedWidth(width_2)
                            
                            
                            rect = QRect(lab_1.x() + width_1, lab_1.y(), width_2, 20)
                            
                            lab_3 = QLabel(note[end+1:])
                            width_3 = lab_3.fontMetrics().horizontalAdvance(lab_3.text())
                            
                            print('Widths: ' + str(width_1 + width_2 + width_3) + ', Label: ' + str(note_lab.fontMetrics().boundingRect(note_lab.text()).width()))
                            
                            note_lab = QHBoxLayout()
                            note_lab.addWidget(lab_1)
                            note_lab.addWidget(lab_2)
                            note_lab.addWidget(lab_3)
                            note_lab.addStretch(1)
                            
                            grid.addLayout(note_lab, index, 1)

                        else:
                            note_lab = QLabel(note)
                            note_lab.setFixedWidth(200)
                            width = note_lab.fontMetrics().boundingRect(note_lab.text()).width()
                            print('Text: ' + str(width) + ', Label: ' + str(note_lab.width()))
                            note_lab.setWordWrap(True)
                            grid.addWidget(note_lab, index, 1)
                        
                        index += 1
                    
                    temp.layout.addLayout(grid)
                    
                else:
                    open_lab = Arrow(self, '\u25b6', place_list, grp_layout, choice)
                    p_grp.addWidget(open_lab)
                    p_grp.addWidget(QLabel(choice))
                    p_grp.addStretch(1)
            
                    temp.layout.addLayout(p_grp)
                
            grp_layout.addWidget(temp)
        return configure_towns
    
    def remove_components(self, layout):
        for i in reversed(range(layout.count())):
            temp_layout = layout.itemAt(i)
            if layout.itemAt(i).layout() != None:
                self.remove_components(temp_layout.layout())
                
                temp_layout.layout().deleteLater()
                
            if temp_layout.widget() != None:
                temp_layout.widget().deleteLater()
            layout.removeItem(temp_layout)

        return layout
    
class Arrow(QLabel):
    def __init__(self, window, arrow, place_list, grp_layout, choice):
        super(Arrow, self).__init__(arrow)
        self.window = window
        self.place_list = place_list
        self.grp_layout = grp_layout
        self.choice = choice
        
        self.label = QLabel(arrow)
        self.label.adjustSize()
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.installEventFilter(self)
        
    #Override
    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.window.town_factory(self.place_list, self.grp_layout, self.choice)()
            #print(str(self.choice) + ' pressed')
            return True
        return False

## Creates a window
window = MainWindow()

## Set this layout to be the layout of the window
window.setLayout(layout)

## Shows the window
window.show()
app.exec_()