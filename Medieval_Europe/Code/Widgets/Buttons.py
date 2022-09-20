"""
Created on Aug 1, 2022

@author: kairom13
"""
import sys

from Medieval_Europe.Code.CustomObjects import Reign, Person, Place, Title
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class ObjectButton(QPushButton):
    def __init__(self, parameters):
        super(ObjectButton, self).__init__(parameters['Page Type'])

        self.window = parameters['Window']
        self.classKey = 'Object Button'
        self.logger = self.window.logger

        self.subject = parameters['Subject']
        self.objectType = parameters['Object Type']
        self.pageType = parameters['Page Type']

        self.connection = None

        self.checkedPlace = True

        if 'Spouse' in parameters:
            self.spouseChoice = parameters['Spouse']
        else:
            self.spouseChoice = None

        if self.pageType == 'Choose':
            self.target = parameters['Target']
            self.connection = parameters['Connection']

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            if self.pageType == 'View':
                self.logger.log('Code', 'Clicked to view ' + str(self.subject.getName()))
                if self.objectType == 'Person':
                    self.window.page_factory('display_person_page', {'Person': self.subject})
                elif self.objectType == 'Title':
                    self.window.page_factory('display_title_page', {'Title': self.subject, 'Page Type': 'View'})
                elif self.objectType == 'Place':
                    self.window.page_factory('display_place_page', {'Place': self.subject})
                else:
                    self.logger.log('Error', str(self.objectType) + ' is not a valid object type to view')

            elif self.pageType == 'Choose':
                self.logger.log('Code', 'Clicked to choose {' + str(self.target.getID()) + '} as ' + str(self.connection) + ' for {' + str(self.subject.getID()) + '}')

                spouse = None
                if self.spouseChoice is not None:
                    spouse = self.spouseChoice.getSelectedSpouse()
                    #print('Choosing: ' + str(spouse))

                self.window.add_connection(self.subject, self.connection, self.target, spouse)

                # When setting predecessor or successor, transfer any places, if desired
                if self.checkedPlace and self.connection in ('Predecessor', 'Successor'):
                    self.logger.log('Code', 'Transferring places to {' + str(self.target.getID()) + '}')
                    # Transfer all the places in the subject reign to the target reign
                    count = 0

                    for p, place in self.subject.placeList.items():
                        if p not in self.target.placeList:
                            self.target.addPlace(place)
                            place.addReign(self.target)

                            count += 1

                    # Transfer all the places in the subject's junior reigns to the equivalent in the target reign
                    for prev_j in self.subject.mergedReigns['Junior']:
                        sub_j = self.window.get_object(prev_j)  # Get the object of the junior reign
                        tar_j = self.window.get_object(sub_j.getConnectedReign(self.connection))  # Get the target object
                        for p, place in sub_j.placeList.items():
                            if p not in tar_j.placeList:
                                tar_j.addPlace(place)
                                place.addReign(tar_j)

                                count += 1

                    # Do the same transfers from target to subject
                    for p, place in self.target.placeList.items():
                        if p not in self.subject.placeList:
                            self.subject.addPlace(place)
                            place.addReign(self.subject)

                            count += 1

                    if self.connection == 'Predecessor':
                        new_con = 'Successor'
                    else:
                        new_con = 'Predecessor'

                    # Transfer all the places in the target's junior reigns to the equivalent in the subject reign
                    for prev_j in self.target.mergedReigns['Junior']:
                        sub_j = self.window.get_object(prev_j)  # Get the object of the junior reign
                        tar_j = self.window.get_object(sub_j.getConnectedReign(new_con))  # Get the target object
                        for p, place in sub_j.placeList.items():
                            if p not in tar_j.placeList:
                                tar_j.addPlace(place)
                                place.addReign(tar_j)

                                count += 1

                    self.logger.log('Code', 'Transferred ' + str(count) + ' places')

                person = None
                place = None
                title = None

                if isinstance(self.subject, Reign):
                    person = self.subject.getConnectedReign('Person')
                    print('Subject is reign, going back to person')
                elif isinstance(self.subject, Person):
                    person = self.subject
                    print('Subject is person, going back to person')
                elif isinstance(self.subject, Place):
                    place = self.subject
                    print('Subject is place, going back to place')
                elif isinstance(self.subject, Title):
                    title = self.subject
                else:
                    self.logger.log('Error', str(self.subject) + ' is not a valid object type')

                if person is not None:
                    self.window.page_factory('edit_person_page', {'Person': person})

                if title is not None:
                    self.window.page_factory('edit_title_page', {'Title': title})

                if self.connection == 'Reign' and isinstance(self.target, Reign):
                    self.window.page_factory('edit_place_page', {'Place': place})

            else:
                self.logger.log('Error', str(self.pageType) + ' is not a valid page type')

            return True
        return False


