An Overview of the Technical Layout, Flow, and Specifications of the code:

# Objects
Three objects are used to hold data: Person, Title, and Reign
## Person
### Fields
- ID: The unique 8-character ID of the person
- Name: The name of the person
- Nickname: Any additional moniker they were known by
- Primary Title: The realms they were mainly known to rule over
- Gender: Man or Woman
- Birth Date: Free text indicating when they were born
  - Could be year, month, date
- Death Date: Free text indicating when they died
  - Could be year, month, date
- Father: The ID of the person object who is their father
- Mother: The ID of the person object who is their mother
- Spouse(s): A dictionary of person IDs who were their spouse
  - Children: Each spouse has a list of person IDs with whom children were shared
    - Children with unknown or missing 2nd parents are included under a default unknown spouse
- Reign List: The list of reign IDs that apply to them

## Title
### Fields

## Reign
### Fields

# Storage
## Person
Data is stored in a YAML named "people.yaml" in the following format:
- Letters indicate variable entries

| Location | Field Name    | Data Type        | Description                                                            | Notes                                                                                                     |
|----------|---------------|------------------|------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| a        | ID            | Alphanumeric (8) | The unique 8-character ID of the person                                | Hidden from user                                                                                          |
| a.1      | Birth Date    | Text             | The date the person was born <br /> Preferred format: <[m]m/[d]d/yyyy> |                                                                                                           |
| a.2      | Death Date    | Text             | The date the person died                                               |                                                                                                           |
| a.3      | Father        | Alphanumeric (8) | The ID of the person who is this person’s father                       |                                                                                                           |
| a.4      | Gender        | Integer (1)      | The gender of the person <br /> Allowed values: 0 (Man), 1 (Woman)     |                                                                                                           |
| a.5      | Mother        | Alphanumeric (8) | The ID of the person who is this person’s father                       |                                                                                                           |
| a.6      | Name          | Text             | The name of this person                                                | Should be populated                                                                                       |
| a.7      | Nickname      | Text             | The nickname for this person                                           | Can be blank                                                                                              |
| a.8      | Primary Title | Text             | The primary title(s) associated with this person                       | Temporarily set by user, will eventually be a toggle within a person's list of titles <br /> Can be blank |
| a.9      | Reign List    | Dictionary       | The dictionary of reigns for this person                               |                                                                                                           |
| a.9.b    | Reign ID      | Alphanumeric (8) | The ID of each reign                                                   |                                                                                                           |
| a.9.b.1  | End Date      | Text             | The date the reign ended                                               |                                                                                                           |
| a.9.b.2  | Predecessor   | Alphanumeric (8) | The ID of the predecessor reign                                        | Can be null                                                                                               |
| a.9.b.3  | Start Date    | Text             | The date the reign began                                               |                                                                                                           |
| a.9.b.4  | Successor     | Alphanumeric (8) | The ID of the successor reign                                          | Can be null                                                                                               |
| a.9.b.5  | Title ID      | Alphanumeric (8) | The title for which the reign occurred                                 | Must be populated                                                                                         |
| a.10     | Spouses       | Dictionary       | The dictionary of spouses for this person                              |                                                                                                           |
| a.10.c   | Spouse ID     | Alphanumeric (8) | The ID of the spouse (-1 if unknown)                                   |                                                                                                           |
| a.10.c.d | Child ID      | Alphanumeric (8) | The list of IDs for each child with the given spouse                   |                                                                                                           |


# Code Organization
## Branching and Pull Requests
### Rules:
1. Don't commit changes directly to master
2. Branches should be for smaller, discrete changes
3. Merge commits on one branch to all other branches if possible
