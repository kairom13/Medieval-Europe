"""
Created on Nov 10, 2021

@author: kairom13
"""

import json
import os
import sys
import uuid
from abc import ABC, abstractmethod
import smtplib

from PyQt5.QtWidgets import QWidget, QMessageBox, QDialog, QDialogButtonBox, QVBoxLayout, QLabel

from Medieval_Europe import get_parent_path

######################################
###                                ###
###      Custom Object Class       ###
###                                ###
######################################

class CustomObject(ABC):
    def __init__(self, logger, objectType, objectID, attribute_list, simple_connections):
        if objectID is None:
            self.objectID = uuid.uuid4().hex[:8]
        else:
            self.objectID = objectID

        self.name = {'Full Info': 'No Name',
                     'Page Title': 'No Name',
                     'Linker Object': 'No Name'}
        self.objectType = objectType

        self.logger = logger

        self.attributes = {}
        self.connectionDict = {}
        self.connections = {}
        self.eventList = {}

        for a in attribute_list:
            self.attributes.update({a: ''})

        for c in simple_connections:
            self.connections.update({c: None})

    #### Common Methods:
    ## Set the name of the object (unique to the object)
    @abstractmethod
    def setName(self):
        pass

    ## Get the name of the object
    def getName(self, name_type=None):
        if name_type is None:
            return self.name['Page Title']
        elif name_type in self.name:
            return self.name[name_type]
        else:
            self.logger.log('Error', 'Invalid name type ' + str(name_type))

    ## Get new ID if this one is a duplicate (Should be redundant)
    def getNewID(self):
        self.logger.log('Code', 'Creating new id')
        self.objectID = uuid.uuid4().hex[:8]

    ## Return this object's id
    def getID(self):
        return self.objectID

    def removeEvent(self, event_id):
        if event_id in self.eventList:
            self.eventList.pop(event_id)
        else:
            self.logger.log('Warning', 'Cannot remove event ' + str(event_id) + '. Not in event list')

    def updateEvent(self, event_id, eventDetails):
        self.eventList.update({event_id: eventDetails})

    def getEvent(self, event_id):
        if event_id in self.eventList:
            return self.eventList[event_id]
        else:
            self.logger.log('Error', 'Cannot get event ' + str(event_id) + '. Not in event list for {' + self.getID() + '}')

    def getEventList(self):
        return self.eventList

    def getObjectType(self):
        return self.objectType

    ## Generic function to update specific attribute data
    def updateAttribute(self, attribute, info):
        if attribute in self.attributes:
            self.attributes.update({attribute: info})
        else:
            self.logger.log('Error', str(attribute) + ' is not a valid attribute of a ' + str(self.__class__.__name__))

    ## Get attribute value
    def getAttribute(self, attribute):
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            self.logger.log('Error', str(attribute) + ' is not a valid attribute of a ' + str(self.__class__.__name__))

    def check_argument(self, arg, connection=None):
        if isinstance(arg, str):
            return arg
        elif arg.__class__.__name__ in ('Person', 'Title', 'Reign', 'Place'):
            return arg.getID()
        else:
            self.logger.log('Error', str(arg) + ' is an invalid data type. Should be String ID or CustomObject.')

    ## Function to handle modification to the connection dict:
    # Add: subject with the given connection name
    # Get: the connection name with the given subject
    # Remove: the connection with the given subject
    def connection(self, update, subject, name=None):
        subjectID = self.check_argument(subject)

        if subjectID is None:
            self.logger.log('Error', 'Cannot modify connection, no subject given')
        else:
            if update == 'Add':
                if subjectID in self.connectionDict:
                    self.logger.log('Warning', 'No need to add {' + str(subjectID) + '} as ' + str(name) + ' of {' + self.getID() + '}. Already connected')
                elif name is None:
                    self.logger.log('Warning', 'No connection name given')
                else:
                    self.connectionDict.update({subjectID: name})

            elif update == 'Get':
                if subjectID in self.connectionDict:
                    return self.connectionDict[subjectID]
                else:
                    self.logger.log('Error', 'Cannot get connection. {' + str(subjectID) + '} is not a connection of ' + self.getName())

            elif update == 'Remove':
                if subjectID in self.connectionDict:
                    self.connectionDict.pop(subjectID)
                else:
                    self.logger.log('Warning', 'Cannot remove connection. {' + str(subjectID) + '} is not a connection of ' + self.getName())

            else:
                self.logger.log('Error', str(update) + ' is an invalid update value')

    ## Set of methods to set, get, remove, and check existence of specific connection types
    def setConnection(self, target, connectionType):
        targetID = self.check_argument(target)

        if connectionType in self.connections:
            self.connections.update({connectionType: targetID})
            self.connection('Add', targetID, connectionType)
        else:
            self.logger.log('Error', str(connectionType) + ' is not a valid connection to add for ' + self.__class__.__name__ + ' {' + self.getID() + '}')

    def getConnection(self, connectionType):
        if connectionType in self.connections:
            return self.connections[connectionType]
        else:
            self.logger.log('Error', str(connectionType) + ' is not a valid connection for ' + self.__class__.__name__ + ' {' + self.getID() + '}')

    def removeConnection(self, connectionType):
        if connectionType not in self.connections:
            self.logger.log('Error', str(connectionType) + ' is not a valid connection to remove from ' + self.__class__.__name__ + ' {' + self.getID() + '}')

        elif connectionType in self.connections:
            self.connection('Remove', self.connections[connectionType])
            self.connections.update({connectionType: None})
        else:
            self.logger.log('Error', str(connectionType) + ' is not a valid connection for ' + self.__class__.__name__ + ' {' + self.getID() + '}')

    def hasConnection(self, connectionType):
        if connectionType in self.connections:
            if self.connections[connectionType] is not None:
                return True
            else:
                return False
        else:
            self.logger.log('Error', str(connectionType) + ' is not a valid connection for a ' + self.__class__.__name__ + ' {' + self.getID() + '}')

    ## Get Dictionary of values
    @abstractmethod
    def getDict(self):
        pass

