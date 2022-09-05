# An Overview of the Database Application

## Person Page Designs
Each person, both displaying and editing, should have 4 sections to display:
1. Personal Information
2. Held Titles
3. Event List
4. Place Map

### Personal Information
The immutable information that describes this person
Includes:
- Name and Nickname
- Gender
- Dynasty (Probably an object)
- Birth Date
- Death Date
- Relatives
  - Father, Mother
  - Spouse(s) (include marriage date)
  - Children
    - Include Birth Date
    - Ordered by age

### Held Titles
The titles that his person held throughout their life
List as a series of reigns
For each reign that this person had:
- The name of the title they held
- The start and end date of their reign
- The predecessor or successor, if applicable
- Any junior reigns (option to merge/unmerge reigns)
- Co/anti rulers
  - Co-ruler: Another person worked with this person to rule
  - Anti-ruler: Another person competed with this person for rule
- Need a system for ordering reigns
  - Ensure primary reign is first
  - Allow users to drag to reorder? Specify order?

### Event List
A list of events that the person did or was involved in.
Can help explain values of other sections (i.e. reigns, spouses, death date, etc)
Each event should be accompanied by a date
Each event may include links to other objects (People, Places, Titles)

### Place Map
A map of the places this person ruled (or was associated with)
Includes timeline slider (maybe)
Places based off of associated reigns
- Get places associated with the person's reigns
  - Could display all places and highlight the one's this person ruled
  - Use Voronoi polygons to better show lands ruled

## Title Page Designs
For each title, have 4 sections to display:
1. Identifying Information
2. Chronology of Reigns
3. Event List
4. Place Map

### Identifying Information
Attributes that identify this title
- Realm Name
  - The name of the place regardless of rank or title
  - Luxembourg, Bavaria, Germany, Ulm, etc
- Title Name
  - The name of the rank this title holds
  - County, Duchy, Kingdom, City, etc
- Male/Female Ruler Titles
  - How the ruler of the title is referenced
  - Duke/Duchess, King/Queen, Count/Countess, etc
- Someway to identify rank? Probably should use separate page to have saveable title info and can specify relative ranks

### Chronology of Reigns
An ordered list of the reigns for this title
