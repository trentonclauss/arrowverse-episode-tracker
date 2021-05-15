# Arrowverse Episode Tracker

*Keep track of your viewing progress in the Arrowverse!*

To launch the application, double click the "arrowverse_episode_tracker.pyw" file.

This application gathers data from https://flash-arrow-order.herokuapp.com/ and generates a list of every episode in the Arrowverse. To download the current list of episodes, click the "Refresh List" button and wait for the download to finish (this may take a few minutes).

![MainScreen](https://github.com/trentonclauss/arrowverse-episode-tracker/blob/main/main-screen.PNG?raw=true)

*__Just click on an episode in the list to toggle its watched status. Double click an episode to open the wiki page for that episode.__*

![FiltersScreen](https://github.com/trentonclauss/arrowverse-episode-tracker/blob/main/filters-screen.PNG?raw=true)

*__You can also exclude series from the list via the "Filters" menu.__*

## Troubleshooting

*This code was developed with Python 3.9.2 on Windows 10.*

- Make sure that you have Selenium for Python installed properly.
- Make sure that the save files "..\Documents\Arrowverse Episode Tracker Data" are formatted properly. *(If needed/corrupted, delete the save files.)*
- Press the "Refresh List" button if nothing is displayed.

I suggest that you first run the ".py" version through an editor to see if any errors pop up in the terminal. Once you verify that it works, launch the application from the file explorer via the ".pyw" version.