######################################
###                                ###
###          Person Class          ###
###                                ###
######################################

## Required common fields and methods:
# id: unique 8 character string that defines a given person
# getName(): method that returns the name of the title
#    is the simple name of the person
# updateFreeInfo(): method that updates certain fields that use text boxes
#    applicable fields for Person:
#    - Name
#    - Nickname
#    - Primary Title
#    - Birth Date
#    - Death Date
# getDict(): method that returns a dictionary that defines this person, used when writing to output file

class Person(CustomObject):
    def __init__(self, logger, gender, init_dict, personID):
        attributes = ['Name',
                      'Nickname',
                      'Birth Date',
                      'Death Date']
        simpleConnections = ['Mother', 'Father']  # The types of connections this object can have that are unique
        super().__init__(logger, 'Person', personID, attributes, simpleConnections)
        self.logger = logger

        self.gender = gender
        self.primaryTitle = None
        
        self.spouses = {'unknown_spouse': []}  # Dictionary, each key is a spouse id, each value is the list of children id's for the spouse
        self.parents = {'Father': None, 'Mother': None}
        
        if init_dict is not None:
            for a in self.attributes:
                self.logger.log('Detailed', 'Initial setting of ' + str(a), True)
                self.updateAttribute(a, init_dict['Attributes'][a])

            for c in init_dict['Connections']:
                self.logger.log('Detailed', 'Initial setting of ' + str(c), True)
                if c == 'Spouses':
                    self.addSpouses(init_dict['Connections'][c])
                else:
                    self.addParent(init_dict['Connections'][c], c)

            self.logger.log('Detailed', 'Initial setting of ' + str(len(init_dict['Events'])) + ' events', True)
            for e in init_dict['Events']:
                self.updateEvent(e, init_dict['Events'][e])

        self.reignList = {}  # {reign.id: reignObject}
        self.placeList = {}  # {place.id: placeObject
        self.seniorReigns = {}  # List of reigns for the person that are not junior

        self.setName()
        self.logger.log('Detailed', 'Initial setting of names: ' + str(list(self.name.items())), True)

    ## Set this person's name as the full name
    def setName(self):
        if self.getAttribute('Nickname') == '':
            nickname = ''
            self.name.update({'Linker Object': self.getAttribute('Name')})
        else:
            nickname = ' ' + self.getAttribute('Nickname')
            self.name.update({'Linker Object': self.getAttribute('Name') + ' ' + self.getAttribute('Nickname')})

        pageTitle = self.getAttribute('Name') + nickname
        fullInfo = self.getAttribute('Name') + nickname + ' ' + self.getDateString()
            
        if self.primary_title('Has'):
            pageTitle += ', ' + self.primary_title('Get')
            fullInfo += '\n' + self.primary_title('Get')

        self.name.update({'Page Title': pageTitle})
        self.name.update({'Full Info': fullInfo})

        for r in self.reignList:
            reign = self.reignList[r]
            reign.setName()


    ## Add Relationship with Child
    ## If there is no spouse, add child with unknown spouse
    def addChild(self, child, spouse):
        childID = self.check_argument(child, 'Child')

        if spouse is None:  ## Person had child with an unknown spouse
            if childID in self.spouses['unknown_spouse']:
                self.logger.log('Warning', '{' + childID + '} is already a child of {' + self.getID() + '} with unknown spouse')
            else:
                self.logger.log('Code', 'Add {' + childID + '} as new child with unknown spouse')
                self.spouses['unknown_spouse'].append(childID)  # Add the child to the unknown spouse list
                self.connection('Add', childID, 'Child')

        else:
            spouseID = self.check_argument(spouse, 'Spouse')
            
            if spouseID in self.spouses:
                ## Person had child with known spouse of person
                ## Add child to the person with given spouse

                self.logger.log('Code', 'Add {' + childID + '} as new child with spouse {' + spouseID + '}')
                self.spouses[spouseID].append(childID)  # Add the child to the given spouse's list
                self.connection('Add', childID, 'Child')

            else:
                self.logger.log('Error', 'Cannot add child, {' + spouseID + '} is not a valid spouse')

        
    ## Remove Relationship with Child 
    def removeChild(self, child):
        childID = self.check_argument(child, 'Child')

        for s in self.spouses:
            for c in self.spouses[s]:
                if childID == c:
                    self.logger.log('Code', 'Removed {' + childID + '} as a child with spouse {' + s + '}')
            
                    self.spouses[s].remove(childID)
                    self.connection('Remove', childID)
                    return s  # Return the spouse with whom the child is being removed
                
        self.logger.log('Warning', '{' + childID + '} is not a child of {' + self.getID() + '}, so cannot be removed')
        return None  # No spouse is returned
        
    ## Add full list of spouses
    def addSpouses(self, spouses):
        for s, children in spouses.items():
            self.spouses.update({s: children})
            if s != 'unknown_spouse':
                self.connection('Add', s, 'Spouse')

            for c in children:
                self.connection('Add', c, 'Child')
        
    ## Add Relationship with Spouse
    def addSpouse(self, spouse):
        spouseID = self.check_argument(spouse, 'Spouse')

        self.spouses.update({spouseID: []})
        self.connection('Add', spouseID, 'Spouse')
        self.logger.log('Code', 'Added {' + spouseID + '} as a spouse')
        
    ## Remove Relationship with Spouse
    def removeSpouse(self, target):
        targetID = self.check_argument(target, 'Spouse')

        if targetID in self.spouses:
            self.logger.log('Code', 'Removing {' + targetID + '} as spouse')
            childrenList = self.spouses[targetID] ## Get the list of children with that spouse

            for c in childrenList:  ## Add those children to the unknown spouse list
                self.logger.log('Code', 'Moving {' + c + '} to unknown spouse')
                self.spouses['unknown_spouse'].append(c)

            self.spouses.pop(targetID)  # Remove the target spouse from the spouse dictionary
            self.connection('Remove', targetID)

        else:
            self.logger.log('Warning', '{' + targetID + '} is not currently a spouse. Cannot be removed')

    # Add parent as the relation to self
    def addParent(self, parent, relation):
        if parent is not None:
            parentID = self.check_argument(parent, 'Person')  # Get the parentID

            if relation in ('Father', 'Mother'):
                self.parents.update({relation: parentID})
                if parentID is not None:  # Only add parent relationship if the parent exists (should not have a None key)
                    self.connection('Add', parentID, name=relation)
            else:
                self.logger.log('Error', str(relation) + ' is not a valid parent type to add')

    
    ## Remove Relationship with Parent (can be either name or subject)
    def removeParent(self, parent):
        if parent in ('Father', 'Mother'):
            parentID = self.getParents(parent)[0]  # Get the subjectID of the parent to remove
            self.parents.update({parent: None})  # Update the parents dict to specify the parent name as None
        else:
            parentID = self.check_argument(parent, 'Person')  # Get the parentID
            relation = self.connection('Get', parentID)  # Get the name of the relationship
            if relation is not None:
                self.parents.update({relation: None})  # Set the relationship as None

        self.logger.log('Code', 'Removing ' + self.connection('Get', parentID) + ' from {' + self.getID() + '}')
        self.connection('Remove', parentID)

    ## Get the parent IDs as a tuple with an order based on what relation name was given
    def getParents(self, relation=None):
        if relation == 'Father':
            return self.parents['Father'], self.parents['Mother']
        elif relation == 'Mother':
            return self.parents['Mother'], self.parents['Father']
        elif relation is None:
            return self.parents['Father'], self.parents['Mother']
        else:
            self.logger.log('Error', str(relation) + ' is not a valid parent type to get')
            
    def addReign(self, reign):
        if isinstance(reign, Reign):
            self.reignList.update({reign.getID(): reign})
            self.connection('Add', reign.getID(), 'Reign')
            if not reign.isJunior:
                self.seniorReigns.update({reign.getID(): reign})
        else:
            self.logger.log('Error', 'Cannot add ' + str(reign) + ' as Reign. Invalid type')
        
    def removeReign(self, reign):
        reignID = self.check_argument(reign, 'Reign')

        self.logger.log('Code', 'Removing reign {' + str(reignID) + '}')
        placeList = self.reignList[reignID].placeList
        for p, place in placeList.items():
            place.removeReign(reignID)

        self.reignList.pop(reignID)

    def removeSeniorReign(self, senior):
        seniorID = self.check_argument(senior)

        if seniorID in self.seniorReigns:
            self.seniorReigns.pop(seniorID)
            self.logger.log('Detailed', 'Remove {' + seniorID + '} from senior reigns dict of {' + self.getID() + '}')
        else:
            self.logger.log('Warning', 'Cannot remove {' + seniorID + '} from senior reigns dict as it is not an element of the list')

    ## Actions related to the primary title for this person
    def primary_title(self, action, title=None):
        if action == 'Set':
            self.primaryTitle = title.getFullRulerTitle(self.gender)
            self.setName()

        elif action == 'Get':
            return self.primaryTitle

        elif action == 'Remove':
            if title.getFullRulerTitle(self.gender) == self.primaryTitle:
                self.primaryTitle = None
                self.setName()
            else:
                self.logger.log('Warning', 'Cannot remove ' + title.getFullRulerTitle(self.gender) + '. Is not the primary title: ' + self.primaryTitle)

        elif action == 'Has':
            if self.primaryTitle is None:
                return False
            else:
                return True

    ## Add a title (with a new reign) to the list
    def addTitle(self, title):
        newReign = Reign(self.logger, self, title, None, None)

        self.reignList.update({newReign.getID(): newReign})
        
        return newReign

    ## Add place to place list
    def addPlace(self, placeObject):
        placeID = placeObject.getID()

        if placeID in self.placeList:
            self.logger.log('Warning', str(placeObject.getAttribute('Name')) + ' is already associated with ' + str(self.getAttribute('Name')))
        else:
            self.placeList.update({placeID: placeObject})

    def removePlace(self, placeObject):
        placeID = placeObject.getID()

        if placeID in self.placeList:
            self.placeList.pop(placeID)
        else:
            self.logger.log('Warning', str(placeObject.getAttribute('Name')) + ' is already associated with ' + str(self.getAttribute('Name')))

    def getDateString(self):
        return '(' + self.getAttribute('Birth Date') + ' - ' + self.getAttribute('Death Date') + ')'
        
    ## Get Dictionary of values
    def getDict(self):
        returnDict = {self.getID(): {'Attributes': self.attributes,
                                     'Gender': self.gender,
                                     'Connections': {'Spouses': self.spouses,
                                                     'Father': self.parents['Father'],
                                                     'Mother': self.parents['Mother']},
                                     'Events': self.eventList,
                                     'Reign List': {}}}
        
        for r in self.reignList:
            returnDict[self.getID()]['Reign List'].update(self.reignList[r].getDict())
            
        return returnDict

    ## Get Dictionary of immutable characteristics
    def getStaticLabels(self):
        genderDict = {0: 'Man', 1: 'Woman'}
        return {'Gender': genderDict[self.gender],
                'Birth Date': self.getAttribute('Birth Date'),
                'Death Date': self.getAttribute('Death Date')}

