import csv
import math
import uuid


class RelationTest:
    def __init__(self):
        self.personList = {}
        self.test_cases = []

        self.scenarios = ['father_no_spouse', 'mother_no_spouse', 'parents_are_spouses', 'child_no_spouse',
                          'child_spouse', 'spouse']

        # Can't have a child with a spouse and no spouse
        # Can't have a father without a spouse and have parents who are spouses
        # Can't have a mother without a spouse and have parents who are spouses
        # Can't have two parents who aren't spouses
        self.mutually_exclusive = ['0-1', '0-2', '1-2', '4-!5']

        self.truth_array = [0, 0, 0, 0, 0, 0]

        self.generate_test_cases()
        self.run_tests()

    # Actions:
    # Add, change, remove connection (father, mother, spouse, child)
    def run_tests(self):
        actions = ['Add', 'Change', 'Remove']
        connections = ['Father', 'Mother', 'Spouse', 'Child']

        connection_list = []

        # Iterate through all combinations of test people connections
        for subject in self.test_cases:
            for target in self.test_cases:

                subject.addFather(target)

                connection_list.append(Connection(self.personList, subject, target, {'Action Type': 'Add', 'Connection': 'Father'}))

                # Add Father

                # Change Father

                # Remove Father

    def generate_test_cases(self):
        while not self.max_array():
            # print(self.truth_array)
            exclude = False
            for m in self.mutually_exclusive:
                false_count = 0
                excludeCase = []
                excludeList = m.split('-')
                for e in excludeList:  ## Only exclude if all conditions are true
                    if e[0] == '!':
                        if self.truth_array[int(e[1:])] == 0:
                            false_count += 0
                            excludeCase.append('no ' + self.scenarios[int(e[1:])])
                        else:
                            false_count += 1
                    elif self.truth_array[int(e)] == 1:
                        false_count += 0
                        excludeCase.append(self.scenarios[int(e)])
                    else:
                        false_count += 1

                if false_count == 0:
                    # print('Exclude: ' + str(excludeCase))
                    exclude = True
                    break
            if not exclude:
                newPerson = TestPerson(self.personList, self.truth_array)

                self.test_cases.append(newPerson)

                # newPerson.string_print()

            self.increment()

    def max_array(self):
        for e in self.truth_array:
            if e == 0:
                return False
        return True

    def increment(self):
        pos = len(self.truth_array) - 1

        for d in reversed(self.truth_array):
            if int(d) == 0:
                self.truth_array[pos] = 1
                break
            else:
                self.truth_array[pos] = 0

            pos -= 1


