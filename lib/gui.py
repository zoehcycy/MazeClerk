import pandas as pd
from tkinter import *
from tkinter import ttk
from datetime import datetime
from tkinter import filedialog

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


def simple_get(widget):
    return widget.get()


def get_required(widget):
    if widget.get() == '':
        warning = Tk()
        warning.wm_attributes('-topmost', 1)  # pin the window to top
        warning.title('Warning')
        lbl = Label(warning, text='End Time must be entered.')
        lbl.pack()
        warning.mainloop()
        exit()
    else:
        return int(widget.get())
    return


class GUI(object):

    def __init__(self, home):
        super().__init__()
        self.my_gui = Tk()
        self.home = home
        self.data_entries = dict()
        self.entries = []
        self.build_widgets()

    def run(self):
        return self.my_gui.mainloop()

    def clear_button_pushed(self):
        self.entry_id.delete(0, END)
        self.entry_weight.delete(0, END)
        self.entry_rme.delete(0, END)
        self.entry_wme.delete(0, END)
        self.entry_notes.delete(0, END)

    def get_input(self, key: str):

        normal_text_field = {
            'date', 'mouse_id','baited_arms','baited_arms_retrieved','other_notes',
        }

        required_field = {
            'weight','reference_memory_errors','working_memory_errors',
        }

        int_field = {
            'weight',
            'baited_arms_retrieved',
            'reference_memory_errors',
            'working_memory_errors',
        }

        ret = None
        if key in normal_text_field:
            ret = simple_get(self.data_entries[key])
        elif key in required_field:
            ret = get_required(self.data_entries[key])
        else:
            raise ValueError('unknown key:' + key)

        if key in int_field:
            ret = int(ret)

        return ret

    def close_button_pushed(self):
        self.my_gui.quit()
        self.my_gui.destroy()

    def get_mouse_id(self):
        return self.data_entries['mouse_id'].get()

    def plot_history_data(self, df, m_ID):

        root = Tk()
        root.wm_attributes('-topmost', 1)  # pin the window to top
        root.wm_title("Snapshot of history data")

        fig = Figure(figsize=(5, 12))
        ##---------------------------Plot Weight----------------------##
        y1 = df['Weight']
        ax1 = fig.add_subplot(311)
        ax1.plot(y1)
        ax1.set_title('Weight of ' + m_ID)
        ##---------------------------Plot RME----------------------##
        y2 = df['Reference Memory Errors']
        ax2 = fig.add_subplot(312)
        ax2.plot(y2)
        ax2.set_title('RME of ' + m_ID)
        ##---------------------------Plot WME----------------------##
        y3 = df['Working Memory Errors']
        ax3 = fig.add_subplot(313)
        ax3.plot(y3)
        ax3.set_title('WME of ' + m_ID)
        canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        def on_key_press(event):
            print("you pressed {}".format(event.key))
            #key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect("key_press_event", on_key_press)

        def _quit():
            root.quit()  # stops mainloop
            root.destroy()  # this is necessary on Windows to prevent
            # Fatal Python Error: PyEval_RestoreThread: NULL tstate

        button = Button(master=root, text="Quit", command=_quit)
        button.pack(side=BOTTOM)

        root.mainloop()

    def append_button_pushed(self):
        prompt = Tk()
        prompt.wm_attributes('-topmost', 1)  # pin the window to top
        prompt.withdraw()
        file_path = filedialog.askopenfilename()
        old_file = pd.read_excel(file_path, sheet_name=None)

        # create save_path with time stamp
        t = datetime.now()
        time_stamp = '_'.join([t.strftime('%Y'), t.strftime('%m'), t.strftime('%d'), \
                               t.strftime('%H'), t.strftime('%M'), t.strftime('%S')])
        save_path = self.home + '\\Experiment_Data\\RAM_Experimental_Data_' + time_stamp + '.xlsx'

        m_IDs = list(old_file.keys())
        m_ID = str('ID_N' + self.get_mouse_id())

        if m_ID in m_IDs:
            print('------------Successfully Found Mouse ' + m_ID)

            attributes = ['Date','Weight','Baited Arms','Baited Arms Retrieved',\
                'Reference Memory Errors','Working Memory Errors','Other Notes']

            new_dict = {}

            for attribute in attributes[:]:
                # append data using callbacks
                new_dict[attribute] = list(old_file[m_ID][attribute])
                n = attribute.lower()
                name = '_'.join(n.split())
                c = self.get_input(name)
                new_dict[attribute].append(c)

            new_df = pd.DataFrame(new_dict)  # new_dict contains updated data of this animal

            with pd.ExcelWriter(save_path) as writer:
                new_df.to_excel(writer, sheet_name=m_ID)
                m_IDs.remove(m_ID)
                for other in m_IDs:
                    old_file[other].to_excel(writer, sheet_name=other,
                                             index=False)  # update record of this animal, others remain unchanged

            print('------------New excel file saved:' + save_path)

            self.plot_history_data(new_df, m_ID)  # plot history data

        else:
            warning = Tk()
            warning.wm_attributes('-topmost', 1)  # pin the window to top
            warning.title('Warning')
            lbl = Label(warning,
                        text='Mouse ID does not exist, please check the input.\nFor adding new mouse, please run new_mouse.py')
            lbl.pack()
            warning.mainloop()
            exit()

    def build_widgets(self):

        frame = Frame(master=self.my_gui, width=600, height=400)
        frame.pack()
        begin = 50
        gap = 40
        wid = 300
        title = Label(self.my_gui, font='bold', text='Enter Mouse Data.Save mouse data into mat structure.')
        title.place(x=10, y=10)

        self.label_id = Label(self.my_gui, text='Mouse ID (numbers only)*')
        self.label_id.place(x=10, y=begin)
        self.entry_id = Entry(self.my_gui, bd=2)
        self.entry_id.place(x=wid, y=begin)
        self.data_entries['mouse_id'] = self.entry_id
        self.entries.append(self.entry_id)

        begin = begin + gap

        self.label_date = Label(self.my_gui, text='Date*')
        self.label_date.place(x=10, y=begin)
        self.entry_date = Entry(self.my_gui, bd=2)
        t = datetime.now()
        self.entry_date.insert(INSERT, '-'.join([t.strftime('%d'), t.strftime('%b'), t.strftime('%y')]))
        self.entry_date.place(x=wid, y=begin)
        self.data_entries['date'] = self.entry_date

        begin = begin + gap

        self.label_weight = Label(self.my_gui, text='Weight*')
        self.label_weight.place(x=10, y=begin)
        self.entry_weight = Entry(self.my_gui, bd=2)
        self.entry_weight.place(x=wid, y=begin)
        self.data_entries['weight'] = self.entry_weight
        self.entries.append(self.entry_weight)

        begin = begin + gap

        self.label_baited_arms = Label(self.my_gui, text='Baited Arms*')
        self.label_baited_arms.place(x=10, y=begin)
        self.baited_arms = StringVar()
        self.combobox_baited_arms = ttk.Combobox(self.my_gui, textvariable=self.baited_arms)
        self.combobox_baited_arms.place(x=wid, y=begin)
        self.combobox_baited_arms['value'] = ('A,C,D,F', 'B,D,F,H', 'B,C,E,G', 'A,B,F,G')  # values for selection
        self.combobox_baited_arms.current(0)  # default value
        self.data_entries['baited_arms'] = self.combobox_baited_arms

        begin = begin + gap

        self.label_retrieved_arms = Label(self.my_gui, text='Baited Arms Retrieved*')
        self.label_retrieved_arms.place(x=10, y=begin)
        self.baited_arms_retrieved = StringVar()
        self.combobox_retrieved_arms = ttk.Combobox(self.my_gui,
                                       textvariable=self.baited_arms_retrieved)
        self.combobox_retrieved_arms.place(x=wid, y=begin)
        self.combobox_retrieved_arms['value'] = (0, 1, 2, 3, 4)  # values for selection
        self.combobox_retrieved_arms.current(0)  # default value
        self.data_entries['baited_arms_retrieved'] = self.combobox_retrieved_arms

        begin = begin + gap

        self.label_rme = Label(self.my_gui, text='Reference Memory Errors*')
        self.label_rme.place(x=10, y=begin)
        self.entry_rme = Entry(self.my_gui, bd=2)
        self.entry_rme.place(x=wid, y=begin)
        self.data_entries['reference_memory_errors'] = self.entry_rme

        begin = begin + gap

        self.label_wme = Label(self.my_gui, text='Working Memory Errors*')
        self.label_wme.place(x=10, y=begin)
        self.entry_wme = Entry(self.my_gui, bd=2)
        self.entry_wme.place(x=wid, y=begin)
        self.data_entries['working_memory_errors'] = self.entry_wme

        begin = begin + gap

        self.label_notes = Label(self.my_gui, text='Other Notes')
        self.label_notes.place(x=10, y=begin)
        self.entry_notes = Entry(self.my_gui, bd=2)
        self.entry_notes.place(x=wid, y=begin)
        self.data_entries['other_notes'] = self.entry_notes

        begin = begin + gap

        self.append_button = Button(self.my_gui, text='Append Data', width=25, command=self.append_button_pushed)
        self.append_button.place(x=10, y=begin)

        self.button_clear = Button(self.my_gui, text='Clear text', width=25, command=self.clear_button_pushed)
        self.button_clear.place(x=210, y=begin)

        self.button_close = Button(self.my_gui, text='Close', width=25, command=self.close_button_pushed)
        self.button_close.place(x=410, y=begin)





############################### RUN GUI ################################
myGUI = GUI(r'D:\GitHub\MazeClerk\data')
myGUI.run()