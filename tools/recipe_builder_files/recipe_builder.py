##############################
# Set working directory
# Remove this when debugging
import os, sys
os.chdir(sys.path[0])
##os.chdir(os.path.dirname(os.path.abspath(__file__)))

##############################
# Imports
import copy
import homebrew as hb
try:
	import dill as pkl
	dill_imported = True
except ModuleNotFoundError:
	dill_imported = False
import re
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
import tkinter.ttk as ttk

##############################
# Functions
def new_recipe():
	global commands, tree, wort
	commands = []
	tree.delete(*tree.get_children())
	wort = hb.Wort()
def open_recipe():
	global commands, tree, wort
	
	if not dill_imported:
		tkmb.showerror('Package error', 'The "dill" package is needed to load recipes.\nTo enable loading, please install dill and restart the program.')
	else:
		filename = tkfd.askopenfilename(initialdir = 'saved_recipes/', title = 'Open recipe', filetypes = (('Recipe files','*.hbr'), ('All files','*.*')))
		if filename != '':
			tree.delete(*tree.get_children())
			with open(filename, 'rb') as loadfile:
				save_dict = pkl.load(loadfile)
			commands = save_dict['commands']
			for item in save_dict['tree_data']:
				tree.insert('', 'end', text = item['text'], values = item['values'])
			wort = hb.Wort()
			try:
				for command in commands:
						command['function'](wort)(**command['kwargs'])
			except:
				tkmb.showwarning('Recipe error', 'Something went wrong when loading recipe (probably related to water additions).')
def save_recipe():
	global commands, tree
	
	if not dill_imported:
		tkmb.showerror('Package error', 'The "dill" package is needed to save recipes.\nTo enable saving, please install dill and restart the program.')
	else:
		tree_data = [tree.item(child) for child in tree.get_children()]
		save_dict = {'commands': commands, 'tree_data': tree_data}
		
		filename = tkfd.asksaveasfilename(initialdir = 'saved_recipes/', title = 'Save recipe', filetypes = (('Recipe files','*.hbr'), ('All files','*.*')))
		if filename != '':
			if not re.search('.hbr$', filename): filename += '.hbr'
			with open(filename, 'wb') as savefile:
				pkl.dump(save_dict, savefile)
def delete_entry():
	global commands, tree, wort
	
	selection = tree.selection()
	
	if len(selection) > 0:
		index = tree.index(selection[0])
		
		# Test that new list of commands will run, otherwise revert to copy
		commands_copy = copy.deepcopy(commands)
		wort_copy = copy.deepcopy(wort)	
		try:
			commands.pop(index)
			wort = hb.Wort()
			for command in commands:
				command['function'](wort)(**command['kwargs'])
			tree.delete(selection[0])
			
			# Fix indices
			children = tree.get_children()
			for fix_index in range(index, len(children)):
				tree.item(children[fix_index], text = str(tree.index(children[fix_index]) + 1))
		except:
			tkmb.showwarning('Recipe error', 'Something went wrong (probably related to water additions).\nChange your selection and try again.')
			commands = commands_copy
			wort = wort_copy
def clear_selection():
	global tree
	
	tree.selection_remove(tree.selection()[0])
def add_water():
	global commands, wort
	
	# Functions
	def submit():
		global commands, wort
		
		volume = entry.get()
		try:
			volume = float(volume)
			
			if volume < 0: raise ValueError
#			if volume % 1 == 0: volume = int(volume)
			
			valid_input = True
		except ValueError:
			tkmb.showwarning('Input error', 'Volume must be a positive number.')
			
			valid_input = False
		
		if valid_input:
			selection = tree.selection()
			if len(selection) > 0:
				index = tree.index(selection[0])
				
				# Make sure new command chain will successfully execute, return to old value if not
				commands_copy = copy.deepcopy(commands)
				wort_copy = copy.deepcopy(wort)
				
				try:
					commands.insert(index, {'function': lambda wort: wort.add_water, 'kwargs': {'volume': volume}})
					wort = hb.Wort()
					for command in commands:
						command['function'](wort)(**command['kwargs'])
					tree.insert('', index, text = index + 1, values = ('Added %.2f gal water' % volume, None))
					children = tree.get_children()
					for fix_index in range(index, len(children)):
						tree.item(children[fix_index], text = str(tree.index(children[fix_index]) + 1))
				except:
					tkmb.showwarning('Recipe error', 'Something went wrong (probably related to water additions).\nChange your selection and try again.')
					commands = commands_copy
					wort = wort_copy
			else:
				wort.add_water(volume)
				commands.append({'function': lambda wort: wort.add_water, 'kwargs': {'volume': volume}})
				tree.insert('', 'end', text = len(tree.get_children()) + 1, values = ('Added %.2f gal water' % volume, None))
			
			dialog.destroy()
	
	#Prompt for inputs
	dialog = tk.Toplevel(root)
	
	dialog.title('Add water')
	
	input_text = tk.Label(dialog, text = 'Gallons of water\nto add:')
	input_text.grid(row = 0, column = 0)
	
	entry = tk.Entry(dialog)
	entry.grid(row = 0, column = 1)
	
	ok_button = tk.Button(dialog, text = 'OK', command = submit)
	ok_button.grid(row = 1, column = 0)
	
	cancel_button = tk.Button(dialog, text = 'Cancel', command = dialog.destroy)
	cancel_button.grid(row = 1, column = 1)
	
	root.wait_window(dialog)