######################################
###                                ###
###          Title Class           ###
###                                ###
######################################

## Required common fields and methods:
# id: unique 8 character string that defines a given person
# getName(): method that returns the name of the title
#    is the full realm title
# updateFreeInfo(): method that updates certain fields that use text boxes
#    applicable fields for Title:
#    - Realm Name
#    - Realm Title
#    - Male Ruler Title
#    - Female Ruler Title
# getDict(): method that returns a dictionary that defines this title, used when writing to output file


class Title(CustomObject):
    def __init__(self, logger, init_dict, titleID):
        attributes = ['Realm Name',  # The name of the realm the title refers to (e.g. Bavaria, Tirol, France, etc)
                      'Realm Title',  # The type of title (e.g. Duchy, County, Kingdom, etc)
                      'Male Ruler Title',  # How the male ruler is referred to, vis-à-vis their title (e.g. Duke, Count, King, etc)
                      'Female Ruler Title']  # How the female ruler is referred to, vis-à-vis their title (e.g. Duchess, Countess, Queen, etc)
        simpleConnections = ['Predecessor', 'Successor']  # The types of connections this object can have that are unique

        super().__init__(logger, 'Title', titleID, attributes, simpleConnections)

        self.availableOrder = 1000
        
        if init_dict is None:
            self.logger.log('Detailed', 'Initial Dictionary is empty', True)
            self.isTitular = False
        else:
            for a in self.attributes:
                self.logger.log('Detailed', 'Initial setting of attribute: ' + str(a), True)
                self.updateAttribute(a, init_dict['Attributes'][a])
            self.isTitular = init_dict['Titular']
            self.logger.log('Detailed', 'Initial setting of isTitular: ' + str(self.isTitular), True)

            for c in init_dict['Connections']:
                if init_dict['Connections'][c] is not None:
                    self.logger.log('Detailed', 'Initial setting of connection: ' + str(c), True)
                    self.setConnection(init_dict['Connections'][c], c)

            self.logger.log('Detailed', 'Initial setting of ' + str(len(init_dict['Events'])) + ' events', True)
            for e in init_dict['Events']:
                self.updateEvent(e, init_dict['Events'][e])

        self.setName()
        self.logger.log('Detailed', 'Initial setting of names: ' + str(list(self.name.items())), True)
        
        self.reignDict = {}  ## structure: {<reignID>: <reignObject>}
        self.orderReignList = []

    def setName(self):
        for t in self.name:
            self.name.update({t: self.getFullRealmTitle()})

    ## Return a string of info to display for this person
    def getDisplayInfo(self):
        return self.getFullRealmTitle()

    def getFullRealmTitle(self):
        if self.isTitular:
            return 'Titular ' + self.getAttribute('Realm Title') + ' of ' + self.getAttribute('Realm Name')
        else:
            return self.getAttribute('Realm Title') + ' of ' + self.getAttribute('Realm Name')
    
    def getFullRulerTitle(self, gender):
        rulerTitle = ''
        if self.isTitular:
            rulerTitle = 'Titular '

        if gender == 0:
            return rulerTitle + self.getAttribute('Male Ruler Title') + ' of ' + self.getAttribute('Realm Name')
        elif gender == 1:
            return rulerTitle + self.getAttribute('Female Ruler Title') + ' of ' + self.getAttribute('Realm Name')
        else:
            self.logger.log('Error', str(gender) + ' is not a valid gender')
            return None

    def orderReigns(self):
        self.orderReignList = list(self.reignDict.keys())
        
        # Python program for implementation of Quicksort Sort
 
        # This function takes last element as pivot, places
        # the pivot element at its correct position in sorted
        # array, and places all smaller (smaller than pivot)
        # to left of pivot and all greater elements to right
        # of pivot
         
         
        def partition(arr, low, high):
            i = (low-1)         # index of smaller element
            pivot = self.reignDict[arr[high]].order    # pivot
         
            for j in range(low, high):
                # If current element is less than or equal to pivot
                if self.reignDict[arr[j]].order <= pivot:
                    # increment index of smaller element
                    i = i+1
                    arr[i], arr[j] = arr[j], arr[i]
         
            arr[i+1], arr[high] = arr[high], arr[i+1]
            
            return i + 1
         
        # The main function that implements QuickSort
        # arr[] --> Array to be sorted,
        # low  --> Starting index,
        # high  --> Ending index
         
        # Function to do Quick sort
         
        def quickSort(arr, low, high):
            if len(arr) == 1:
                return arr
            
            if low < high:
         
                # pi is partitioning index, arr[p] is now
                # at right place
                pi = partition(arr, low, high)
         
                # Separately sort elements before
                # partition and after partition
                quickSort(arr, low, pi-1)
                quickSort(arr, pi+1, high)
        
        quickSort(self.orderReignList, 0, len(self.orderReignList)-1)
        
    def addReign(self, reign):
        if isinstance(reign, Reign):
            self.reignDict.update({reign.getID(): reign})
            self.connection('Add', reign.getID(), 'Reign')

            reign.order = self.availableOrder
            self.availableOrder += 200
        else:
            self.logger.log('Error', 'Cannot add ' + str(reign) + ' to title ' + str(self.getName()) + '. Invalid type')
    
    def removeReign(self, reignID):
        if reignID in self.reignDict:
            self.reignDict.pop(reignID)
            self.connection('Remove', reignID)
        else:
            self.logger.log('Warning', 'Cannot remove {' + str(reignID) + '}; Not in dictionary of reigns')
            
    def getDict(self):
        return {self.getID(): {'Attributes': self.attributes,
                               'Titular': self.isTitular,
                               'Connections': self.connections,
                               'Events': self.eventList,
                               'Reign List': list(self.reignDict.keys())}}


