'''
Created on Jul 22, 2020

@author: aaronleisure
'''

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import yaml
import uuid
from BinarySearchTree import insert

## Creates a QT Application
app = QApplication([])

class MainWindow(QWidget):    
    def __init__(self, *args, **kwargs):
        ## Set up Window layout
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle('Medieval Europe')
        self.setGeometry(900, 200, 500, 500)
        
        self.layout.addWidget(QWidget())
        
        ## None Person
        ## In order to prevent Null Pointer Exception, there will be a None person to use as filler
        ## Is Empty except name is Null and gender is -1
        
        self.null_person = Person(None, 'Null', -1)
        
        ## Facilitate program
        self.read_data()
        
        ## Initialize tab screen
        # First Tab: List of all characters, includes edit and view buttons, has an add button for a new character
        # Second Tab: View character, lists the info about the character. Relatives have links to their own pages. Includes and edit button for changing info
        # Third Tab: Edit Character, has line edit widgets to change 
        
        self.tab_list = []
        self.tab_list.append(self.first_factory())
        self.tab_list.append(self.second_factory())
        self.tab_list.append(self.third_factory())
        
        
        
        #self.tabs.resize(300,200)
        
        # Add tabs
        #self.tabs.addTab(self.tab_list[0], 'Person List')
        #self.tabs.addTab(self.tab_list[1], 'Add Person')
        
        # Configure tabs
        #self.first_page()
        
        #first_key = list(self.char_list.keys())[0]
        #self.second_page(self.tab_list[1], self.char_list[first_key])()
        
        # Add tabs to widget
        #self.layout.addWidget(self.tab_list[0])
        self.page_factory(0, {'Char List': self.char_list, 'Search Text': '', 'Choose Char': False})
        
    def read_data(self):
        with open("characters.yaml", 'r') as stream:
            try:
                self.char_list = []
                init_list = yaml.safe_load(stream)
                
                if init_list == None:
                    self.char_list = []
                else:
                    for key in init_list:
                        char_dict = init_list[key]
                        
                        self.char_list.append(Person(self.null_person, char_dict['Name'], char_dict['Gender']))
                    
                #print(self.place_list)
            except yaml.YAMLError as exc:
                print(exc)
    
    def first_factory(self):
        def first_page(parameters):
            ## Create layout for the tab
            tab = QWidget()
            tab.layout = QVBoxLayout()
            
            chars_list = parameters['Char List']
            
            ## Widget for searching for specific characters
            search = QLineEdit(parameters['Search Text'])
            search.layout = QHBoxLayout()
            search.layout.addStretch(2)
            search.layout.addWidget(QLabel('Search:'))
            search.layout.addWidget(search)
            search.layout.addStretch(1)
            
            search.setFocusPolicy(Qt.StrongFocus)
            
            tab.layout.addLayout(search.layout)
            
            ## Include button to add new characters
            add_button = QPushButton('Add')
            search.layout.addWidget(add_button)
            search.layout.addStretch(2)
            
            add_button.clicked.connect(lambda: self.pre_add_char( { 'Person': None, 'Edit': False }))
            
            ## Groupbox that lists every character
            group = QGroupBox()
            group.layout = QVBoxLayout()
            group.setLayout(group.layout)
            
            #self.group.layout.addWidget(QWidget())
            
            ## Create list of characters
            for person in chars_list:
                char_lab = QLabel(person.name)
                char_lab.layout = QHBoxLayout()
                char_lab.layout.addWidget(char_lab)
                char_lab.layout.addStretch(1)
                
                if parameters['Choose Char']:
                    ## Parameters['Person']: Subject
                    ## Person: Target
                    ## Parameters['Relation']: Relation
                    choose = ChooseButton(self, parameters['Person'], person, parameters['Relation'])
                    char_lab.layout.addWidget(choose)
                else:
                    view = ViewButton(self, person)
                    #view.clicked.connect(lambda: self.page_factory(1, { 'Person' : person, 'Char List' : self.char_list }))
                    char_lab.layout.addWidget(view)
                
                group.layout.addLayout(char_lab.layout)
            
            group.layout.addStretch(1)
    
            ## Call search method when typing in the search bar
            search.textEdited.connect(lambda: self.check_text(search))
            
            ## Create scrolling mechanics
            scroll = QScrollArea()
            
            scroll.setWidget(group)
            scroll.setWidgetResizable(True)
            
            ## Add widgets to tab
            tab.layout.addWidget(scroll)
            
            return tab, tab.layout
        return first_page
        
    def check_text(self, search):
        text = search.text().lower()
        
        temp_list = []
        
        for person in self.char_list:
            if text in person.name.lower():
                temp_list.append(person)
                
        self.page_factory(0, { 'Char List': temp_list, 'Search Text': text, 'Choose Char': False })
        
    def page_factory(self, tab_index, parameters):
        ## Removes current content from page and adds new content from tab at tab_index
        ## parameters is the list of parameters need to create a page, positionally based
        ## Parameters
            # 0: Person -> object that represents a single person
            # 1: Char_list -> list of characters to include in master list
            # 2: Search Text -> text in the search box
            # 3: Gender -> The gender of the person
        
        temp = self.layout.itemAt(0).widget()
        temp.deleteLater()
        
        temp, temp.layout = self.tab_list[tab_index](parameters)
        print('Tab: ' + str(temp) + ', Layout: ' + str(temp.layout))
        #temp.layout = tab.layout
        temp.setLayout(temp.layout)
        
        #if tab_index == 0:
            #parameters[2].setFocus()
        
        #self.layout.addLayout(temp.layout)
        self.layout.addWidget(temp)
    
    def second_factory(self):
        def second_page(parameters):
            person = parameters['Person']
            
            print(person)
            
            tab = QWidget()
            tab.layout = QVBoxLayout()
            
            title = QLabel(person.name)
            title.layout = QHBoxLayout()
            
            back = QPushButton('Back')
            back.clicked.connect(lambda: self.page_factory(0, {'Char List': self.char_list, 'Search Text': '', 'Choose Char': False}))
            
            edit = QPushButton('Edit')
            edit.clicked.connect(lambda: self.page_factory(2, {'Person': person, 'Gender': person.gender, 'Edit': True}))
            
            title.layout.addWidget(back)
            title.layout.addStretch(1)
            title.layout.addWidget(title)
            title.layout.addStretch(1)
            title.layout.addWidget(edit)
            
            tab.layout.addLayout(title.layout)
            
            if person.gender == 0:
                gen_lab = 'Male'
            else:
                gen_lab = 'Female'
            
            gender = QLabel('Gender: ' + gen_lab)
            gender.layout = QHBoxLayout()
            gender.layout.addWidget(gender)
            gender.layout.addStretch(1)
            
            tab.layout.addLayout(gender.layout)
            
            birthdate = QLabel('Birthdate: ' + person.bday)
            birthdate.layout = QHBoxLayout()
            birthdate.layout.addWidget(birthdate)
            birthdate.layout.addStretch(1)
            
            tab.layout.addLayout(birthdate.layout)
            
            deathdate = QLabel('Deathdate: ' + person.dday)
            deathdate.layout = QHBoxLayout()
            deathdate.layout.addWidget(deathdate)
            deathdate.layout.addStretch(1)
            
            tab.layout.addLayout(deathdate.layout)
            
            if not person.spouses:
                father = QLabel('Spouse(s): ' + person.father.name)
            else:
                father = QLabel('Spouse(s):')
            
            father.layout = QHBoxLayout()
            father.layout.addWidget(father)
            father.layout.addStretch(1)
            
            tab.layout.addLayout(father.layout)
            
            if person.father != self.null_person:
                father = QLabel('Father: ' + person.father.name)
            else:
                father = QLabel('Father:')
            
            father.layout = QHBoxLayout()
            father.layout.addWidget(father)
            father.layout.addStretch(1)
            
            tab.layout.addLayout(father.layout)
            
            if person.mother != self.null_person:
                mother = QLabel('Mother: ' + person.mother.name)
            else:
                mother = QLabel('Mother: ')
            
            mother.layout = QHBoxLayout()
            mother.layout.addWidget(mother)
            mother.layout.addStretch(1)
            
            tab.layout.addLayout(mother.layout)
            
            tab.layout.addStretch(1)
            
            tab.setLayout(tab.layout)
            
            return tab, tab.layout
        return second_page
    
    def pre_add_char(self, parameters):
        dlg = ChooseGenderDialog(self)
        
        print('Pre: ' + str(parameters))
        
        parameters.update({'Gender' : dlg.exec_()})
        
        self.page_factory(2, parameters)
    def third_factory(self):            
        def third_page(parameters):  
            tab = QWidget()
            tab.layout = QVBoxLayout()
            
            print('Post: ' + str(parameters))
            
            person = parameters['Person']
            
            title = QLineEdit()
            title_lab = QLabel('Name: ')
            title.layout = QHBoxLayout()
            title.layout.addStretch(3)
            title.layout.addWidget(title_lab)
            title.layout.addWidget(title)
            title.layout.addStretch(2)
            
            done_button = QPushButton('Done')
            title.layout.addWidget(done_button)
            
            tab.layout.addLayout(title.layout)

            gen = parameters['Gender']
            
            switch_button = QPushButton('Switch')
            switch_button.clicked.connect(lambda: self.page_factory(2, {'Person': person, 'Gender': 1-gen, 'Edit': parameters['Edit'] }))
            
            if gen == 0:
                gen_lab = 'Male'
            elif gen == 1:
                gen_lab = 'Female'
            else:
                gen_lab = 'Error'
                
            gender = QLabel('Gender: ' + gen_lab)
            gender.layout = QHBoxLayout()
            gender.layout.addWidget(switch_button)
            gender.layout.addWidget(gender)
            gender.layout.addStretch(1)
            
            tab.layout.addLayout(gender.layout)
            
            birthdate = QLabel('Birthdate:')
            birthdate.layout = QHBoxLayout()
            bday_text_box = QLineEdit()
            birthdate.layout.addWidget(birthdate)
            birthdate.layout.addWidget(bday_text_box)
            birthdate.layout.addStretch(1)
            
            tab.layout.addLayout(birthdate.layout)
            
            deathdate = QLabel('Deathdate:')
            deathdate.layout = QHBoxLayout()
            dday_text_box = QLineEdit()
            deathdate.layout.addWidget(deathdate)
            deathdate.layout.addWidget(dday_text_box)
            deathdate.layout.addStretch(1)
            
            tab.layout.addLayout(deathdate.layout)
            
            spouse_lab = QLabel('Spouse(s):')
            spouse = QLabel('')
            
            spouse.layout = QHBoxLayout()
            
            if person != None:
                spouse_button = QPushButton('Add')
                spouse_button.clicked.connect(lambda: self.page_factory(0, {'Person': person, 'Char List': self.char_list, 'Search Text': '', 'Choose Char': True, 'Relation': 'Spouse'}))
                spouse.layout.addWidget(spouse_button)
                spouse.layout.addWidget(spouse_lab)
                
                for s in person.spouses:
                    print(person.spouses[s])
                    spouse.setText(person.spouses[s])
                    spouse.layout.addWidget(spouse)
            else:       
                spouse.layout.addWidget(spouse_lab)
            spouse.layout.addStretch(1)
            
            
            tab.layout.addLayout(spouse.layout)
            
            father_lab = QLabel('Father:')
            father = QLabel('')
            
            father.layout = QHBoxLayout()
            
            if person != None:
                father_button = QPushButton('Add')
                father_button.clicked.connect(lambda: self.page_factory(0, {'Person': person, 'Char List': self.char_list, 'Search Text': '', 'Choose Char': True, 'Relation': 'Father'}))
                father.layout.addWidget(father_button)
            
            father.layout.addWidget(father_lab)
            father.layout.addWidget(father)
            father.layout.addStretch(1)
            
            tab.layout.addLayout(father.layout)
            
            mother_lab = QLabel('Mother:')
            mother = QLabel('')
            mother.layout = QHBoxLayout()
            
            if person != None:
                mother_button = QPushButton('Add')
                mother_button.clicked.connect(lambda: self.page_factory(0, {'Person': person, 'Char List': self.char_list, 'Search Text': '', 'Choose Char': True, 'Relation': 'Mother'}))
                mother.layout.addWidget(mother_button)
            
            mother.layout.addWidget(mother_lab)
            mother.layout.addWidget(mother)
            mother.layout.addStretch(1)
            
            tab.layout.addLayout(mother.layout)
            
            if person != None:
                #title_lab.setText('')
                title.setText(person.name)
                bday_text_box.setText(person.bday)
                dday_text_box.setText(person.dday)
                if person.father != self.null_person:
                    father_button.setText('Change')
                    father.setText(person.father.name)
                if person.mother != self.null_person:
                    mother_button.setText('Change')
                    mother.setText(person.mother.name)
                
            tab.layout.addStretch(1)
            
            print(title.text())
            
            if parameters['Edit']:
                done_button.clicked.connect(lambda: self.add_new({'Edit': parameters['Edit'], 'Person': person}))
                #edit_param = {'Edit': parameters['Edit'], 'Person': person}
            else:
                done_button.clicked.connect(lambda: self.add_new({'Edit': parameters['Edit'], 'Name': title.text(), 'Gender': gen, 'B-Day': bday_text_box.text(), 'D-Day': dday_text_box.text()}))
                #edit_param = {'Edit': parameters['Edit'], 'Name': title.text(), 'Gender': gen, 'B-Day': bday_text_box.text(), 'D-Day': dday_text_box.text()}
            
            #done_button.clicked.connect(lambda: self.add_new(edit_param))
            
            return tab, tab.layout
        return third_page
    
    def add_new(self, parameters):
        if parameters['Edit']:
            person = parameters['Person']
        else:
            print('New Name: ' + parameters['Name'])
            person = Person(self.null_person, parameters['Name'], parameters['Gender'])
            person.bday = parameters['B-Day']
            person.dday = parameters['D-Day']
            
            self.char_list.append(person)
        self.write_data()
        
        self.page_factory(1, {'Person': person })
        
    def write_data(self):
        write_list = {}
        for persons in self.char_list:
            write_list.update(persons.get_dict())
            
        with open('characters.yaml', 'w') as outfile:
            yaml.dump(write_list, outfile, default_flow_style=False)

