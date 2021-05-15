from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import time 
from threading import Thread



# Filepaths for save data
saved_dir_path = os.path.join(os.path.expanduser('~/Documents'), 'Arrowverse Episode Tracker Data') 
saved_episodes_path = os.path.join(saved_dir_path, 'episodes.json')
saved_filters_path = os.path.join(saved_dir_path, 'filters.json')

# Dictionaries for keeping track of states
episodes = {}
filters = {}

# Counters for current displayed episode list
num_displayed = 0
num_watched_in_display = 0

# Episode List URL to retrieve data from
episode_list_url = 'https://flash-arrow-order.herokuapp.com/'

# Is the app currently updating the list?
is_updating = False

# GUI components
root = tk.Tk()
list_frame = tk.Frame(root)
list_scrollbar = tk.Scrollbar(list_frame)
displayed_list = ttk.Treeview(list_frame,columns=('Number', 'Series', 'Episode Number', 'Episode Name', 'Air Date', 'Watched?'),show="headings", yscrollcommand=list_scrollbar.set, selectmode='browse')
buttons_menu = tk.Frame(root)
update_list_button = tk.Button(buttons_menu, text='Refresh List')
filters_button = tk.Button(buttons_menu, text='Filters')
reset_watched_button = tk.Button(buttons_menu, text='Reset Watched')
progress_bar_frame = tk.Frame(root)
progress_bar_label = tk.Label(progress_bar_frame, text='Watch Progress:')
watched_progress_bar = ttk.Progressbar(progress_bar_frame, orient='horizontal', mode='determinate', length=200)
style = ttk.Style(progress_bar_frame)

'''
Check if save files exist on the system; create files if not
Return 'True' if files already existed; 'False' if files did not exist
'''
def check_for_files():
    result = True
    if not os.path.exists(saved_dir_path):
        result = False
        os.mkdir(saved_dir_path)
    if not os.path.exists(saved_episodes_path):
        result = False
        f = open(saved_episodes_path,'w+')
        f.write('{}')
        f.close()
    if not os.path.exists(saved_filters_path):
        result = False
        f = open(saved_filters_path,'w+')
        f.write('{}')
        f.close()
    return result

'''
Save the current state of the episode list and filters to the system
'''
def save_data():
    check_for_files()
    f = open(saved_episodes_path, 'w')
    json.dump(episodes, f)
    f.close()
    f = open(saved_filters_path, 'w')
    json.dump(filters, f)
    f.close()

'''
Load the json data into variables 
'''
def load_data():
    global episodes
    global filters
    check_for_files()
    f = open(saved_episodes_path)
    try:
        episodes = json.load(f)
    except:
        episodes = {}
    f.close()
    f = open(saved_filters_path)
    try:
        filters = json.load(f)
    except:
        filters = {}
    f.close()

'''
Update the watched progress bar to the current value
'''
def update_watched_progress_bar():
    percentage = 0
    try:
        percentage = (float(num_watched_in_display) / float(num_displayed)) * 100.0
    except:
        percentage = 0
    watched_progress_bar['value'] = percentage
    style.configure('text.Horizontal.TProgressbar', text='{:g} %'.format(round(percentage, 2)))

'''
Update episodes and filters lists using the website data
'''
def update_list_func():
    global episodes
    global filters
    options = Options()
    options.add_argument('--headless')
    web = webdriver.Chrome(options=options)
    web.get(episode_list_url)

    table = web.find_element_by_id('episode-list').find_element_by_tag_name('tbody')

    for row in table.find_elements_by_css_selector('tr'):
        episode_data = []
        for cell in row.find_elements_by_tag_name('td'):
            episode_data.append(cell.text)
        episode_data.append(row.get_attribute('data-href'))
        episode_data.append(False)
        if episode_data[0] not in episodes:
            episodes[episode_data[0]] = { 'series' : episode_data[1], 'season_episode' : episode_data[2], 'name' : episode_data[3], 'air_date' : episode_data[4], 'info_url' : episode_data[5], 'watched' : episode_data[6] }  
        if episode_data[1] not in filters:
            filters[episode_data[1]] = False

    web.close()

    print('done updating list')
    display_list()

'''
Test function for progress bar visualization
'''
def test_func(sleep_time):
    time.sleep(sleep_time)

'''
Threading for progress bar window
'''
def progress_bar_thread():
    global is_updating
    popup = tk.Toplevel()
    popup.geometry('250x100')
    label = tk.Label(popup, text='Updating List...')
    label.pack(pady=20)
    progress_bar = ttk.Progressbar(popup, orient='horizontal', mode='indeterminate', length=200)
    progress_bar.pack()
    progress_bar.start(interval=10)
    update_list_func()
    #test_func(4)
    progress_bar.stop()
    popup.destroy()
    is_updating = False 

'''
Update episodes and filters lists using the website data and display a popup progress bar (using threading)
'''
def update_list():
    global is_updating
    if not is_updating:
        is_updating = True
        Thread(target=progress_bar_thread).start()

'''
Convert the boolean status to 'Yes' or 'No'
'''
def convert_to_yes_no(status):
    if (status is True):
        return 'Yes'
    else:
        return 'No'

'''
Display the episode list with the filters applied
'''
def display_list():
    global num_displayed
    global num_watched_in_display
    displayed_list.delete(*displayed_list.get_children())
    num_displayed = 0
    num_watched_in_display = 0
    for key in episodes:
        if filters[episodes[key]['series']] == False:
            watched_status = episodes[key]['watched']
            if watched_status:
                num_watched_in_display += 1
            displayed_list.insert("", 'end', values=(key, episodes[key]['series'], episodes[key]['season_episode'], episodes[key]['name'], episodes[key]['air_date'], convert_to_yes_no(watched_status)))
            num_displayed += 1
    update_watched_progress_bar()