def add_malt():
	global commands, wort
	
	# Functions
	def submit():
		global commands, wort
		
		ppg = entry_ppg.get()
		weight = entry_weight.get()
		try:
			ppg = float(ppg)
			weight = float(weight)
			
			if ppg < 0 or weight < 0: raise ValueError
#			if weight % 1 == 0: weight = int(weight)
			
			valid_input = True
		except ValueError:
			tkmb.showwarning('Input error', 'PPG and weight must be positive numbers.')
			
			valid_input = False
		
		if valid_input:
			selection = tree.selection()
			if len(selection) > 0:
				index = tree.index(selection[0])
				
				# Make sure new command chain will successfully execute, return to old value if not
				commands_copy = copy.deepcopy(commands)
				wort_copy = copy.deepcopy(wort)
				
				try:
					commands.insert(index, {'function': lambda wort: wort.add_malt, 'kwargs': {'malt_additions': hb.MaltAddition(PPG = ppg, weight = weight)}})
					wort = hb.Wort()
					for command in commands:
						command['function'](wort)(**command['kwargs'])
					tree.insert('', index, text = index + 1, values = ('Added %.2f lbs of %.3f PPG malt' % (weight, ppg), None))
					children = tree.get_children()
					for fix_index in range(index, len(children)):
						tree.item(children[fix_index], text = str(tree.index(children[fix_index]) + 1))
				except:
					tkmb.showwarning('Recipe error', 'Something went wrong (probably related to water additions).\nChange your selection and try again.')
					commands = commands_copy
					wort = wort_copy
			else:
				try:
					wort.add_malt(hb.MaltAddition(PPG = ppg, weight = weight))
					commands.append({'function': lambda wort: wort.add_malt, 'kwargs': {'malt_additions': hb.MaltAddition(PPG = ppg, weight = weight)}})
				
					tree.insert('', 'end', text = len(tree.get_children()) + 1, values = ('Added %.2f lbs of %.3f PPG malt' % (weight, ppg), None))
				except ValueError:
					tkmb.showwarning('Recipe error', 'Water must be added to recipe before malt.')
			
			dialog.destroy()
	
	if wort.volume <= 0:
		tkmb.showwarning('Recipe error', 'Water must be added to recipe before malt.')
	else:
		dialog = tk.Toplevel(root)
		
		dialog.title('Add malt')
		
		input_text_ppg = tk.Label(dialog, text = 'PPG of malt addition:')
		input_text_ppg.grid(row = 0, column = 0)
		
		entry_ppg = tk.Entry(dialog)
		entry_ppg.grid(row = 0, column = 1)
		
		input_text_weight = tk.Label(dialog, text = 'Weight of malt addition (lbs):')
		input_text_weight.grid(row = 1, column = 0)
		
		entry_weight = tk.Entry(dialog)
		entry_weight.grid(row = 1, column = 1)
		
		ok_button = tk.Button(dialog, text = 'OK', command = submit)
		ok_button.grid(row = 2, column = 0)
		
		cancel_button = tk.Button(dialog, text = 'Cancel', command = dialog.destroy)
		cancel_button.grid(row = 2, column = 1)
		
		root.wait_window(dialog)
	
def add_hops():
	global commands, wort
	
	# Functions
	def submit():
		global commands, wort
		
		aau = entry_aau.get()
		weight = entry_weight.get()
		time = entry_time.get()
		try:
			aau = float(aau)
			weight = float(weight)
			time = float(time)
			
			if aau < 0 or weight < 0 or time < 0: raise ValueError
