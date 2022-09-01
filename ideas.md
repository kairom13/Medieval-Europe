# An Overview of Ideas I Want to Implement

## Person Page Designs
Each person, both displaying and editing, should have 4 sections to display:
1. Personal Information
2. Held Titles
3. Biography
4. Map

### Personal Information
The immutable information that describes this person
Includes:
- Name and Nickname
- Gender
- Dynasty
- Birth Date
- Death Date
- Relatives
  - Father, Mother
  - Spouse(s) (include marriage date)
  - Children (include birth dates)

### Held Titles
The titles that his person held throughout their life
List as a series of reigns
For each reign that this person had:
- The name of the title they held
- The start and end date of their reign
- The predecessor or successor, if applicable

### Biography
A list of events that the person did or was involved in.
Can help explain values of other sections (i.e. reigns, spouses, death date, etc)
Each event should be accompanied with a date
Each event may include links to other objects (People, Places, Titles)

### Map
A map of the realms this person ruled (or was associated with)
Includes timeline slider
Realms based off of associated reigns
- Get reigns that contain the given date
- Display polygons of the realm for that date