######################################
###                                ###
###          Place Class           ###
###                                ###
######################################

## Required common fields and methods:
# id: unique 8 character string that defines a given person
# getName(): method that returns the name of the reign
#    is the associated person + the full ruler title of the associated title
# updateFreeInfo(): method that updates certain fields that use text boxes
#    applicable fields for Reign:
#    - Start Date
#    - End Date
# getDict(): method that returns a dictionary that defines this reign, used when writing to output file

class Place(CustomObject):
    def __init__(self, logger, init_dict, place_id):
        super().__init__(logger, 'Place', place_id, ['Name', 'Latitude', 'Longitude'], [])

        if init_dict is None:
            self.logger.log('Detailed', 'Initial Dictionary is empty', True)
            self.reignList = []

        else:
            for a in self.attributes:
                self.logger.log('Detailed', 'Intial setting of ' + str(a), True)
                self.updateAttribute(a, init_dict['Attributes'][a])

            self.logger.log('Detailed', 'Initial setting of ' + str(len(init_dict['Events'])), True)
            for e in init_dict['Events']:
                self.updateEvent(e, init_dict['Events'][e])

            self.reignList = init_dict['Reign List']
            self.logger.log('Detailed', 'Initial setting of ' + str(len(init_dict['Reign List'])), True)
            for r in self.reignList:
                self.connection('Add', r, 'Reign')

        self.setName()
        self.logger.log('Detailed', 'Initial setting of names: ' + str(list(self.name.items())), True)

    def setName(self):
        self.name.update({'Full Info': self.getAttribute('Name') + ' (' + self.getAttribute('Latitude') + ', ' + self.getAttribute('Longitude') + ')'})
        self.name.update({'Page Title': self.getAttribute('Name') + ' (' + self.getAttribute('Latitude') + ', ' + self.getAttribute('Longitude') + ')'})
        self.name.update({'Linker Object': self.getAttribute('Name')})

    ## Return a string of info to display for this person
    def getDisplayInfo(self):
        return self.getAttribute('Name') + ' (' + self.getAttribute('Latitude') + ', ' + self.getAttribute('Longitude') + ')'

    def addReign(self, reign):
        reignID = self.check_argument(reign, 'Reign')

        if reignID is not None:
            if reignID in self.reignList:
                self.logger.log('Warning', '{' + reignID + '} already in list for {' + self.getID() + '}')
            else:
                self.reignList.append(reignID)
                self.connection('Add', reignID, 'Reign')

    def removeReign(self, reign):
        reignID = self.check_argument(reign, 'Reign')

        if reignID is not None:
            if reignID in self.reignList:
                self.reignList.remove(reignID)
                self.connection('Remove', reignID)
            else:
                self.logger.log('Warning', '{' + reignID + '} already in list for {' + self.getID() + '}')

    def hasReign(self, reign):
        reignID = self.check_argument(reign, 'Reign')

        if reignID in self.reignList:
            return True
        else:
            return False

    def addCoords(self, lat=None, long=None):
        if lat is not None:
            self.updateAttribute('Latitude', lat)

        if long is not None:
            self.updateAttribute('Longitude', long)

    def getCoords(self):
        return {self.getAttribute('Latitude'), self.getAttribute('Longitude')}

    def getDict(self):
        return {self.getID(): {'Attributes': self.attributes,
                               'Events': self.eventList,
                               'Reign List': self.reignList}}