# Used to check if connection has any issues and was successfully made
class Connection:
    def __init__(self, personList, subject, target, action):
        self.personList = personList
        self.subject = subject
        self.target = target
        self.action = action

        cases = self.checkConnections()

        total = 0
        for c in cases:
            total += not c

        print('\----- Next Case ------')
        self.subject.string_print()
        self.target.string_print()
        print(cases)
        print(total)

    def getConnection(self, connection):
        if connection == 'Subject':
            return [self.subject.personID]
        elif connection == 'Target':
            return [self.target.personID]
        else:
            print('ERROR: ' + str(connection) + ' is not a valid connection')
            return None

    def makeConnection(self):
        if self.action['Action Type'] == 'Add':
            if self.action['Connection'] == 'Father':
                if self.subject.father != self.target.personID:
                    self.subject.addFather(self.target.personID)
                if self.subject.mother == -1:
                    if self.subject.personID not in self.target.spouses['unknown spouse']:
                        self.target.addChild(self.subject.personID, None)
                else:
                    if self.subject.mother not in self.target.spouses:
                        self.target.addSpouse(self.subject.mother)
                    if self.target.personID not in self.subject.mother.spouses:
                        self.subject.mother.addSpouse(self.target.personID)

    def checkConnections(self):

        if self.action['Action Type'] == 'Add':
            if self.action['Connection'] == 'Father':
                # Rules for configuration:
                # Condition: Boolean for if the test case depends on a prior condition (e.g. only if the subject has a mother)
                # Dependency: Target or Subject: the person the condition is dependent on
                # Dependency Rule: The connection that is being depended on to exist
                # Field: Target or Subject: The person whose perspective is being checked
                # Sub Field: If the perspective is a connection of the field (i.e. the subject's mother)
                # Field Rule: The connection being checked, framed as [<sub field> of ] <field> is <field rule> of [<field sub target> of ] <field target>
                # Field Target: The connection to the person opposite the field
                # Field Sub Target: If the target is a connection of the field target

                cases = {'Case 1': {'Condition': False, 'Field': ['Target'], 'Field Rule': 'Father', 'Field Target': ['Subject']},
                         'Case 2': {'Condition': True, 'Dependency': 'Subject', 'Dependency Rule': 'Mother',
                                    'Field': ['Target'], 'Field Rule': 'Spouse', 'Field Target': ['Subject', 'Mother']},
                         'Case 3': {'Condition': True, 'Dependency': 'Subject', 'Dependency Rule': 'Mother',
                                    'Field': ['Subject', 'Mother'], 'Field Rule': 'Spouse', 'Field Target': ['Subject']},
                         'Case 4': {'Condition': True, 'Dependency': 'Subject', 'Dependency Rule': 'Mother',
                                    'Field': ['Subject'], 'Field Rule': 'Child', 'Field Target': ['Target'],
                                    'With': ['Subject', 'Mother']},
                         'Case 5': {'Condition': True, 'Dependency': 'Subject', 'Dependency Rule': 'Mother',
                                    'Field': ['Subject'], 'Field Rule': 'Child', 'Field Target': ['Subject', 'Mother'],
                                    'With': ['Target']},
                         'Case 6': {'Condition': True, 'Dependency': 'Subject', 'Dependency Rule': '!Mother',
                                    'Field': ['Subject'], 'Field Rule': 'Child', 'Field Target': ['Target'],
                                    'With': ['unknown spouse']}}

                test_results = {}

                for c in cases:
                    test_case = cases[c]

                    run_test_case = False

                    # Is there a condition for the test case?
                    if test_case['Condition']:
                        # Does the dependency rule for the dependency not exist and follow the required absence?
                        if test_case['Dependency Rule'][0] == '!' and self.people[test_case['Dependency']].getConnection(test_case['Dependency Rule'][1:]) is None:
                            # Run the test case since the dependency rule is satisfied
                            run_test_case = True

                        # Does the dependency rule for the dependency exist and follow the required presence?
                        elif test_case['Dependency Rule'][0] != '!' and self.people[test_case['Dependency']].getConnection(test_case['Dependency Rule']) is not None:
                            # Run the test case since the dependency rule is satisfied
                            run_test_case = True
                        else:
                            # Don't run the test case since the dependency rule is not satisfied
                            run_test_case = False
                    else:
                        # Run the test case since there's no condition
                        run_test_case = True

                    if run_test_case:
                        left = self
                        for f in test_case['Field']:
                            left = left.getConnection(f)  # Returns the id of the person which "f" is the connection
                            if len(left) == 1:
                                left = self.personList[left[0]]  # Get the person object
                        left = left.personID

                        # Is there a with statement for the field rule
                        if 'With' in test_case:
                            # Get the with person for the given field rule
                            with_person = self
                            for f in test_case['With']:
                                with_person = with_person.getConnection(f)
                            # with_person = with_person
                        else:
                            # Get the target person for the given field rule
                            right = self
                            for f in test_case['Field Target']:
                                right = right.getConnection(f)
                            right = right['Field Rule']

                            test_results.update({c: left in self.people[test_case['Field Target']][test_case['Field Rule']]})

                return test_results

            elif self.action['Connection'] == 'Mother':
                cases = ['Target is mother of subject',
                         'If subject has father, then target is spouse of father',
                         'If subject has father, then father of subject is spouse of target',
                         'If subject has father, then subject is child of target with father of subject',
                         'If subject has father, then subject is child of father with target',
                         'If subject has no father, then subject is child of target with unknown spouse']

                cases[0] = self.subject.mother == self.target.personID

                if self.subject.father == -1:
                    cases[5] = self.subject.personID in self.target.spouses['unknown spouse']

                else:
                    cases[1] = self.subject.father in self.target.spouses
                    cases[2] = self.target.personID in self.subject.father.spouses
                    cases[3] = self.subject.personID in self.father.spouses[self.target.personID]
                    cases[4] = self.subject.personID in self.target.spouses[self.father.personID]

        return cases

