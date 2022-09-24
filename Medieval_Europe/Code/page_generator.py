"""
Created on Dec 23, 2021

@author: kairom13
"""

from Medieval_Europe.Code.Widgets.Buttons import *
from Medieval_Europe.Code.Widgets.Displays import *
from Medieval_Europe.Code.Widgets.Interactives import *
from Medieval_Europe.Code.Reigns import *


class PageGenerator:
    def __init__(self, window):
        self.window = window
        self.logger = self.window.logger

        self.logger.log('Code', 'Created Page Generator Object')

    def get_page(self, method_choice, parameters):
        return getattr(self, method_choice)(parameters)

    ## Pages:
    # objectListPage - list of objects; including search feature, dropdown for object type, and button to view details
    # displayPersonPage - display details for the given person; including relatives, titles, and button to edit
    # editPersonPage - edit details for the given person; editable extension of displayed values
    # displayTitlePage - display details for the given title; including list of reigns and links to rulers
    # editTitlePage - edit details for the given title
    # chooseReignPage - Choose reign from a set list
    # displayDynastyPage - display family tree for given dynasty
    # displayPlacePage - display details for a given place
    # editPlacePage - edit details for the given place

    ## objectListPage()
    # Displays the first page, which is the list of objects
    # Parameters is a dictionary of variable parameters necessary for the page
    # Expected Parameters:
    # Object Type
    # Search Text
    # Page Type
    # For choosing object:
    # Relation
    # Person

    def view_object_list(self, parameters):
        ## Create Widget and Layout
        page = QWidget()
        page_layout = QGridLayout()
        page.setLayout(page_layout)
        page_layout.setColumnStretch(0, 2)
        page_layout.setColumnStretch(1, 3)
        page_layout.setColumnStretch(2, 2)

        page_layout.setRowStretch(0, 1)
        page_layout.setRowStretch(1, 10)

        page_layout.setSpacing(10)

        headerLayout = QHBoxLayout()

        object_type = parameters['Object Type']
        object_list = self.window.objectLists[object_type]
        self.logger.log('Code', 'Viewing list of ' + object_type)

        choose_object_type = ObjectType({'Window': self.window, 'Object Type': object_type, 'Object List': object_list})
        self.logger.log('Detailed', 'Created Combo Box to switch between object types')

        ## Widget for searching for specific characters
        search = SearchBar(self.window, parameters['Search Text'])
        self.logger.log('Detailed', 'Created Search Bar')

        headerLayout.addWidget(choose_object_type)
        headerLayout.addStretch(1)

        headerLayout.addWidget(search)
        headerLayout.addStretch(1)

        ## Include button to add new objects
        add_button = QPushButton('Add')
        add_button.clicked.connect(lambda: self.window.prepareNewObject({'Object Type': object_type}))
        headerLayout.addWidget(add_button)
        self.logger.log('Detailed', 'Created Add button for new objects of type ' + object_type)

        page_layout.addLayout(headerLayout, 0, 1, 1, 1)  # row 0, column 1, spans 1 row, spans 1 column

        list_layout = QVBoxLayout()

        list_layout.addWidget(QLabel('Number of ' + str(object_type) + 's: ' + str(len(object_list))), alignment=Qt.AlignHCenter)

        ## Groupbox that lists every object
        group = QWidget()
        group.layout = QVBoxLayout()
        group.setLayout(group.layout)
        group.layout.setSpacing(0)

        ## Create list of objects
        self.window.widgets = []

        self.logger.log('Code', 'Adding list of ' + object_type + 's')

        for o in object_list:
            obj = object_list[o]

            button = ObjectButton({'Window': self.window, 'Logger': self.logger, 'Subject': obj, 'Object Type': object_type, 'Page Type': 'View'})
            object_label = ObjectLabelWidget(obj, object_type, button)
            self.window.widgets.append(object_label)

            group.layout.addWidget(object_label)

        group.layout.addStretch(1)

        ## Create scrolling mechanics
        scroll = QScrollArea()

        scroll.setWidget(group)
        scroll.setWidgetResizable(True)

        list_layout.addWidget(scroll)
        self.logger.log('Detailed', 'Added scroll area')

        ## Add widgets to tab
        if object_type == 'Place':
            page_layout.addLayout(list_layout, 1, 0, 1, 1)  # row 1, column 0, spans 1 row, spans 1 column
            self.logger.log('Detailed', 'List of places moved to left side to make room for place map')
        else:
            page_layout.addLayout(list_layout, 1, 1, 1, 1)  # row 1, column 1, spans 1 row, spans 1 column

        ############ Map Group #############
        if object_type == 'Place':
            self.logger.log('Code', 'Adding map of places')
            # Add Map to right side lower 2/3ds
            mapGroup = QGroupBox('Place Map')
            page_layout.addWidget(mapGroup, 1, 1, 1, 2)  # row 1, column 1, spans 1 rows, spans 2 column

            mapLayout = QVBoxLayout(mapGroup)

            placeMap = PlaceMap(self.window, {})
            mapLayout.addWidget(placeMap)
            self.logger.log('Detailed', 'Successfully created place map and added to view object list')

        return page

    def choose_object_list(self, parameters):
        ## Create Widget and Layout
        page = QWidget()
        page_layout = QGridLayout()
        page.layout = QVBoxLayout()
        page.setLayout(page_layout)
        page_layout.addLayout(page.layout, 0, 1)
        page_layout.setColumnStretch(0, 2)
        page_layout.setColumnStretch(1, 3)
        page_layout.setColumnStretch(2, 2)
        page_layout.setSpacing(0)

        headerLayout = QHBoxLayout()

        object_type = parameters['Object Type']
        subject = parameters['Subject']

        if 'Object List' in parameters:
            object_list = parameters['Object List']
            self.logger.log('Detailed', 'Custom list of ' + object_type + ' used for choosing')
        else:
            self.logger.log('Detailed', 'Standard list of ' + object_type + ' used for choosing')
            object_list = self.window.objectLists[object_type]

        ## Widget for searching for specific characters
        search = SearchBar(self.window, parameters['Search Text'])
        self.logger.log('Detailed', 'Created Search Bar')

        cancel = QPushButton('Cancel')
        headerLayout.addWidget(cancel)
        headerLayout.addStretch(1)
        self.logger.log('Detailed', 'Added cancel button')

        button_params = {}
        if parameters['Connection'] == 'Child':
            spouse_choice = SpouseChoice({'Window': self.window, 'Subject': subject})
            headerLayout.addWidget(spouse_choice)
            self.logger.log('Detailed', 'Added spouse choice combo box')

            button_params.update({'Spouse': spouse_choice})

        headerLayout.addStretch(1)

        ## Add reminder label about who the user is choosing a relationship for
        self.logger.log('Code', 'Choosing ' + parameters['Connection'] + ' for ' + subject.getName())
        reminder_label = QLabel('Choosing ' + parameters['Connection'] + ' for ' + subject.getName())
        reminder_layout = QVBoxLayout()
        reminder_layout.addWidget(reminder_label, alignment=Qt.AlignCenter)
        reminder_layout.addWidget(search, alignment=Qt.AlignCenter)

        headerLayout.addLayout(reminder_layout)
        headerLayout.addStretch(2)

        #print('Is Person or Title:')
        #print(isinstance(parameters['Subject'], Person) or isinstance(parameters['Subject'], Title))

        if parameters['Connection'] in ('Reign', 'Place'):
            self.logger.log('Detailed', 'When cancelling, go back to edit the place of {' + subject.getID() + '}')
            cancel.clicked.connect(lambda: self.window.page_factory('edit_place_page', {'Place': subject}))
        else:
            if parameters['Connection'] in ('Predecessor', 'Successor'):
                self.logger.log('Detailed', 'When cancelling, go back to edit the person of {' + subject.getConnection('Person').getID() + '}')
                cancel.clicked.connect(lambda: self.window.page_factory('edit_person_page', {'Person': subject.getConnection('Person')}))
            elif parameters['Connection'] in ('Title Predecessor', 'Title Successor'):
                self.logger.log('Detailed', 'When cancelling, go back to edit the title of {' + subject.getID() + '}')
                cancel.clicked.connect(lambda: self.window.page_factory('edit_title_page', {'Title': subject}))
            else:
                self.logger.log('Detailed', 'When cancelling, go back to edit the person of {' + subject.getID() + '}')
                cancel.clicked.connect(lambda: self.window.page_factory('edit_person_page', {'Person': subject}))

                self.logger.log('Code', 'Including Add new object button')
                ## Include button to add new objects
                add_button = QPushButton('Add')
                headerLayout.addWidget(add_button)

                add_params = button_params
                add_params.update({'Object Type': object_type, 'Subject': subject, 'Connection': parameters['Connection']})
                add_button.clicked.connect(lambda: self.window.prepareNewObject(add_params))

        page.layout.addLayout(headerLayout)

        ## Groupbox that lists every object
        group = QWidget()
        group.layout = QVBoxLayout()
        group.setLayout(group.layout)

        ## Create list of objects
        self.window.widgets = []

        self.logger.log('Code', 'Add list of objects')

        # Possible scenarios to display
        # 1) Person adding relation
        #   - List of objects will be people
        #   - Subject will be person requesting relations
        #   - Only restriction is cannot be self
        #   - Valid connections: father, mother, child, spouse
        # 2) Person adding new reign (title)
        #   - List of objects will be titles
        #   - Subject will be person adding a new reign
        #   - No restriction on options, can have more than one reign with the same title
        #   - Valid connections: title
        # 3) Person adding a predecessor or successor to an existing reign
        #   - List of objects will be reigns within the given title
        #   - Subject will be the reign getting a new predecessor or successor
        #   - Restrict to only reigns with the given title and who don't have the reciprocal of the connection
        #       i.e. if getting predecessor, look for only available successors, vice versa
        #   - Valid connections: predecessor, successor
        # 4) Place adding a new reign
        #   a) First choose a title (cannot add a new one)
        #       - List of objects will be titles
        #       - Subject will be place
        #       - No restriction on titles
        #       - Valid connections: reign
        #   b) Then choose a reign within the title
        #       - List of objects will be reigns within the given title
        #       - Subject will be place
        #       - Restrict to only reigns with the given title and who aren't already chosen
        #       - Valid connections: reign
        # 5) Choosing a reign to merge with
        #   - List of objects will be valid reigns to merge with
        #       i.e. is not the current reign and is not a junior reign
        #   - Subject will be reign seeking a senior
        #   - Restricted by object list parameter
        #   - Valid connections: reign

        for o in object_list:
            obj = object_list[o]

            # Just make sure the subject is not in the list to choose
            if subject.getID() != o:
                button_params.update({'Window': self.window, 'Subject': subject, 'Object Type': object_type, 'Target': obj, 'Page Type': 'Choose', 'Connection': parameters['Connection']})
                button = ObjectButton(button_params)

                object_label = ObjectLabelWidget(obj, object_type, button)
                self.window.widgets.append(object_label)

                group.layout.addWidget(object_label)

        group.layout.addStretch(1)

        ## Create scrolling mechanics
        scroll = QScrollArea()

        scroll.setWidget(group)
        scroll.setWidgetResizable(True)

        ## Add widgets to tab
        page.layout.addWidget(scroll)

        return page

    ## displayPersonPage()
    # Designs the second page, which views the details of an individual character
    # Expected Parameters:
    # Person

    def display_person_page(self, parameters):
        ## Create Page Widget
        page = QWidget()

        ## Create All Layouts for this Page
        page.layout = QGridLayout()  ## Overall layout for the page
        page.setLayout(page.layout)

        header_layout = QHBoxLayout()  ## The layout at the top of the page
        page.layout.addLayout(header_layout, 0, 0, 1, 2)  # row 0, column 0, spans 1 row, spans 2 columns

        page.layout.setColumnStretch(0, 1)  # column 0 is stretched to 1
        page.layout.setColumnStretch(1, 2)  # column 1 is stretched to 2

        ## Get the person to display
        person = parameters['Person']

        ## Label for the person's name
        self.logger.log('Code', 'Displaying {' + person.getID() + '}')

        ############ Header #############
        name = QLabel(person.getName())

        ## Go back to list of characters
        back = QPushButton('List of People')
        back.clicked.connect(lambda: self.window.page_factory('view_object_list', {'Object Type': 'Person', 'Search Text': ''}))
        self.logger.log('Detailed', 'Including button to go back to list of people')

        ## Edit the character's details
        edit = QPushButton('Edit')
        edit.clicked.connect(lambda: self.window.page_factory('edit_person_page', {'Person': person}))
        self.logger.log('Detailed', 'Including button to edit {' + person.getID() + '}')

        ## Display their name
        header_layout.addWidget(back)
        header_layout.addStretch(1)
        header_layout.addWidget(name)
        header_layout.addStretch(1)
        header_layout.addWidget(edit)

        self.logger.log('Code', 'Add Name Widget', True)

        ############ Info Group #############
        infoGroup = QGroupBox('Personal Information')
        infoGroup.layout = QVBoxLayout()
        infoGroup.setLayout(infoGroup.layout)

        ## Get dictionary for static labels
        staticLabels = person.getStaticLabels()

        def display_relation_graph():
            self.logger.log('Code', 'Clicked to display relations')

            import networkx as nx
            import matplotlib.pyplot as plt
            from networkx.drawing.nx_pydot import graphviz_layout

            G = nx.DiGraph()
            labels = {}

            personList = {}

            def getRelations(sub_person, sub_personList, maxLevel, level):
                if sub_person is None:
                    self.logger.log('Detailed', 'Subject Person is None', True)
                    return sub_personList
                elif level > maxLevel:
                    self.logger.log('Detailed', 'Level ' + str(level) + ' is greater than the max level: ' + str(maxLevel), True)
                    return sub_personList
                elif sub_person.getID() not in sub_personList:
                    self.logger.log('Detailed', 'Adding {' + sub_person.getID() + '} to dictionary of relatives', True)
                    sub_personList.update({sub_person.getID(): sub_person})
                    for c_id in sub_person.connectionDict:
                        if sub_person.connection('Get', c_id) in ('Father', 'Mother', 'Spouse', 'Child'):
                            connect_object = self.window.get_object(c_id)
                            sub_personList = getRelations(connect_object, sub_personList, maxLevel, level + 1)

                    return sub_personList
                else:
                    self.logger.log('Detailed', '{' + sub_person.getID() + '} is already in the dictionary of relatives.', True)
                    return sub_personList

            personList = getRelations(person, personList, 5, 0)

            #displayRelations = DisplayRelationGraph(self.window, personList)

            drawSpouses = True

            self.logger.log('Detailed', 'Creating connections for relations graph')
            for p_id, personObject in personList.items():
                edge = False
                parents = personObject.getParents()
                if parents[0] is not None and parents[0] in personList:
                    self.logger.log('Detailed', 'Drawing {' + parents[0] + '} as the father of {' + p_id + '}', True)
                    G.add_edge(parents[0], p_id, color='r')
                    edge = True

                if parents[1] is not None and parents[1] in personList:
                    self.logger.log('Detailed', 'Drawing {' + parents[1] + '} as the mother of {' + p_id + '}', True)
                    G.add_edge(parents[1], p_id, color='b')
                    edge = True

                if drawSpouses:
                    for s_id in personObject.spouses:
                        if s_id != 'unknown_spouse' and s_id in personList:
                            self.logger.log('Detailed', 'Drawing {' + s_id + '} as the spouse of {' + p_id + '}', True)
                            G.add_edge(p_id, s_id, color='g')
                            edge = True

                if not edge:
                    self.logger.log('Detailed', 'No drawable connection for {' + p_id + '}', True)
                    G.add_node(p_id)

                labels[p_id] = personObject.getAttribute('Name')

            colors = nx.get_edge_attributes(G, 'color').values()
            #pos = nx.kamada_kawai_layout(G)
            #pos = nx.random_layout(G)
            #pos = nx.spring_layout(G)
            pos = graphviz_layout(G, prog="neato")

            # for p_id in pos:
            #     if p_id in labels:
            #         print(str(p_id) + ': Pos: ' + str(pos[p_id]) + ', Label: ' + str(labels[p_id]))
            #
            #     else:
            #         print('POSITION BUT NO LABEL: ' + str(p_id))
            #
            # for p_id in labels:
            #     if p_id not in pos:
            #         print('LABEL BUT NO POSITION: ' + str(p_id))
            #         labels.pop(p_id)

            nx.draw(G, pos=pos, with_labels=False, edge_color=colors, node_size=10, width=0.5)
            nx.draw_networkx_labels(G, pos, labels, font_size=8, alpha=1)
            self.logger.log('Detailed', 'Drew relations graph')

            fig = plt.gcf()
            fig.set_size_inches(10, 10)

            plt.show()

        for s in staticLabels:
            label = QLabel(s + ':\t' + staticLabels[s])
            self.logger.log('Code', 'Add ' + s + ': ' + str(staticLabels[s]), True)
            label.layout = QHBoxLayout()
            label.layout.addWidget(label)
            label.layout.addStretch(1)

            if s == 'Gender':
                displayGraph = QPushButton('Display Relations')
                displayGraph.clicked.connect(display_relation_graph)
                label.layout.addWidget(displayGraph)

            infoGroup.layout.addLayout(label.layout)

        ## Add Father Widget
        fatherLayout = QHBoxLayout()
        fatherLayout.addWidget(ParentWidget(self.window, False, 'Father', person))
        fatherLayout.addStretch(1)

        infoGroup.layout.addLayout(fatherLayout)

        ## Add Mother Widget
        motherLayout = QHBoxLayout()
        motherLayout.addWidget(ParentWidget(self.window, False, 'Mother', person))
        motherLayout.addStretch(1)

        infoGroup.layout.addLayout(motherLayout)

        for p in ('Father', 'Mother'):
            if person.getParents(p)[0] is not None:
                self.logger.log('Code', 'Add ' + p + ': {' + person.getParents(p)[0] + '}', True)
            else:
                self.logger.log('Code', 'Add ' + p + ': None', True)

        ## Labels for Spouses
        spouse_layout = QHBoxLayout()

        spouse_lab = QLabel('Spouse(s):')
        spouse_lab.layout = QVBoxLayout()
        spouse_lab.layout.addWidget(spouse_lab)
        spouse_lab.layout.addWidget(QLabel('Children:'))
        spouse_lab.layout.addStretch(1)

        spouse_layout.addLayout(spouse_lab.layout)

        ## Iterate through all spouses
        for s in person.spouses:
            if s == 'unknown_spouse':
                spouse = QLabel('')
            else:
                spouse = ObjectLabel(self.window, self.window.get_object(s), 'Linker Object')
                self.logger.log('Code', 'Add Spouse: {' + s + '}', True)

            ## Have Spouse and children with that spouse as a vertical list
            spouse.layout = QVBoxLayout()
            spouse.layout.addWidget(spouse)

            ## Iterate through list of children for the given spouse
            for c in person.spouses[s]:
                child = ObjectLabel(self.window, self.window.get_object(c), 'Linker Object')
                spouse.layout.addWidget(child)

                if s == 'unknown_spouse':
                    self.logger.log('Code', 'Add Child With No Spouse: {' + c + '}', True)
                else:
                    self.logger.log('Code', 'Add Child With {' + s + '}: {' + c + '}', True)

            spouse.layout.addStretch(1)
            spouse_layout.addLayout(spouse.layout)

        spouse_layout.addStretch(1)

        infoGroup.layout.addLayout(spouse_layout)

        page.layout.addWidget(infoGroup, 1, 0, 1, 1)  # row 1, column 0, spans 1 row, spans 1 column
        page.layout.setRowStretch(1, 1)  # row 2 is stretched to 1

        ############ Title Group #############
        titleGroup = QGroupBox('Held Titles')
        titleGroup.layout = QVBoxLayout()
        titleGroup.setLayout(titleGroup.layout)

        titleScroll = QWidget()
        titleScroll.layout = QVBoxLayout()
        titleScroll.setLayout(titleScroll.layout)

        for r, reignObject in person.reignList.items():
            if not reignObject.isJunior:
                titleScroll.layout.addWidget(ReignWidget({'Window': self.window, 'Object Type': 'Person', 'Reign': reignObject, 'Edit': False, 'Logger': self.logger}))

        titleScroll.layout.addStretch(1)

        ## Create scrolling mechanics
        scroll = QScrollArea()

        scroll.setWidget(titleScroll)
        scroll.setWidgetResizable(True)

        titleGroup.layout.addWidget(scroll)
        page.layout.addWidget(titleGroup, 2, 0, 1, 1)  # row 2, column 0, spans 2 rows, spans 1 column
        page.layout.setRowStretch(2, 2)  # row 2 is stretched to 2

        ############ Map Group #############
        # Add Map to right side lower 2/3ds
        mapGroup = QGroupBox('Place Map')
        page.layout.addWidget(mapGroup, 2, 1, 1, 1)  # row 2, column 1, spans 2 rows, spans 1 column

        mapLayout = QVBoxLayout(mapGroup)

        placeList = {}
        for r, reign in person.reignList.items():
            for p, place in reign.placeList.items():
                if p not in placeList:
                    placeList.update({p: place})
                    self.logger.log('Detailed', 'Added {' + p + '} as a place for {' + person.getID() + '}')

        placeMap = PlaceMap(self.window, placeList)
        mapLayout.addWidget(placeMap)
        self.logger.log('Detailed', 'Successfully created and added the map of places')

        ############ Events Group #############
        page.layout.addWidget(EventsWidget(self.window, False, person), 1, 1, 1, 1)
        self.logger.log('Detailed', 'Successfully created and added the events widget in display mode')

        return page

    ## editPersonPage()
    # Person object should never be null
    # Expected Parameters;
    # Person
    def edit_person_page(self, parameters):
        self.logger.log('Code', 'Editing Person: {' + parameters['Person'].getID() + '}')
        ## Create Page Widget
        page = QWidget()

        ## Create All Layouts for this Page
        page.layout = QGridLayout()  ## Overall layout for the page
        page.setLayout(page.layout)

        header_layout = QHBoxLayout()  ## The layout at the top of the page
        page.layout.addLayout(header_layout, 0, 0, 1, 2)  # row 0, column 0, spans 1 row, spans 2 columns

        page.layout.setRowStretch(1, 1)
        page.layout.setRowStretch(2, 1)

        page.layout.setColumnStretch(0, 1)  # column 0 is stretched to 1
        page.layout.setColumnStretch(1, 1)  # column 1 is stretched to 1

        person = parameters['Person']

        def display_person():
            self.window.write_data()
            self.window.page_factory('display_person_page', {'Person': person})

        nameLayout = QVBoxLayout()

        ## Edit the name of the person
        nameLayout.addWidget(AttributeWidget(self.window, True, 'Name', person))
        self.logger.log('Detailed', 'Successfully created and added the attribute widget for Name', True)

        ## Edit the nickname of the person
        nameLayout.addWidget(AttributeWidget(self.window, True, 'Nickname', person))
        self.logger.log('Detailed', 'Successfully created and added the attribute widget for Nickname', True)

        header_layout.addStretch(1)
        header_layout.addLayout(nameLayout)
        header_layout.addStretch(1)

        ## Button to press when finished
        done_button = QPushButton('Done')
        done_button.clicked.connect(display_person)
        self.logger.log('Detailed', 'Added button to complete editing')

        done_button.layout = QVBoxLayout()
        done_button.layout.addWidget(done_button)
        done_button.layout.addStretch(1)
        header_layout.addLayout(done_button.layout)

        ################ Info Group ################

        infoGroup = QGroupBox('Personal Information')
        infoGroup.layout = QVBoxLayout()
        infoGroup.setLayout(infoGroup.layout)
        infoGroup.layout.setSpacing(0)

        ## Edit Birth and Death dates
        infoGroup.layout.addWidget(AttributeWidget(self.window, True, 'Birth Date', person))
        self.logger.log('Detailed', 'Successfully created and added the attribute widget for Birth Date', True)
        infoGroup.layout.addWidget(AttributeWidget(self.window, True, 'Death Date', person))
        self.logger.log('Detailed', 'Successfully created and added the attribute widget for Death Date', True)

        ## Button to switch gender (remakes current page with update)
        switchButton = SwitchGenderButton(self.window, self.logger, person)

        if person.gender == 0:
            gen = 'Man'
        else:
            gen = 'Woman'

        genderLabel = QLabel('Gender:\t' + gen)
        genderLabel.layout = QHBoxLayout()
        genderLabel.layout.addWidget(switchButton)
        genderLabel.layout.addSpacing(10)
        genderLabel.layout.addWidget(genderLabel)
        genderLabel.layout.addStretch(1)

        infoGroup.layout.addLayout(genderLabel.layout)
        self.logger.log('Detailed', 'Added label for the subject\'s gender')

        ## Add Father Widget
        fatherLayout = QHBoxLayout()
        fatherLayout.addWidget(ParentWidget(self.window, True, 'Father', person))
        self.logger.log('Detailed', 'Successfully created and added the parent widget for Father', True)
        fatherLayout.addStretch(1)

        infoGroup.layout.addLayout(fatherLayout)

        ## Add Mother Widget
        motherLayout = QHBoxLayout()
        motherLayout.addWidget(ParentWidget(self.window, True, 'Mother', person))
        self.logger.log('Detailed', 'Successfully created and added the parent widget for Mother', True)
        motherLayout.addStretch(1)

        infoGroup.layout.addLayout(motherLayout)

        ## Label for Spouses
        spouse_layout = QHBoxLayout()

        ## Choose a spouse from the list of characters (calls first page to choose character)
        spouse_button = QPushButton('Add')
        spouse_button.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Person', 'Search Text': '', 'Subject': person, 'Connection': 'Spouse'}))
        spouse_layout.addWidget(spouse_button)
        self.logger.log('Detailed', 'Created button to add new spouse')

        spouse_lab = QLabel('Spouse(s):')
        spouse_layout.addSpacing(10)
        spouse_layout.addWidget(spouse_lab)

        childrenList = []

        ## Iterate through all spouses
        for s in person.spouses:
            for c in person.spouses[s]:
                childrenList.append(c)

            if s != 'unknown_spouse':
                # print('Spouse: ' + str(s) + ' -> ' + person.spouses[s]['Name'])

                spouseObject = self.window.get_object(s)
                spouse = QLabel(spouseObject.getAttribute('Name'))
                self.logger.log('Code', 'Can modify spouse: {' + s + '}', True)

                sp_layout = QHBoxLayout()
                sp_layout.addStretch(1)
                sp_layout.addWidget(spouse)
                sp_layout.addStretch(1)

                ## Have Spouse and children with that spouse as a vertical list
                spouse.layout = QVBoxLayout()
                spouse.layout.addLayout(sp_layout)

                remove = RemoveConnectionButton(self.window, person, self.window.get_object(s))
                self.logger.log('Detailed', 'Successfully created and added button to remove spousal connection between '
                                            '{' + person.getID() + '} and {' + s + '}', True)

                spouse.layout.addWidget(remove)

                spouse_layout.addLayout(spouse.layout)

        spouse_layout.addStretch(1)
        infoGroup.layout.addLayout(spouse_layout)

        ## Label for Children
        child = QLabel('Children:')
        child.layout = QHBoxLayout()

        child_button = QPushButton('Add')
        child_button.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Person', 'Search Text': '', 'Subject': person, 'Connection': 'Child'}))
        child.layout.addWidget(child_button)
        child.layout.addSpacing(10)
        child.layout.addWidget(child)
        self.logger.log('Detailed', 'Created button to add new child')

        child.layout.addStretch(1)

        infoGroup.layout.addLayout(child.layout)

        children_layout = QVBoxLayout()
        for c in childrenList:
            child_layout = QHBoxLayout()
            remove_child = RemoveConnectionButton(self.window, person, self.window.get_object(c))
            self.logger.log('Detailed', 'Successfully created and added button to remove child connection between '
                                        '{' + person.getID() + '} and {' + c + '}', True)
            child_layout.addWidget(remove_child)
            child_layout.addSpacing(10)

            child_lab = QLabel(self.window.get_object(c).getAttribute('Name'))
            self.logger.log('Code', 'Can modify child: {' + c + '}', True)
            child_layout.addWidget(child_lab)

            child_layout.addStretch(1)

            children_layout.addLayout(child_layout)

        infoGroup.layout.addLayout(children_layout)

        infoGroup.layout.addStretch(1)

        page.layout.addWidget(infoGroup, 1, 0)

        ################ Title Group ################
        titleGroup = QGroupBox('Held Titles')
        titleGroup.layout = QVBoxLayout()
        titleGroup.setLayout(titleGroup.layout)
        titleGroup.layout.setSpacing(0)

        titleScrollWidget = QWidget()
        titleScrollWidget.layout = QVBoxLayout()
        titleScrollWidget.setLayout(titleScrollWidget.layout)

        numReigns = len(person.reignList)
        self.logger.log('Code', 'Can edit ' + str(numReigns) + ' Reigns')
        if numReigns > 1:
            self.logger.log('Code', 'Include ability to merge')

        for r, reignObject in person.reignList.items():
            if not reignObject.isJunior:
                titleScrollWidget.layout.addWidget(
                    ReignWidget({'Window': self.window, 'Object Type': 'Person', 'Reign': reignObject, 'Edit': True, 'Logger': self.logger}))
        self.logger.log('Detailed', 'Successfully created and added widget to display reigns', True)

        ## For A New Reign
        addButton = QPushButton('Add')
        addButton.layout = QHBoxLayout()
        addButton.layout.addStretch(1)
        addButton.layout.addWidget(addButton)
        addButton.layout.addStretch(1)

        # Choose title to add from list
        addButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Title', 'Search Text': '', 'Subject': person, 'Connection': 'Title'}))

        titleScrollWidget.layout.addWidget(addButton, alignment=Qt.AlignHCenter)
        titleScrollWidget.layout.addStretch(1)
        self.logger.log('Detailed', 'Added button to add a new reign')

        ## Create scrolling mechanics
        titleScroll = QScrollArea()

        titleScroll.setWidget(titleScrollWidget)
        titleScroll.setWidgetResizable(True)

        titleGroup.layout.addWidget(titleScroll)

        page.layout.addWidget(titleGroup, 2, 0)

        ############ Events Group #############
        page.layout.addWidget(EventsWidget(self.window, True, person), 1, 1)
        self.logger.log('Detailed', 'Successfully created and added the events widget in edit mode', True)

        # ################ Place Group ################
        # reignGroup = QGroupBox('Places')
        # reignGroup.layout = QVBoxLayout()
        # reignGroup.setLayout(reignGroup.layout)
        # reignGroup.layout.setSpacing(0)
        #
        # addReignButton = QPushButton('Add')
        # # Choose title to add from list
        # addReignButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Place', 'Search Text': '', 'Subject': person, 'Connection': 'Reign'}))
        #
        # addButtonLayout = QHBoxLayout()
        # addButtonLayout.addStretch(1)
        # addButtonLayout.addWidget(addReignButton)
        # reignGroup.layout.addLayout(addButtonLayout)
        #
        # reignScrollWidget = QWidget()
        # reignScrollWidget.layout = QVBoxLayout()
        # reignScrollWidget.setLayout(reignScrollWidget.layout)
        #
        # for p, place in person.placeList.items():
        #     placeLabel = QHBoxLayout()
        #     placeLabel.addStretch(1)
        #
        #     info = place.getAttribute('Name') + ' (' + place.getAttribute('Latitude') + ', ' + place.getAttribute('Longitude') + ')'
        #
        #     placeLabel.addWidget(QLabel(info))
        #
        #     placeLabel.addStretch(1)
        #
        #     reignScrollWidget.layout.addLayout(placeLabel)
        #
        # reignScrollWidget.layout.addStretch(1)
        #
        # ## Create scrolling mechanics
        # reignScroll = QScrollArea()
        #
        # reignScroll.setWidget(reignScrollWidget)
        # reignScroll.setWidgetResizable(True)
        #
        # reignGroup.layout.addWidget(reignScroll)
        #
        # page.layout.addWidget(reignGroup, 2, 1)  # Add at row 2 and column 1

        return page

    def display_title_page(self, parameters):
        self.logger.log('Code', 'Displaying Title: ' + str(parameters['Title'].getName()))

        ## Get the title to display
        titleObject = parameters['Title']
        titleObject.orderReigns()

        ## Create Widget and Layout
        page = QWidget()
        pageLayout = QGridLayout()
        page.layout = QVBoxLayout()
        page.setLayout(pageLayout)
        pageLayout.addLayout(page.layout, 0, 1)
        pageLayout.setColumnStretch(0, 2)
        pageLayout.setColumnStretch(1, 3)
        pageLayout.setColumnStretch(2, 2)
        pageLayout.setSpacing(10)

        name = QLabel(titleObject.getFullRealmTitle())
        name.setAlignment(Qt.AlignCenter)
        header_layout = QHBoxLayout()

        ## Display Reigns
        reignGroup = QWidget()
        reignGroup.layout = QVBoxLayout()
        reignGroup.setLayout(reignGroup.layout)

        ## Go back to list of titles
        back = QPushButton('List of Titles')
        back.clicked.connect(lambda: self.window.page_factory('view_object_list', {'Object Type': 'Title', 'Search Text': '', 'Page Type': 'View'}))

        ## Edit the character's details
        edit = QPushButton('Edit')
        edit.clicked.connect(lambda: self.window.page_factory('edit_title_page', {'Title': titleObject}))

        ## Display their name
        header_layout.addWidget(back)
        header_layout.addStretch(1)

        name_layout = QVBoxLayout()
        name_layout.addWidget(name)

        timeline_layout = QHBoxLayout()
        timeline_layout.addStretch(1)
        timeline_layout.addSpacing(10)

        ## Connect to predecessor title
        if titleObject.getConnection('Predecessor') is not None:
            timeline_layout.addWidget(ObjectLabel(self.window, self.window.get_object(titleObject.getConnection('Predecessor')), 'Linker Object'))

        timeline_layout.addWidget(QLabel('\u25C0'))
        timeline_layout.addWidget(QLabel('\u25b6'))

        ## Connect to successor title
        if titleObject.getConnection('Successor') is not None:
            timeline_layout.addWidget(ObjectLabel(self.window, self.window.get_object(titleObject.getConnection('Successor')), 'Linker Object'))

        timeline_layout.addStretch(1)

        name_layout.addLayout(timeline_layout)
        header_layout.addLayout(name_layout)

        header_layout.addStretch(1)
        header_layout.addWidget(edit)

        page.layout.addLayout(header_layout)

        for r in titleObject.orderReignList:
            reignObject = self.window.get_object(r)
            reignGroup.layout.addWidget(ReignWidget({'Window': self.window, 'Object Type': 'Title', 'Reign': reignObject, 'Edit': False, 'Logger': self.logger}))

        reignGroup.layout.addStretch(1)

        ## Create scrolling mechanics
        scroll = QScrollArea()

        scroll.setWidget(reignGroup)
        scroll.setWidgetResizable(True)

        page.layout.addWidget(scroll)

        # page.layout.addStretch(1)

        return page

    def edit_title_page(self, parameters):
        self.logger.log('Code', 'Editing title: ' + str(parameters['Title'].getName()))

        ## Create Widget and Layout
        page = QWidget()
        page.layout = QVBoxLayout()
        page.setLayout(page.layout)
        page.layout.setSpacing(0)

        title = parameters['Title']

        def display_title():
            self.window.write_data()
            if 'Connection' in parameters:
                self.window.page_factory('edit_person_page', {'Person': parameters['Subject']})
            else:
                self.window.page_factory('display_title_page', {'Title': title, 'Page Type': 'View'})

        ## Button to press when finished
        done = QPushButton('Done')
        done.clicked.connect(display_title)
        done.layout = QHBoxLayout()
        done.layout.addStretch(1)
        done.layout.addWidget(done)

        page.layout.addLayout(done.layout)

        info_layout = QVBoxLayout()

        ## Edit the name of the realm
        info_layout.addWidget(AttributeWidget(self.window, True, 'Realm Name', title), alignment=Qt.AlignCenter)

        ## Edit the realm title
        realmTitleLayout = QHBoxLayout()
        realmTitleLayout.addStretch(1)
        realmTitleLayout.addWidget(AttributeWidget(self.window, True, 'Realm Title', title))

        ## Check box for marking as titular title
        def checkedTitular(checked):
            if checked > 0:
                title.isTitular = True
            else:
                title.isTitular = False

        titularCheckBox = QCheckBox('Titular')
        titularCheckBox.setChecked(title.isTitular)
        titularCheckBox.stateChanged.connect(checkedTitular)

        realmTitleLayout.addSpacing(10)
        realmTitleLayout.addWidget(titularCheckBox)
        realmTitleLayout.addStretch(1)

        info_layout.addLayout(realmTitleLayout)

        ## Edit the male ruler title
        info_layout.addWidget(AttributeWidget(self.window, True, 'Male Ruler Title', title), alignment=Qt.AlignHCenter)

        ## Edit the female ruler title
        info_layout.addWidget(AttributeWidget(self.window, True, 'Female Ruler Title', title), alignment=Qt.AlignHCenter)

        timelineLayout = QHBoxLayout()
        timelineLayout.addStretch(1)

        valid_pre = {}

        for t, potential_title in self.window.objectLists['Title'].items():
            # Can only choose titles that aren't the current title and don't have a successor
            if t != title.getID() and potential_title.successor is None:
                valid_pre.update({t: potential_title})

        if title.predecessor is None:
            addButton = QPushButton('Add')
            timelineLayout.addWidget(addButton)

            addButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Title', 'Object_List': valid_pre, 'Search Text': '', 'Subject': title, 'Connection': 'Title Predecessor'}))
        else:
            preVBox = QVBoxLayout()

            changeButton = QPushButton('Change')
            preVBox.addWidget(changeButton)
            changeButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Title', 'Object_List': valid_pre, 'Search Text': '', 'Subject': title, 'Connection': 'Title Predecessor'}))

            removeButton = QPushButton('Remove')
            preVBox.addWidget(removeButton)

            timelineLayout.addLayout(preVBox)

            # timelineLayout.addWidget(ObjectLabel(self.window, title.predecessor, 'Title', -1))
            predecessorTitle = self.window.get_object(title.predecessor)
            timelineLayout.addWidget(QLabel(predecessorTitle.getFullRealmTitle()))

        timelineLayout.addSpacing(10)
        timelineLayout.addWidget(QLabel('<- Predecessor - Successor ->'))
        timelineLayout.addSpacing(10)

        valid_suc = {}

        for t, potential_title in self.window.objectLists['Title'].items():
            # Can only choose titles that aren't the current title and don't have a predecessor
            if t != title.getID() and potential_title.predecessor is None:
                valid_suc.update({t: potential_title})

        if title.successor is None:
            addButton = QPushButton('Add')
            timelineLayout.addWidget(addButton)

            addButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Title', 'Object_List': valid_suc, 'Search Text': '', 'Subject': title, 'Connection': 'Title Successor'}))
        else:
            sucVBox = QVBoxLayout()

            changeButton = QPushButton('Change')
            sucVBox.addWidget(changeButton)

            changeButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Title', 'Object_List': valid_suc, 'Search Text': '', 'Subject': title, 'Connection': 'Title Successor'}))

            removeButton = QPushButton('Remove')
            sucVBox.addWidget(removeButton)

            timelineLayout.addLayout(sucVBox)

            # timelineLayout.addWidget(ObjectLabel(self.window, title.predecessor, 'Title', -1))
            successorTitle = self.window.get_object(title.successor)
            timelineLayout.addWidget(QLabel(successorTitle.getFullRealmTitle()))

        timelineLayout.addStretch(1)
        info_layout.addLayout(timelineLayout)

        page.layout.addLayout(info_layout)

        page.layout.addStretch(1)

        return page

    def display_place_page(self, parameters):
        self.logger.log('Code', 'Displaying Place')

        ## Create Widget and Layout
        page = QWidget()
        page.layout = QGridLayout()
        page.setLayout(page.layout)
        page.layout.setColumnStretch(0, 1)  # column 0 is stretched to 1
        page.layout.setColumnStretch(1, 1)  # column 1 is stretched to 1
        page.layout.setColumnStretch(2, 1)  # column 2 is stretched to 1
        page.layout.setColumnStretch(3, 1)  # column 3 is stretched to 1

        page.layout.setRowStretch(1, 1)  # row 1 is stretched to 1
        page.layout.setRowStretch(2, 1)  # row 2 is stretched to 1

        page.layout.setSpacing(10)

        place = parameters['Place']

        nameLayout = QVBoxLayout()
        nameLayout.addWidget(AttributeWidget(self.window, False, 'Name', place), alignment=Qt.AlignHCenter)
        nameLayout.addWidget(QLabel('(' + place.getAttribute('Latitude') + ', ' + place.getAttribute('Longitude') + ')'), alignment=Qt.AlignHCenter)

        headerLayout = QHBoxLayout()

        ## Go back to list of characters
        back = QPushButton('List of Places')
        back.clicked.connect(lambda: self.window.page_factory('view_object_list', {'Object Type': 'Place', 'Search Text': ''}))

        ## Edit the character's details
        edit = QPushButton('Edit')
        edit.clicked.connect(lambda: self.window.page_factory('edit_place_page', {'Place': place}))

        ## Display their name
        headerLayout.addWidget(back)
        headerLayout.addStretch(1)
        headerLayout.addLayout(nameLayout)
        headerLayout.addStretch(1)
        headerLayout.addWidget(edit)

        page.layout.addLayout(headerLayout, 0, 0, 1, 4)  # row 0, column 0, spans 1 row, spans 2 columns

        ################ Reign Group ################
        reignGroup = QGroupBox('Applicable Reigns')
        reignGroup.layout = QVBoxLayout()
        reignGroup.setLayout(reignGroup.layout)
        reignGroup.layout.setSpacing(10)

        reignScrollWidget = QWidget()
        reignScrollWidget.layout = QVBoxLayout()
        reignScrollWidget.setLayout(reignScrollWidget.layout)

        for r in place.reignList:
            reignObject = self.window.get_object(r)

            reignLabel = QHBoxLayout()
            reignLabel.addStretch(1)

            ruler = reignObject.getConnection('Person')

            reignLabel.addWidget(ObjectLabel(self.window, reignObject, 'Page Title'))
            reignLabel.addWidget(QLabel(reignObject.getDateString()))

            reignLabel.addStretch(1)

            reignScrollWidget.layout.addLayout(reignLabel)

        reignScrollWidget.layout.addStretch(1)

        ## Create scrolling mechanics
        reignScroll = QScrollArea()

        reignScroll.setWidget(reignScrollWidget)
        reignScroll.setWidgetResizable(True)

        reignGroup.layout.addWidget(reignScroll)

        page.layout.addWidget(reignGroup, 1, 1, 2, 1)  # At row 1 and column 1, span 1 row and 1 column

        page.layout.addWidget(EventsWidget(self.window, False, place), 1, 2, 1, 2)

        return page

    def edit_place_page(self, parameters):
        self.logger.log('Code', 'Editing Place: ' + parameters['Place'].getName())

        ## Create Widget and Layout
        ## Page will have header for basic info
        ## Two columns, left for list of reigns, right for list of events
        page = QWidget()
        page.layout = QGridLayout()
        page.setLayout(page.layout)
        page.layout.setColumnStretch(0, 1)  # column 0 is stretched to 1
        page.layout.setColumnStretch(1, 1)  # column 1 is stretched to 1
        page.layout.setColumnStretch(2, 1)  # column 2 is stretched to 1
        page.layout.setColumnStretch(3, 1)  # column 3 is stretched to 1

        page.layout.setRowStretch(1, 1)  # column 1 is stretched to 1

        page.layout.setSpacing(10)

        header_layout = QHBoxLayout()  ## The layout at the top of the page
        page.layout.addLayout(header_layout, 0, 0, 1, 4)  # row 0, column 0, spans 1 row, spans 2 columns

        ## Get the person to edit
        place = parameters['Place']

        infoLayout = QVBoxLayout()
        infoLayout.setSpacing(10)

        ## Edit the name of the person
        infoLayout.addWidget(AttributeWidget(self.window, True, 'Name', place), alignment=Qt.AlignHCenter)

        ## Edit the name of the person
        infoLayout.addWidget(AttributeWidget(self.window, True, 'Latitude', place), alignment=Qt.AlignHCenter)

        ## Edit the name of the person
        infoLayout.addWidget(AttributeWidget(self.window, True, 'Longitude', place), alignment=Qt.AlignHCenter)

        header_layout.addStretch(1)
        header_layout.addLayout(infoLayout)
        header_layout.addStretch(1)

        def display_place():
            self.window.write_data()
            self.window.page_factory('display_place_page', {'Place': place})

        ## Button to press when finished
        done_button = QPushButton('Done')
        done_button.clicked.connect(display_place)

        done_button.layout = QVBoxLayout()
        done_button.layout.addWidget(done_button)
        done_button.layout.addStretch(1)
        header_layout.addLayout(done_button.layout)

        ################ Reign Group ################
        reignGroup = QGroupBox('Applicable Reigns')
        reignGroup.layout = QVBoxLayout()
        reignGroup.setLayout(reignGroup.layout)
        reignGroup.layout.setSpacing(0)

        addReignButton = QPushButton('Add')
        # Choose title to add from list
        addReignButton.clicked.connect(lambda: self.window.page_factory('choose_object_list', {'Object Type': 'Title', 'Search Text': '', 'Subject': place, 'Connection': 'Reign'}))

        addButtonLayout = QHBoxLayout()
        addButtonLayout.addStretch(1)
        addButtonLayout.addWidget(addReignButton)
        reignGroup.layout.addLayout(addButtonLayout)

        reignScrollWidget = QWidget()
        reignScrollWidget.layout = QVBoxLayout()
        reignScrollWidget.setLayout(reignScrollWidget.layout)

        for r in place.reignList:
            reignObject = self.window.get_object(r)

            reignLabel = QHBoxLayout()
            reignLabel.addStretch(1)

            ruler = reignObject.getConnection('Person')

            rulerName = ruler.getAttribute('Name') + ' ' + ruler.getAttribute('Nickname')

            reignLabel.addWidget(QLabel(rulerName))
            reignLabel.addWidget(QLabel(reignObject.getDateString()))

            reignLabel.addWidget(RemoveConnectionButton(self.window, place, reignObject))

            reignLabel.addStretch(1)

            reignScrollWidget.layout.addLayout(reignLabel)

        reignScrollWidget.layout.addStretch(1)

        ## Create scrolling mechanics
        reignScroll = QScrollArea()

        reignScroll.setWidget(reignScrollWidget)
        reignScroll.setWidgetResizable(True)

        reignGroup.layout.addWidget(reignScroll)

        page.layout.addWidget(reignGroup, 1, 1, 2, 1)  # At row 1 and column 1, span 1 row and 1 column

        page.layout.addWidget(EventsWidget(self.window, True, place), 1, 2, 1, 2)

        return page