######################################
###                                ###
###          Reign Class           ###
###                                ###
######################################

## Required common fields and methods:
# id: unique 8 character string that defines a given person
# getName(): method that returns the name of the reign
#    is the associated person + the full ruler title of the associated title
# updateFreeInfo(): method that updates certain fields that use text boxes
#    applicable fields for Reign:
#    - Start Date
#    - End Date
# getDict(): method that returns a dictionary that defines this reign, used when writing to output file

class Reign(CustomObject):
    def __init__(self, logger, ruler, title, init_dict, reignID):
        attributes = ['Start Date',  # The start date of this reign
                      'End Date']  # The end date of this reign
        simpleConnections = ['Predecessor', 'Successor']  # The types of connections this object can have that are unique

        super().__init__(logger, 'Reign', reignID, attributes, simpleConnections)

        self.isJunior = False  # Is this reign a junior to another reign
        self.isPrimary = False  # Is this reign the primary for the person

        self.logger.log('Detailed', 'Setting initial connection to person: {' + ruler.getID() + '}', True)
        self.connection('Add', ruler, 'Person')
        ruler.addReign(self)

        self.logger.log('Detailed', 'Setting initial connection to title: {' + title.getID() + '}', True)
        self.connection('Add', title, 'Title')
        title.addReign(self)

        self.order = -1  # The order of this reign in the title
        self.connections.update({'Person': ruler, 'Title': title})

        if init_dict is None:
            self.logger.log('Detailed', 'Initial Dictionary is empty', True)
            self.mergedReigns = {'Senior': None,
                                 'Junior': []}

        else:
            for a in self.attributes:
                self.updateAttribute(a, init_dict['Attributes'][a])

            for c in ('Predecessor', 'Successor'):
                if init_dict['Connections'][c] is not None:
                    self.logger.log('Detailed', 'Intial setting of ' + str(c))
                    self.setConnection(init_dict['Connections'][c], c)

            self.logger.log('Detailed', 'Initial setting of merged reigns')
            self.mergedReigns = init_dict['Merged Reigns']

            if self.mergedReigns['Senior'] != -1 and self.mergedReigns['Senior'] is not None:
                self.logger.log('Detailed', 'Reign is a junior reign', True)
                self.isJunior = True
                ruler.removeSeniorReign(self)

            self.isPrimary = init_dict['Is Primary']
            if self.isPrimary:
                self.logger.log('Detailed', 'Reign is the primary title', True)
                self.connections['Person'].primary_title('Set', self.getConnection('Title'))

        self.setName()
        self.logger.log('Detailed', 'Initial setting of names: ' + str(list(self.name.items())), True)

        self.placeList = {}  # List of places associated with this reign

    def setName(self):
        ruler = self.getConnection('Person')
        title = self.getConnection('Title')
        self.name.update({'Page Title': ruler.getAttribute('Name') + ', ' + title.getFullRulerTitle(ruler.gender)})

        if ruler.getAttribute('Nickname') == '':
            self.name.update({'Linker Object': ruler.getAttribute('Name')})
            self.name.update({'Full Info': ruler.getAttribute('Name') + self.getDateString() + '\n' + title.getFullRulerTitle(ruler.gender)})
        else:
            self.name.update({'Linker Object': ruler.getAttribute('Name') + '\n' + ruler.getAttribute('Nickname')})
            self.name.update({'Full Info': ruler.getAttribute('Name') + ' ' + ruler.getAttribute('Nickname') + self.getDateString() + '\n' + title.getFullRulerTitle(ruler.gender)})

    def setPrimary(self, checked):
        self.isPrimary = checked
        ruler = self.getConnection('Person')

        if checked:
            ruler.primary_title('Set', self.getConnection('Title'))
        else:
            ruler.primary_title('Remove', self.getConnection('Title'))
        
    ## The order of this reign for the associated title
    def setOrder(self, order):
        self.order = order
    
    ## Merge with <reign> by setting it as the <relation> in the relationship
    ## Expected relation values:
    # Senior
    # Junior
    
    ## Handling scenarios
    # Will not override senior reign appointment. Once the relationship is established, can only unmerge first
    # Will not have reigns as both senior/junior, cannot pick a junior reign as senior reign also
    
    def mergeReign(self, reign, relation):
        reignID = self.check_argument(reign)

        if relation == 'Senior':
            ## Set <reign> as this reign's senior
            self.mergedReigns[relation] = reignID
            self.isJunior = True
            self.connection('Add', reignID, relation)
            self.getConnection('Person').removeSeniorReign(self)

            self.mergedReigns['Junior'] = []  # Remove all junior reigns from the list
        elif relation == 'Junior':
            ## Add <reign> as a junior to this reign
            self.mergedReigns[relation].append(reignID)
            self.connection('Add', reignID, relation)
        else:
            self.logger.log('Error', str(relation) + ' is not a valid relation for merging reigns')

    def transferJuniorReigns(self, globalReignList, newSenior):
        for j in self.mergedReigns['Junior']:
            juniorReign = globalReignList[j]  # Get the reign object for each junior reign
            juniorReign.mergeReign(newSenior, 'Senior')
            newSenior.mergeReign(juniorReign, 'Junior')

    def unmerge(self, seniorReign):
        if isinstance(seniorReign, Reign):
            seniorID = seniorReign.getID()
        else:
            seniorID = -1
            self.logger.log('Error', 'Cannot unmerge. ' + str(seniorReign) + ' is not a Reign object')

        if self.isJunior:
            if self.mergedReigns['Senior'] == seniorID:
                self.isJunior = False
                self.mergedReigns['Senior'] = -1
                self.connection('Remove', seniorID)

                seniorReign.mergedReigns['Junior'].pop(self.getID())
                seniorReign.connection('Remove', self.getID())

                self.logger.log('Detailed', 'Successfully removed {' + seniorID + '} as the senior reign for {' + self.getID() + '}')
            else:
                self.logger.log('Error', '{' + seniorID + '} is not the senior reign for {' + self.getID() + '} so cannot be removed')
        else:
            self.logger.log('Warning', '{' + self.getID() + '} is already a junior reign')

    def addPlace(self, placeObject):
        placeID = placeObject.getID()

        if placeID in self.placeList:
            self.logger.log('Warning', str(placeObject.getAttribute('Name')) + ' is already associated with ' + str(self.getAttribute('Name')))
        else:
            self.getConnection('Person').addPlace(placeObject)
            self.placeList.update({placeID: placeObject})
            self.connection('Add', placeID, 'Place')

    def removePlace(self, placeObject):
        placeID = placeObject.getID()

        if placeID in self.placeList:
            self.getConnection('Person').removePlace(placeObject)
            self.placeList.pop(placeID)
            self.connection('Remove', placeID)
        else:
            self.logger.log('Warning', str(placeObject.getAttribute('Name')) + ' is already associated with ' + str(self.getAttribute('Name')))
        
    def getDateString(self):
        return '(' + str(self.getAttribute('Start Date')) + ' - ' + str(self.getAttribute('End Date')) + ')'
        
    def getDict(self):    
        return {self.getID(): {'Attributes': self.attributes,
                               'Connections': {'Title': self.getConnection('Title').getID(),
                                               'Predecessor': self.getConnection('Predecessor'),
                                               'Successor': self.getConnection('Successor')},
                               'Is Primary': self.isPrimary,
                               'Merged Reigns': self.mergedReigns}}

        