#			if weight % 1 == 0: weight = int(weight)
			
			valid_input = True
		except ValueError:
			tkmb.showwarning('Input error', 'PPG and weight must be positive numbers.')
			
			valid_input = False
		
		if valid_input:
			selection = tree.selection()
			if len(selection) > 0:
				index = tree.index(selection[0])
				
				# Make sure new command chain will successfully execute, return to old value if not
				commands_copy = copy.deepcopy(commands)
				wort_copy = copy.deepcopy(wort)
				
				try:
					commands.insert(index, {'function': lambda wort: wort.add_hops, 'kwargs': {'hop_additions': hb.HopAddition(AAU = aau, weight = weight, time = time)}})
					wort = hb.Wort()
					for command in commands:
						command['function'](wort)(**command['kwargs'])
					tree.insert('', index, text = index + 1, values = ('Added %.2f oz of %.2f%% AAU hops (%.1f min)' % (weight, aau, time), None))
					children = tree.get_children()
					for fix_index in range(index, len(children)):
						tree.item(children[fix_index], text = str(tree.index(children[fix_index]) + 1))
				except:
					tkmb.showwarning('Recipe error', 'Something went wrong (probably related to water additions).\nChange your selection and try again.')
					commands = commands_copy
					wort = wort_copy
			else:
				try:
					wort.add_hops(hb.HopAddition(AAU = aau, weight = weight, time = time))
					commands.append({'function': lambda wort: wort.add_hops, 'kwargs': {'hop_additions': hb.HopAddition(AAU = aau, weight = weight, time = time)}})
				
					tree.insert('', 'end', text = len(tree.get_children()) + 1, values = ('Added %.2f oz of %.2f%% AAU hops (%.1f min)' % (weight, aau, time), None))
				except ValueError:
					tkmb.showwarning('Recipe error', 'Water must be added to recipe before hops.')
			
			dialog.destroy()
	
	if wort.volume <= 0:
		tkmb.showwarning('Recipe error', 'Water must be added to recipe before hops.')
	else:
		dialog = tk.Toplevel(root)
		
		dialog.title('Add hops')
		
		input_text_aau = tk.Label(dialog, text = 'AAU of hop addition (%):')
		input_text_aau.grid(row = 0, column = 0)
		
		entry_aau = tk.Entry(dialog)
		entry_aau.grid(row = 0, column = 1)
		
		input_text_weight = tk.Label(dialog, text = 'Weight of hop addition (oz):')
		input_text_weight.grid(row = 1, column = 0)
		
		entry_weight = tk.Entry(dialog)
		entry_weight.grid(row = 1, column = 1)
		
		input_text_time = tk.Label(dialog, text = 'Duration of boil (min):')
		input_text_time.grid(row = 2, column = 0)
		
		entry_time = tk.Entry(dialog)
		entry_time.grid(row = 2, column = 1)
		
		ok_button = tk.Button(dialog, text = 'OK', command = submit)
		ok_button.grid(row = 3, column = 0)
		
		cancel_button = tk.Button(dialog, text = 'Cancel', command = dialog.destroy)
		cancel_button.grid(row = 3, column = 1)
		
		root.wait_window(dialog)
def ferment():
	def submit():
		OG_override = entry_og.get()
		attenuation = entry_attenuation.get()
		FG_override = entry_fg.get()
		
		valid_input = True
		
		try:
			if OG_override == '':
				OG = None
			else:
				OG = float(OG_override)
				if OG < 0: raise ValueError
		except ValueError:
			tkmb.showwarning('Input error', 'OG override must be either blank or a number greater than zero.')
			valid_input = False
			
		try:
			if attenuation == '':
				attenuation = None
			else:
				attenuation = float(attenuation)
				if attenuation < 0 or attenuation > 1: raise ValueError
		except ValueError:
			tkmb.showwarning('Input error', 'Attenuation must be either blank or a number between zero and one.')
			valid_input = False
			
		try:
			if FG_override == '':
				FG = None
			else:
				FG = float(FG_override)
				if FG < 0: raise ValueError
		except ValueError:
			tkmb.showwarning('Input error', 'FG override must be either blank or a number between zero and one.')
			valid_input = False
			
		if attenuation == None and FG == None:
			tkmb.showwarning('Input error', 'Either attenuation or FG override must be specified.')
			valid_input = False
		
		if valid_input:
			dialog.destroy()
			
			# Derive results
			beer = hb.Beer(wort, OG = OG)
			abv = beer.calculate_abv(attenuation = attenuation, FG = FG)
			
			if FG == None:
				FG = (beer.OG - 1) * (1 - attenuation) + 1
			else:
				attenuation = 1 - (FG - 1) / (beer.OG - 1)
			
			# Package in a new dialog
			results_dialog = tk.Toplevel(root)
			results_dialog.title('Fermentation results')
			
			tk.Label(results_dialog, text = 'OG: %.3f' % beer.OG).grid(row = 0, column = 0)
			tk.Label(results_dialog, text = 'FG: %.3f' % FG).grid(row = 1, column = 0)
			tk.Label(results_dialog, text = 'Attenuation: %.2f' % attenuation).grid(row = 2, column = 0)
			tk.Label(results_dialog, text = 'IBU: %.1f' % beer.ibu).grid(row = 3, column = 0)
			tk.Label(results_dialog, text = 'ABV: %.2f%%' % abv).grid(row = 4, column = 0)
			
			tk.Button(results_dialog, text = 'OK', command = results_dialog.destroy).grid(row = 5, column = 0)
	
	if wort.volume <= 0:
		tkmb.showwarning('Recipe error', 'Water must be added to recipe before fermentation.')
	else:
		dialog = tk.Toplevel(root)
		dialog.title('Fermentation options')
		
		input_text_og = tk.Label(dialog, text = 'OG override:')
		input_text_og.grid(row = 0, column = 0)
		
		entry_og = tk.Entry(dialog)
		entry_og.grid(row = 0, column = 1)
		
		input_text_attenuation = tk.Label(dialog, text = 'Attenuation:')
		input_text_attenuation.grid(row = 1, column = 0)
		
		entry_attenuation = tk.Entry(dialog)
		entry_attenuation.insert(0, '0.75')
		entry_attenuation.grid(row = 1, column = 1)
		
		input_text_fg = tk.Label(dialog, text = 'FG override:')
		input_text_fg.grid(row = 2, column = 0)
		
		entry_fg = tk.Entry(dialog)
		entry_fg.grid(row = 2, column = 1)
		
		ok_button = tk.Button(dialog, text = 'OK', command = submit)
		ok_button.grid(row = 3, column = 0)
		
		cancel_button = tk.Button(dialog, text = 'Cancel', command = dialog.destroy)
		cancel_button.grid(row = 3, column = 1)
	
