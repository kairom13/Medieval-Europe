# List of Ideas that I Want to Implement
## Dynasties
1. Should be its own object
   1. Allows for enhancements to focus on just the dynasty
2. Will have its own list, edit, and display pages
3. Will have its own save file
   1. Need to determine data structure (likely binary search tree)
4. Would like to include an image of the coat of arms
5. Would like to include a map (not sure of implementation)
   1. Likely need a slider to show a certain date
6. Would like to include a graph of members
   1. Need to determine how to display (not sure how well networkx would do)
   2. This would be the best way to go to navigate to individual rulers
   3. Women can have links to husbands and their dynasties
   4. Cadet branches can have links to those dynasties

## Dates as usable information
1. Currently, just stored as strings, can be stored as information
2. Need to handle different formats (i.e. just year, just month, etch)
   1. Also need date ranges, bounds, options
      1. (i.e. 1070-1080, after 1227, 1082 or 1085)
3. Would be used for timeline sliders, downloadable data

## Title Predecessors and Successors
1. Would allow reigns to be linked between titles
   1. Restrictions on link
      1. Can only happen once
      2. Based on the links on the title page
      3. Can only be in the same direction
         1. If the title has a successor, then a reign can only add a successor to a reign in the successor title
         2. If the title has a predecessor, then a reign can only add a predecessor to a reign in the predecessor title