######################################
###                                ###
###      Custom Logger Class       ###
###                                ###
######################################

## A custom logger class for logging code, warnings, and errors
## Includes functionality to convert object IDs into their names

class Logger:
    def __init__(self, objectList, test):
        self.objectList = objectList
        self.testFlag = test

        self.logDict = {'Code': {'Pages': {}, 'Log': {}},
                        'Error': {'Pages': {}, 'Log': {}},
                        'Warning': {'Pages': {}, 'Log': {}},
                        'Detailed': {'Pages': {}, 'Log': {}}}

        self.page_key = '000_Init'

        self.writeLogs()
        
    ## Main method that stores information sent in <value>
    #        in the appropriate log, determined by <kind>
    #        and the appropriate location, determined by <key>
    
    ## Considering classes as three types: class, object, widget
    #    class: the logic and display of the application, facilitates the process. Method's super important
    #    object: custom way to store and manipulate data. Will have many instances, but similar processes'
    #    widget: custom way to display on the GUI. Always created as part of class method, only notable when activated
    #
    # Keys for each type of class
    #    :
    #    - classKey: describes the class object in which methods are called, no index used
    #    - methodKey: records when method is called and run, global index used
    #    object:
    #    - classKey: describes the generic object class, no index used
    #    - classInstance: describes the specific instance of the object, including method calls, no index used
    #    widget:
    #    - classKey: describes the underlying class for which 
    
    # <value> expected as String
    # <kind> expected as String with allowed values:
    #    - 'Code'
    #    - 'Warning'
    #    - 'Error'
    # <key> expected as String
    
    ## Key expectations (future enhancement for more generic expectations)
    #    key[0] is the class (class instance for objects)
    #    key[1] is the specific method called, or object instance
    
    ## Use curly brace wrappers to identify object IDs
    def log(self, kind, value, array=None):
        value = self.enhanceStringLinks(value)

        if array is None:
            array = False

        sublog = {}
        pages = {}
                
        # Get the appropriate log dict
        if kind in self.logDict:
            sublog = self.logDict[kind]['Log']
            pages = self.logDict['Code']['Pages']  # The number of logs for the particular page instance

            if kind != 'Detailed':
                self.log('Detailed', kind + ': ' + value, array)
        else:
            self.log('Error', str(kind) + ' is not a valid type of log. Must be ' + str(list(self.logDict.keys())))

        # Check if the page key (i.e. 005_display_title_page) has already been added to the log dict
        if self.page_key in pages:
            pages[self.page_key] += 1  # Get the next index to store the log
            index = pages[self.page_key]

            # Append the value to the log at page_key if it already exists in the log dict
            if self.page_key in sublog:
                page_log = sublog[self.page_key]
                lastIndex = len(page_log) - 1

                if array:
                    if isinstance(sublog[self.page_key][lastIndex], list):
                        # The last entry is in an array
                        sublog[self.page_key][lastIndex].append(f'{index:03d}_' + value)
                    else:
                        # The last entry is not in an array
                        # Add the value as the first element of a new array
                        sublog[self.page_key].append([f'{index:03d}_' + value])

                else:
                    sublog[self.page_key].append(f'{index:03d}_' + value)
            else:
                # Create new list for the page_key in the log dict
                # (mostly for errors and warnings to track where on the page they occurred
                if array:
                    sublog.update({self.page_key: [[f'{index:03d}_' + value]]})
                else:
                    sublog.update({self.page_key: [f'{index:03d}_' + value]})
        else:
            # Create new dict entry in the log dict
            index = 0

            pages.update({self.page_key: index})

            if array:
                sublog.update({self.page_key: [[f'{index:03d}_' + value]]})
            else:
                sublog.update({self.page_key: [f'{index:03d}_' + value]})

        # Call writeLogs to write to external file
        if kind != 'Detailed':
            self.writeLogs()

        if kind == 'Error':
            self.handleError(value)
        
    def enhanceStringLinks(self, value):
        if '{' in value:  # Only replace IDs if there are actually IDs to replace
            idSplit = value.split('{')  # Split the value along curly braces
            value = idSplit[0]
            for objectID in idSplit[1:]:  # Iterate through list starting from 2nd value (first is before curly brace is found)
                after = objectID[objectID.find('}')+1:]  # Get string after curly braces for new value string
                objectID = objectID[:objectID.find('}')]  # Get objectID from characters up to closed curly brace
                                                          # need handling of no closed curly brace, too long/short id

                obj = None

                for o_key, o_list in self.objectList.items():
                    if objectID in o_list:
                        obj = o_list[objectID]  # Get object based on which list it's in

                if obj is not None:
                    value += obj.getName() + after  # Replace object ID with associated object name
                else:
                    self.log('Warning', 'Could not enhance ' + str(objectID) + '. ID not found in object lists')
                    value += str(objectID) + after
                
        return value
    
    def writeLogs(self):
        for k in self.logDict:
            with open(os.path.join(get_parent_path(), 'Logs/' + k.lower() + '_log.json'), 'w') as outfile:
                json.dump(self.logDict[k]['Log'], outfile, indent=4)

    def handleError(self, message):
        if not self.testFlag:
            dlg = DisplayErrorDialog(message)
            dlg.exec()
        else:
            print('The application encountered an error:')
            print(message)
            print('The application will now close')

        sys.exit()


## Dialog box to for displaying an error
class DisplayErrorDialog(QDialog):
    def __init__(self, message):
        super().__init__()

        self.setWindowTitle('An Error Occurred')

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        topLabel = QLabel('The application encountered an error:')
        messageLabel = QLabel(message)
        bottomLabel = QLabel('The application will now close')

        self.layout.addWidget(topLabel)
        self.layout.addWidget(messageLabel)
        self.layout.addWidget(bottomLabel)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        # import smtplib, ssl
        #
        # port = 465  # For SSL
        # password = input("Type your password and press enter: ")
        #
        # # Create a secure SSL context
        # context = ssl.create_default_context()
        #
        # sender_email = "medapp.errors@gmail.com"
        # receiver_email = "medapp.errors@gmail.com"
        # message = """\
        # Subject: Test Email
        #
        # This message is sent from Python."""
        #
        # with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        #     server.login("medapp.errors@gmail.com", password)
        #     server.sendmail(sender_email, receiver_email, message)