class TestPerson:
    def __init__(self, personList, truthArray=None):
        self.personList = personList

        self.personID = uuid.uuid4().hex[:8]

        self.personList.update({self.personID: self})

        self.father = -1
        self.mother = -1
        self.spouses = {'unknown spouse': []}

        self.truth_array = None
        self.connections = {}

        if truthArray is not None:
            self.truth_array = truthArray

            pos = 5

            for t in reversed(self.truth_array):
                if t == 1:
                    if pos == 5:
                        spouse = TestPerson(self.personList)
                        self.addSpouse(spouse.personID)
                        spouse.addSpouse(self.personID)

                    elif pos == 4:
                        child_spouse = TestPerson(self.personList)
                        child_spouse.addFather(self.personID)

                        for s in self.spouses:
                            if s != 'unknown spouse':
                                self.addChild(child_spouse.personID, s)

                    elif pos == 3:
                        child_no_spouse = TestPerson(self.personList)
                        child_no_spouse.addFather(self.personID)
                        self.addChild(child_no_spouse.personID, None)

                    elif pos == 2:
                        mother_spouse = TestPerson(self.personList)
                        self.addMother(mother_spouse.personID)

                        father_spouse = TestPerson(self.personList)
                        self.addFather(father_spouse.personID)

                        father_spouse.addSpouse(mother_spouse)
                        mother_spouse.addSpouse(father_spouse)

                    elif pos == 1:
                        mother_no_spouse = TestPerson(self.personList)
                        self.addMother(mother_no_spouse.personID)

                    elif pos == 0:
                        father_no_spouse = TestPerson(self.personList)
                        self.addFather(father_no_spouse.personID)

                pos -= 1
    def getConnection(self, connection):
        if connection == 'Father':
            return self.personList[self.father]
        elif connection == 'Mother':
            return self.personList[self.mother]


    def addFather(self, father):
        if isinstance(father, str):
            fatherID = father
        elif isinstance(father, TestPerson):
            fatherID = father.personID
        else:
            print('ERROR: Cannot add ' + str(father) + ' as Father. Invalid type')

        if fatherID in self.connections:
            print('ERROR: Cannot add ' + str(fatherID) + ' as Father. Already a connection as ' + str(self.connections[fatherID]))
        else:
            self.father = fatherID
            self.connections.update({fatherID: 'Father'})

    def removeFather(self):
        self.connections.pop(self.father)
        self.father = -1

    def addMother(self, mother):
        if isinstance(mother, str):
            motherID = mother
        elif isinstance(mother, TestPerson):
            motherID = mother.personID
        else:
            print('ERROR: Cannot add ' + str(mother) + ' as Mother. Invalid type')

        if motherID in self.connections:
            print('ERROR: Cannot add ' + str(motherID) + ' as Mother. Already a connection as ' + str(self.connections[motherID]))
        else:
            self.mother = motherID
            self.connections.update({motherID: 'Mother'})

    def removeMother(self):
        self.connections.pop(self.mother)
        self.mother = -1

    def addSpouse(self, spouse):
        if isinstance(spouse, str):
            spouseID = spouse
        elif isinstance(spouse, TestPerson):
            spouseID = spouse.personID
        else:
            print('ERROR: Cannot add ' + str(spouse) + ' as Spouse. Invalid type')

        if spouseID in self.spouses:
            print('Cannot add ' + str(spouseID) + ' as Spouse. Already a spouse of ' + str(self.personID))
        elif spouseID in self.connections:
            print('ERROR: Cannot add ' + str(spouseID) + ' as Spouse. Already a connection as ' + str(self.connections[spouseID]))
        else:
            self.spouses.update({str(spouseID): []})
            self.connections.update({spouseID: 'Spouse'})

    def removeSpouse(self, spouse):
        if isinstance(spouse, str):
            spouseID = spouse
        elif isinstance(spouse, TestPerson):
            spouseID = spouse.personID
        else:
            print('WARNING: Cannot remove ' + str(spouse) + ' as Spouse. Invalid type')

        if spouseID not in self.connections:
            print('WARNING: Cannot remove ' + str(spouseID) + 'as spouse. Not currently a connection')

        elif spouseID not in self.spouses:
            print('WARNING: Cannot remove ' + str(spouseID) + 'as spouse. Not a spouse of ' + str(self.personID))
        else:
            for c in self.spouses[spouseID]:
                self.spouses['unknown spouse'].append(c)

            self.spouses.pop(spouseID)
            self.connections.pop(spouseID)


    def addChild(self, child, spouse):
        # Get right type of spouse ID
        if isinstance(spouse, str):
            spouseID = spouse
        elif isinstance(spouse, TestPerson):
            spouseID = spouse.personID
        else:
            print('ERROR: Cannot add ' + str(spouse) + ' as Spouse. Invalid type')

        # Get right type of child ID
        if isinstance(child, str):
            childID = child
        elif isinstance(child, TestPerson):
            childID = child.personID
        else:
            print('ERROR: Cannot add ' + str(child) + ' as Child. Invalid type')

        if childID in self.connections:
            print('ERROR: Cannot add ' + str(childID) + ' as Child. Already a connection as ' + str(self.connections[childID]))

        if spouseID is None:
            if childID in self.spouses['unknown spouse']:
                print('ERROR: Cannot add ' + str(childID) + ' as Child. Already a child of unknown spouse with ' + str(self.personID))
            else:
                self.spouses['unknown spouse'].append(childID)
                self.connections.update({childID: 'Child'})

        elif spouseID not in self.spouses:
            print('Cannot add child. ' + str(spouseID) + ' is not a spouse of ' + str(self.personID))

        elif childID in self.spouses[spouseID]:
            print('Cannot add child: ' + str(childID) + ' is already a child of ' + str(spouseID) + ' with ' + str(self.personID))

        else:
            self.spouses[spouseID].append(childID)
            self.connections.update({childID: 'Child'})

    def removeChild(self, child):
        if isinstance(child, str):
            childID = child
        elif isinstance(child, TestPerson):
            childID = child.personID
        else:
            print('WARNING: Cannot remove ' + str(child) + ' as Child. Invalid type')

        if childID not in self.connections:
            print('WARNING: Cannot remove ' + str(child) + ' as Child. Not currently a connection')

        removed = False
        for s in self.spouses:
            if childID in self.spouses[s]:
                self.spouses[s].pop(childID)
                self.connections.pop(childID)

                removed = True

        if not removed:
            print('ERROR: Could not find ' + str(childID) + ' among spouses despite having a connection: ' + str(self.connections[childID]))
            self.connections.pop(childID)


    def string_print(self):
        toString = 'Father: ' + str(self.father) + '\nMother: ' + str(self.mother) + '\nSpouses:' + str(self.spouses)

        print(toString)

    def print_connections(self):
        print(self.connections)