## Button to remove relative in edit screen
class RemoveConnectionButton(QPushButton):
    def __init__(self, window, subject, target):
        super(RemoveConnectionButton, self).__init__('Remove')

        self.window = window
        self.subject = subject  # The subject who is losing a connection
        self.target = target  # The target who is also losing a connection

        self.connection = self.subject.connection('Get', self.target)

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.window.logger.log('Code', 'Removing {' + self.target.getID() + '} as ' + str(self.connection) + ' with {' + self.subject.getID() + '}')

            # Remove the target as a spouse of the subject
            # Remove the subject as a spouse of the target
            if self.connection == 'Spouse':
                self.subject.removeSpouse(self.target)
                self.target.removeSpouse(self.subject)
                self.window.page_factory('edit_person_page', {'Person': self.subject})

            # Remove the target as a parent of the subject
            # Remove the subject as a child of the target
            elif self.connection in ('Mother', 'Father'):
                self.subject.removeParent(self.target)
                s = self.target.removeChild(self.subject)

                if s != 'unknown_spouse':
                    spouse = self.window.get_object(s)
                    spouse.removeChild(self.target)
                    spouse.addChild(self.target, None)

                self.window.page_factory('edit_person_page', {'Person': self.subject})

            # Remove the target as a child of the subject
            # Remove the subject as a parent of the target
            # If the child has another parent, move the child to that parent's unknown_spouse list
            elif self.connection == 'Child':
                self.subject.removeChild(self.target)  # Remove the target as a child of the subject

                parent_type = self.target.connection('Get', self.subject)  # Get the name of the relationship with the subject
                otherParent_id = self.target.getParents(parent_type)[1]  # Get the id of the other parent
                if otherParent_id is not None:
                    otherParent = self.window.get_object(otherParent_id)  # Get the object of the other parent ID

                    # Move the child to be in the unknown_spouse list
                    otherParent.removeChild(self.target)
                    otherParent.addChild(self.target, None)

                self.target.removeParent(self.subject)  # Remove the parent from the target

                self.window.page_factory('edit_person_page', {'Person': self.subject})

            elif self.connection in ('Predecessor', 'Successor'):
                if self.connection == 'Predecessor':
                    opp_connection = 'Successor'
                else:
                    opp_connection = 'Predecessor'

                # Self.subject is the reign
                # Self.target is the connected reign to be removed
                self.subject.removeConnectedReign(self.connection)  # Remove the target reign as connection to the subject reign
                self.target.removeConnectedReign(opp_connection)  # Remove the subject reign as the opposite connection to the target reign

                # Get the person of the subject reign to return to
                person = self.subject.getConnectedReign('Person')
                self.window.page_factory('edit_person_page', {'Person': person})

            elif self.connection == 'Reign':
                self.subject.removeReign(self.target)
                self.target.removePlace(self.subject)

                self.window.page_factory('edit_place_page', {'Place': self.subject})

            else:
                self.window.logger.log('Error', str(self.connection) + ' is not a valid connection to removal')

            return True
        return False


class UnmergeButton(QPushButton):
    def __init__(self, window, juniorReign):
        super(UnmergeButton, self).__init__('Unmerge')

        self.window = window
        self.juniorReign = juniorReign
        self.seniorReign = juniorReign.mergedReigns['Senior']
        self.person = juniorReign.getConnectedReign('Person')

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.juniorReign.mergedReigns['Senior'] = -1
            self.juniorReign.isJunior = False

            self.seniorReign.mergedReigns['Junior'].remove(self.juniorReign.getID())

            self.window.page_factory('edit_person_page', {'Person': self.person})

            return True
        return False


class SwitchGenderButton(QPushButton):
    def __init__(self, window, logger, person):
        super(SwitchGenderButton, self).__init__('Switch')

        self.window = window
        self.logger = logger
        self.classKey = 'Activated Widget'

        self.person = person

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.logger.log('Code', self.person.getName() + ' is switching gender')
            self.person.gender = 1 - self.person.gender

            self.window.write_data()
            self.window.page_factory('edit_person_page', {'Person': self.person})
            return True
        return False