class Person():
    def __init__(self, null, name, gender):
        self.id = uuid.uuid4().hex[:8]
        
        self.name = name # String
        self.gender = gender # 0 or 1
        self.bday = '' # String
        self.dday = '' # String
        self.father = null # Person
        self.mother = null # Person
        self.children = {} # Dictionary of ID:Names
        self.spouses = {} # Dictionary of ID:Names
        
    def addChild(self, child):
        self.children.update({child.id: child.name})
        
    def addSpouse(self, spouse):
        self.spouses.update({spouse.id: spouse.name})
        
    def get_dict(self):
        return { self.id: { 'Name': self.name, \
                            'Gender': self.gender, \
                            'Birth Date': self.bday, \
                            'Death Date': self.dday, \
                            'Spouses': self.spouses, \
                            'Father': self.father.id, \
                            'Mother': self.mother.id,
                            'Children': self.children }}
        
class ChooseGenderDialog(QMessageBox):
    def __init__(self, *args, **kwargs):
        super(ChooseGenderDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle('New Character')
        
        self.setText('New Character Gender?')
        
        #self.setTextInteractionFlags(Qt.NoTextInteraction) # (QtCore.Qt.TextSelectableByMouse)
        #self.setDetailedText('line 1\nline 2\nline 3')
        
        
        male_button = QPushButton('Male')
        female_button = QPushButton('Female')
        
        self.addButton(male_button, QMessageBox.ActionRole)
        self.addButton(female_button, QMessageBox.ActionRole)
        
        #self.buttonBox.clicked.connect(self.yes)
        #self.buttonBox.clicked.connect(self.accept)

        #self.layout = QVBoxLayout()
        #self.layout.addWidget(self.buttonBox)
        #self.setLayout(self.layout)
        
class ViewButton(QPushButton):
    def __init__(self, window, person, *args, **kwargs):
        super(ViewButton, self).__init__('View')
        
        self.window = window
        self.person = person
        
        self.installEventFilter(self)
        
    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.window.page_factory(1, {'Person': self.person})
            return True
        return False
    
class ChooseButton(QPushButton):
    def __init__(self, window, subject, target, relation, *args, **kwargs):
        super(ChooseButton, self).__init__('Choose')
        
        self.window = window
        self.target = target
        self.subject = subject
        self.relation = relation
        
        self.installEventFilter(self)
        
    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            
            if self.relation == 'Father':
                self.subject.father = self.target
                self.target.addChild(self.subject)
            elif self.relation == 'Mother':
                self.subject.mother = self.target
                self.target.addChild(self.subject)
            elif self.relation == 'Spouse':
                self.subject.addSpouse(self.target)
                self.target.addSpouse(self.subject)
            
            self.window.write_data()
            self.window.page_factory(2, {'Person': self.subject, 'Gender': self.subject.gender, 'Edit': True})
            return True
        return False

## Creates a window
window = MainWindow()

## Shows the window
window.show()
app.exec_()