class BinaryNumber:
    def __init__(self, initial=None):
        if initial is None:
            self.number = 0
            self.digits = 1
        else:
            self.number = self.convertToBinary(initial)
            self.digits = math.floor(math.log(self.number, 2))

    def valueAt(self, index):
        if index >= self.digits:
            print('ERROR: Index out of bounds. ' + str(index) + ' >= ' + str(self.digits) + ', ' + str(self.number))
            return 0
        else:
            print('Value Retrieved at: ' + str(index) + ' in ' + str(self.number))
            return str(self.number)[index]

    def convertToBinary(self, number):
        remainder = number

        binNumber = 0

        while remainder > 0:
            digits = math.floor(math.log(remainder, 2))
            binNumber += 10 ** digits
            remainder -= 2 ** digits

        # print('Binary: ' + str(binNumber))

        return binNumber

    def increment(self):
        stringNumber = str(self.number)

        pos = len(stringNumber) - 1
        flipped = False
        for d in reversed(stringNumber):
            if int(d) == 0:
                stringNumber = stringNumber[:pos] + '1' + stringNumber[pos + 1:]
                flipped = True
                break
            else:
                stringNumber = stringNumber[:pos] + '0' + stringNumber[pos + 1:]

            pos -= 1

        if not flipped:
            '1' + stringNumber
            self.digits += 1

        self.number = int(stringNumber)
        # print('Increment: ' + str(self.number))

    def decrement(self):
        if self.number == 0:
            print('Number is ' + str(self.number) + '. Cannot decrement')
        else:
            stringNumber = str(self.number)

            pos = len(stringNumber) - 1
            flipped = False
            for d in reversed(stringNumber):
                if int(d) == 1:
                    stringNumber = stringNumber[:pos] + '0' + stringNumber[pos + 1:]
                    flipped = True
                    break
                else:
                    stringNumber = stringNumber[:pos] + '1' + stringNumber[pos + 1:]

                pos -= 1

            if not flipped:
                '0' + stringNumber
                self.digits -= 1

            self.number = int(stringNumber)
            # print('Decrement: ' + str(self.number))


def main():
    app = RelationTest()

    print('Code Executed and Log Written')


if __name__ == '__main__':
    main()
