# dash_app_render
deploying dash app via Render

Note:
- the list of authors currently includes male authors (will remove later)
- there might be errors that I have not found yet! 

Features (visit by order):
1. Author dropdown
   provides a list of authors
   when an author is selected, an image of the author will be displayed in the right 
   can search author names by typing in the dropdown
   click 'x' at the right to clear the dropdown
3. Location dropdown
   when an author is selected, the list of locations visited by the selected author is displayed
   the list of locations change depending on the author selected
   when a location is selected, the map zooms into the selected location
   click 'x' at the right to clear the dropdown, which will also reset the scale of the map
5. Next button
   clicking the 'next' button will output traces of the itiniary of the selected author by order
   the details of each trip will be displayed under the author's photo (includes index, date, and locations)
6. Previous button
   clicking the 'previous' button will output the previous trace of the itiniary of the selected author
7. '+' button (zoom-in button)
   '+' button will be active only once the 'next' button has been pressed
   when '+' button is clicked, the map will zoom in to give a better view of the current trace (described under the author's photo)
   the '+' button can only be clicked once per trace (clicking more than once will not result in an error, but the map will not zoom in further)
9. '-' button (zoom-out button)
   '-' button will be active when the map is zoomed in
   the map will zoom out until the scale of the map is reset 
10. Markers
    each markers on the map (pink color) can be clicked
    its information (location and date) will be displayed under the author's photo and the details about the current trace
