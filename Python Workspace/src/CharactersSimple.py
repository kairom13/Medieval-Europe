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
import copy

## Creates a QT Application
app = QApplication([])

class MainWindow(QWidget):    
    def __init__(self, *args, **kwargs):
        ## Set up Window layout
        super(MainWindow, self).__init__(*args, **kwargs)
        
        ## Configure Window Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle('Medieval Europe')
        self.setGeometry(900, 200, 500, 500)
        
        self.layout.addWidget(QWidget())
        
        ## Read Data
        self.read_data()
        
        ## Initialize tab screen
        # First Tab: List of all characters, includes edit and view buttons, has an add button for a new character
        # Second Tab: View character, lists the info about the character. Relatives have links to their own pages. Includes and edit button for changing info
        # Third Tab: Edit Character, has line edit widgets to change 
        
        self.tab_list = []
        self.tab_list.append(self.first_factory())
        self.tab_list.append(self.second_factory())
        self.tab_list.append(self.third_factory())
        
        ## Go to First Page
        self.page_factory(0, {'Char List': self.char_list, 'Search Text': '', 'Choose Char': False})
    
    ## Read Data()
    # Gets the character data from 'characters.yaml'
    # Creates Person objects for each entry
    # Stores each person in dictionary (char_list)
    def read_data(self):
        with open("characters.yaml", 'r') as stream:
            try:
                self.char_list = {}
                init_list = yaml.safe_load(stream)
                
                if init_list != None:
                    for key in init_list:
                        char_dict = init_list[key]
                        
                        person = Person(char_dict['Name'], char_dict['Gender'])
                        
                        person.id = key
                        person.bday = char_dict['Birth Date']
                        person.dday = char_dict['Death Date']
                        person.father = char_dict['Father']
                        person.mother = char_dict['Mother']
                        person.children = char_dict['Children']
                        person.spouses = char_dict['Spouses']
                        
                        self.char_list.update({person.id: person})
                    
            except yaml.YAMLError as exc:
                print(exc)
    
    ## First Factory()
    # Displays the first page, which is the list of characters
    # Parameters is a dictionary of variable parameters necessary for the page
    def first_factory(self):
        def first_page(parameters):
            ## Create layout for the page
            tab = QWidget()
            tab.layout = QVBoxLayout()
            
            ## Get List of characters (can be modified from search, etc)
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
            
            ## Create list of characters
            for p_id in chars_list:
                person = chars_list[p_id]
                
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
    
    ## Check Text(search)
    # Modify list of characters based on search text
    def check_text(self, search):
        text = search.text().lower()
        
        temp_list = {}
        
        for p_id in self.char_list:
            person = self.char_list[p_id]
            if text in person.name.lower():
                temp_list.update({person.id: person})
                
        self.page_factory(0, { 'Char List': temp_list, 'Search Text': text, 'Choose Char': False })
    
    ## Page Factory(Tab Index, Parameters)
    # Generic function for removing current content and adding new content based on the page at tab_index
    # Parameters is a dictionary of variable parameters necessary for the page
    def page_factory(self, tab_index, parameters):
        ## Get Current content and delete it
        temp = self.layout.itemAt(0).widget()
        temp.deleteLater()
        
        ## Get new content
        temp, temp.layout = self.tab_list[tab_index](parameters)
        #print('Tab: ' + str(temp) + ', Layout: ' + str(temp.layout))
        temp.setLayout(temp.layout)
        
        self.layout.addWidget(temp)
    
    ## Second Factory()
    # Designs the second page, which views the details of an individual character
    def second_factory(self):
        def second_page(parameters):
            ## Get the character to display
            person = parameters['Person']
            #print(person)
            
            ## Create the widget
            tab = QWidget()
            tab.layout = QVBoxLayout()
            
            ## Label for the person's name
            title = QLabel(person.name)
            title.layout = QHBoxLayout()
            
            ## Go back to list of characters
            back = QPushButton('Back')
            back.clicked.connect(lambda: self.page_factory(0, {'Char List': self.char_list, 'Search Text': '', 'Choose Char': False}))
            
            ## Edit the character's details
            edit = QPushButton('Edit')
            edit.clicked.connect(lambda: self.page_factory(2, {'Person': person, 'Gender': person.gender, 'Edit': True}))
            
            title.layout.addWidget(back)
            title.layout.addStretch(1)
            title.layout.addWidget(title)
            title.layout.addStretch(1)
            title.layout.addWidget(edit)
            
            tab.layout.addLayout(title.layout)
            
            ## Label for Gender
            if person.gender == 0:
                gen_lab = 'Male'
            else:
                gen_lab = 'Female'
            
            gender = QLabel('Gender:\t' + gen_lab)
            gender.layout = QHBoxLayout()
            gender.layout.addWidget(gender)
            gender.layout.addStretch(1)
            
            tab.layout.addLayout(gender.layout)
            
            ## Label for Birth Date
            birthdate = QLabel('Birth Date:\t' + person.bday)
            birthdate.layout = QHBoxLayout()
            birthdate.layout.addWidget(birthdate)
            birthdate.layout.addStretch(1)
            
            tab.layout.addLayout(birthdate.layout)
            
            ## Label for Death Date
            deathdate = QLabel('Death Date:\t' + person.dday)
            deathdate.layout = QHBoxLayout()
            deathdate.layout.addWidget(deathdate)
            deathdate.layout.addStretch(1)
            
            tab.layout.addLayout(deathdate.layout)
            for id in self.char_list:
                print('ID: ' + id + ', Person: ' + str(self.char_list[id]))
            
            ## Label for Father
            if person.father != None:
                father = QLabel('Father:\t' + self.char_list[person.father].name)
            else:
                father = QLabel('Father:')
            
            father.layout = QHBoxLayout()
            father.layout.addWidget(father)
            father.layout.addStretch(1)
            
            tab.layout.addLayout(father.layout)
            
            ## Label for Mother
            if person.mother != None:
                mother = QLabel('Mother:\t' + self.char_list[person.mother].name)
            else:
                mother = QLabel('Mother:')
            
            mother.layout = QHBoxLayout()
            mother.layout.addWidget(mother)
            mother.layout.addStretch(1)
            
            tab.layout.addLayout(mother.layout)
            
            ## Labels for Spouses
            spouse_layout = QHBoxLayout()
            
            spouse_lab = QLabel('Spouse(s):')
            spouse_lab.layout = QVBoxLayout()
            spouse_lab.layout.addWidget(spouse_lab)
            spouse_lab.layout.addWidget(QLabel('Children:'))
            spouse_lab.layout.addStretch(1)
            
            spouse_layout.addLayout(spouse_lab.layout)
            
            ## Create a deepcopy of the children dictionary, so removals won't remove from the original.
            children = list(copy.deepcopy(person.children))
            
            print(person.name + '\'s Children: ' + str(children))
            
            ## Iterate through all spouses
            for s in person.spouses:
                print('Spouse: ' + str(s) + ' -> ' + person.spouses[s])
                spouse = QLabel(person.spouses[s])
                
                ## Have Spouse and children with that spouse as a vertical list
                spouse.layout = QVBoxLayout()
                spouse.layout.addWidget(spouse)
                
                ## Iterate through list of children to get only those who have Spouse S as a parent
                for c in person.children:
                    print('\n\nChild: ' + str(c) + ' -> ' + self.char_list[c].name)
                    print('Mother: ' + str(self.char_list[c].mother))
                    print('Father: ' + str(self.char_list[c].father))
                    print('Same Spouse? ' + str(self.char_list[c].father == s or self.char_list[c].mother == s))
                    
                    if self.char_list[c].father == s or self.char_list[c].mother == s:
                        child = QLabel(self.char_list[c].name)
                        spouse.layout.addWidget(child)
                        
                        children.remove(c)
                
                spouse.layout.addStretch(1)
                spouse_layout.addLayout(spouse.layout)
            
            
            child = QLabel('')
            child.layout = QVBoxLayout()
            child.layout.addWidget(child)
            for c in children:
                print('No Spouse Child: ' + self.char_list[c].name)
                child_lab = QLabel(self.char_list[c].name)
                child.layout.addWidget(child_lab)
            
            child.layout.addStretch(1)
            spouse_layout.addLayout(child.layout)
                    
            spouse_layout.addStretch(1)
            
            tab.layout.addLayout(spouse_layout)
            
            tab.layout.addStretch(1)
            
            tab.setLayout(tab.layout)
            
            return tab, tab.layout
        return second_page
    
    def pre_add_char(self, parameters):
        dlg = ChooseGenderDialog(self)
        
        parameters.update({'Gender' : dlg.exec_()})
        
        self.page_factory(2, parameters)
        
    def third_factory(self):            
        def third_page(parameters):  
            tab = QWidget()
            tab.layout = QVBoxLayout()
            tab.layout.setSpacing(0)
            
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
            
            birthdate = QLabel('Birthdate:\t')
            birthdate.layout = QHBoxLayout()
            bday_text_box = QLineEdit()
            birthdate.layout.addWidget(birthdate)
            birthdate.layout.addWidget(bday_text_box)
            birthdate.layout.addStretch(1)
            
            tab.layout.addLayout(birthdate.layout)
            
            deathdate = QLabel('Deathdate:\t')
            deathdate.layout = QHBoxLayout()
            dday_text_box = QLineEdit()
            deathdate.layout.addWidget(deathdate)
            deathdate.layout.addWidget(dday_text_box)
            deathdate.layout.addStretch(1)
            
            tab.layout.addLayout(deathdate.layout)
            
            father_lab = QLabel('Father:\t')
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
            
            mother_lab = QLabel('Mother:\t')
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
            
            ## Label for Spouses
            spouse_layout = QHBoxLayout()
            
            spouse_button = QPushButton('Add')
            spouse_layout.addWidget(spouse_button)
            
            spouse_lab = QLabel('Spouse(s):')
            spouse_layout.addWidget(spouse_lab)
            
            ## Iterate through all spouses
            for s in person.spouses:
                print('Spouse: ' + str(s) + ' -> ' + person.spouses[s])
                spouse = QLabel(person.spouses[s])
                
                ## Have Spouse and children with that spouse as a vertical list
                spouse.layout = QVBoxLayout()
                spouse.layout.addWidget(spouse)
                
                remove = QPushButton('Remove')
                spouse.layout.addWidget(remove)
                
                spouse_layout.addLayout(spouse.layout)
                
            spouse_layout.addStretch(1)
            tab.layout.addLayout(spouse_layout)
            
            ## Label for Children
            child = QLabel('Children:')
            child.layout = QHBoxLayout()
            
            child_button = QPushButton('Add')
            child.layout.addWidget(child_button)
            child.layout.addWidget(child)
            
            child.layout.addStretch(1)
            
            tab.layout.addLayout(child.layout)
            
            children_layout = QVBoxLayout()
            for c in person.children:
                child_layout = QHBoxLayout()
                remove_child = QPushButton('Remove')
                child_layout.addWidget(remove_child)
                
                child_lab = QLabel(self.char_list[c].name)
                child_layout.addWidget(child_lab)
                
                child_layout.addStretch(1)
            
                children_layout.addLayout(child_layout)

            tab.layout.addLayout(children_layout)
            
            if person != None:
                #title_lab.setText('')
                title.setText(person.name)
                bday_text_box.setText(person.bday)
                dday_text_box.setText(person.dday)
                if person.father != None:
                    father_button.setText('Change')
                    father.setText(self.char_list[person.father].name)
                if person.mother != None:
                    mother_button.setText('Change')
                    mother.setText(self.char_list[person.mother].name)
                
            tab.layout.addStretch(1)
            
            print(title.text())
            
            if parameters['Edit']:
                done_button.clicked.connect(lambda: self.add_new({'Edit': parameters['Edit'], 'Person': person}))
            else:
                done_button.clicked.connect(lambda: self.add_new({'Edit': parameters['Edit'], 'Name': title.text(), 'Gender': gen, 'B-Day': bday_text_box.text(), 'D-Day': dday_text_box.text()}))

            return tab, tab.layout
        return third_page
    
    def add_new(self, parameters):
        if parameters['Edit']:
            person = parameters['Person']
        else:
            print('New Name: ' + parameters['Name'])
            person = Person(parameters['Name'], parameters['Gender'])
            person.bday = parameters['B-Day']
            person.dday = parameters['D-Day']
            
            self.char_list.update({person.id: person})
        self.write_data()
        
        self.page_factory(1, {'Person': person })
        
    def write_data(self):
        write_list = {}
        for p_id in self.char_list:
            person = self.char_list[p_id]
            print(person)
            write_list.update(person.get_dict())
            
        with open('characters.yaml', 'w') as outfile:
            yaml.dump(write_list, outfile, default_flow_style=False)

class Person():
    def __init__(self, name, gender):
        self.id = uuid.uuid4().hex[:8]
        
        self.name = name # String
        self.gender = gender # 0 or 1
        self.bday = '' # String
        self.dday = '' # String
        self.father = None # String ID
        self.mother = None # String ID
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
                            'Father': self.father, \
                            'Mother': self.mother,
                            'Children': self.children }}
        
class ChooseGenderDialog(QMessageBox):
    def __init__(self, *args, **kwargs):
        super(ChooseGenderDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle('New Character')
        
        self.setText('New Character Gender?')
        
        male_button = QPushButton('Male')
        female_button = QPushButton('Female')
        
        self.addButton(male_button, QMessageBox.ActionRole)
        self.addButton(female_button, QMessageBox.ActionRole)
        
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
                self.subject.father = self.target.id
                self.target.addChild(self.subject)
            elif self.relation == 'Mother':
                self.subject.mother = self.target.id
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