'''
Reset every episode's 'watched' value to False
'''
def reset_watched():
    if not is_updating:
        if messagebox.askokcancel('Reset Watched', 'Are you sure you want to reset your watched episodes?'):
            for key in episodes:
                episodes[key]['watched'] = False
            display_list()

'''
Reset all filters to false
'''
def reset_filters(filters_list):
    filters_list.delete(*filters_list.get_children())
    if not is_updating:
        for key in filters:
            filters[key] = False
            filters_list.insert("", 'end', values=(key, convert_to_yes_no(not filters[key])))     

'''
Change status of 'watched' attribute
'''
def toggle_watched(event):
    global num_watched_in_display
    if not is_updating:
        key = str(displayed_list.item(displayed_list.focus())['values'][0])
        watched_status = episodes[key]['watched']
        if not watched_status:
            num_watched_in_display += 1
        else:
            num_watched_in_display -= 1
        episodes[key]['watched'] = not watched_status
        displayed_list.item(displayed_list.focus(), values=(key, episodes[key]['series'], episodes[key]['season_episode'], episodes[key]['name'], episodes[key]['air_date'], convert_to_yes_no(episodes[key]['watched'])))
        update_watched_progress_bar()

'''
Open the specified URL in the user's default browser
'''
def open_url(url_to_open):
    if not is_updating:
        webbrowser.open(url_to_open)

'''
Save the data and close the app
'''
def exit_app():
    if messagebox.askokcancel('Quit', 'Do you want to quit?'):
        save_data()
        root.destroy() 

'''
Toggle whether a series is included or not
'''
def toggle_filter(event, filters_list):
    key = str(filters_list.item(filters_list.focus())['values'][0])
    filters[key] = not filters[key]
    filters_list.item(filters_list.focus(), values=(key, convert_to_yes_no(not filters[key])))

'''
Reload the list with the filters applied
'''
def apply_filters(window):
    display_list()
    window.destroy()

'''
Start filter selection process by opening a popup window
'''
def filter_selection():
    if not is_updating:
        filter_popup = tk.Toplevel()
        filter_popup.geometry('750x325')
        filters_list_frame = tk.Frame(filter_popup)
        filters_list_scrollbar = tk.Scrollbar(filters_list_frame)
        filters_list = ttk.Treeview(filters_list_frame,columns=('Series', 'Include?'),show="headings", yscrollcommand=filters_list_scrollbar.set, selectmode='browse')
        reset_filters_button = tk.Button(filter_popup, text='Reset Filters')
        reset_filters_button.config(command=lambda:reset_filters(filters_list))
        reset_filters_button.pack(side='top', anchor='nw')
        label = tk.Label(filter_popup, text='Select Series to Exclude From the List')
        label.pack(pady=20)
        filters_list_frame.pack()
        filters_list_scrollbar.config(command=filters_list.yview)
        filters_list_scrollbar.pack(side='right', fill='y')
        filters_list.heading('#1', text='Series')
        filters_list.heading('#2', text='Include?')
        filters_list.column('#1', stretch='YES', width=200)
        filters_list.column('#2', stretch='YES', width=60)
        filters_list.bind('<ButtonRelease-1>', lambda event: toggle_filter(event, filters_list))
        filters_list.pack()
        filters_list.delete(*filters_list.get_children())
        for key in filters:
            filters_list.insert("", 'end', values=(key, convert_to_yes_no(not filters[key])))
        filter_popup.protocol("WM_DELETE_WINDOW", lambda: apply_filters(filter_popup))

'''
Start up the GUI 
'''
def initialize_gui():
    root.title('Arrowverse Episode Tracker')
    root.geometry('750x400')
    style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
    style.configure('text.Horizontal.TProgressbar', text='0 %')
    buttons_menu.pack(side='top', anchor='nw')
    update_list_button.config(command=update_list)
    update_list_button.grid(row=0, column=0)
    filters_button.config(command=filter_selection)
    filters_button.grid(row=0, column=1)
    reset_watched_button.config(command=reset_watched)
    reset_watched_button.grid(row=0, column=2)
    list_frame.pack(pady=20)
    list_scrollbar.config(command=displayed_list.yview)
    list_scrollbar.pack(side='right', fill='y')
    displayed_list.heading('#1', text='Number')
    displayed_list.heading('#2', text='Series')
    displayed_list.heading('#3', text='Episode Number')
    displayed_list.heading('#4', text='Episode Name')
    displayed_list.heading('#5', text='Air Date')
    displayed_list.heading('#6', text='Watched?')
    displayed_list.column('#1', stretch='YES', width=60)
    displayed_list.column('#2', stretch='YES', width=100)
    displayed_list.column('#3', stretch='YES', width=100)
    displayed_list.column('#4', stretch='YES', width=150)
    displayed_list.column('#5', stretch='YES', width=125)
    displayed_list.column('#6', stretch='YES', width=60)
    displayed_list.bind('<Double-1>', lambda f: open_url(episodes[str(displayed_list.item(displayed_list.focus())['values'][0])]['info_url']))
    displayed_list.bind('<ButtonRelease-1>', toggle_watched)
    displayed_list.pack()
    progress_bar_frame.pack()
    progress_bar_label.grid(row=0, column=0)
    watched_progress_bar.config(style='text.Horizontal.TProgressbar')
    watched_progress_bar.grid(row=0, column=1)
    load_data()
    display_list()
    root.protocol("WM_DELETE_WINDOW", exit_app)
    root.mainloop()


initialize_gui()