##############################
# Set up root window
root = tk.Tk()

##############################
# Create buttons
button_width = 90
num_buttons = 9
# Load images
photo_new = tk.PhotoImage(file = 'images/new.png')
photo_open = tk.PhotoImage(file = 'images/open.png')
photo_save = tk.PhotoImage(file = 'images/save.png')
photo_delete = tk.PhotoImage(file = 'images/delete.png')
photo_clear = tk.PhotoImage(file = 'images/clear.png')
photo_water = tk.PhotoImage(file = 'images/water.png')
photo_malt = tk.PhotoImage(file = 'images/malt.png')
photo_hops = tk.PhotoImage(file = 'images/hops.png')
photo_ferment = tk.PhotoImage(file = 'images/ferment.png')

# Make buttons
button_new = tk.Button(root, image = photo_new, text = 'New recipe', compound = tk.TOP, command = new_recipe, width = button_width)
button_open = tk.Button(root, image = photo_open, text = 'Open', compound = tk.TOP, command = open_recipe, width = button_width)
button_save = tk.Button(root, image = photo_save, text = 'Save', compound = tk.TOP, command = save_recipe, width = button_width)
button_delete = tk.Button(root, image = photo_delete, text = 'Delete entry', compound = tk.TOP, command = delete_entry, width = button_width)
button_clear = tk.Button(root, image = photo_clear, text = 'Clear selection', compound = tk.TOP, command = clear_selection, width = button_width)
button_water = tk.Button(root, image = photo_water, text = 'Add water', compound = tk.TOP, command = add_water, width = button_width)
button_malt = tk.Button(root, image = photo_malt, text = 'Add malt', compound = tk.TOP, command = add_malt, width = button_width)
button_hops = tk.Button(root, image = photo_hops, text = 'Add hops', compound = tk.TOP, command = add_hops, width = button_width)
button_ferment = tk.Button(root, image = photo_ferment, text = 'Ferment', compound = tk.TOP, command = ferment, width = button_width)

##############################
# Create list of actions
tree = ttk.Treeview(root, columns = ('Action'), height = 25)
tree.heading('#0', text = 'Step')
tree.heading('#1', text = 'Action')
tree.column('#0', width = 50, stretch = tk.YES)
tree.column('#1', width = button_width * num_buttons - 50, stretch = tk.YES)

##############################
# Arrange elements
button_new.grid(row = 0, column = 0)
button_open.grid(row = 0, column = 1)
button_save.grid(row = 0, column = 2)
button_delete.grid(row = 0, column = 3)
button_clear.grid(row = 0, column = 4)
button_water.grid(row = 0, column = 5)
button_malt.grid(row = 0, column = 6)
button_hops.grid(row = 0, column = 7)
button_ferment.grid(row = 0, column = 8)

tree.grid(row = 1, columnspan = num_buttons)

##############################
# Set root window dimensions/values
root.title('Homebrew Recipe Builder')
#root.minsize(0, 500)
root.resizable(width = False, height = False)

#root.minsize(button_width * (num_buttons + 1), 500)
#root.maxsize(button_width * (num_buttons + 1), 500)

##############################
# Run program
commands = []
wort = hb.Wort()

root.mainloop()

##############################
