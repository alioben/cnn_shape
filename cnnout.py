from ast import literal_eval
import readline 
import rlcompleter
import json
import os, glob 
import sys, StringIO
import subprocess as sp

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

history_file = '.cnnouthistory'
readline.parse_and_bind('tab: complete') 
readline.set_completer(complete)
try: 
    readline.read_history_file(history_file) 
except IOError: 
    pass

def get_shape(W,K,S,P,deconv=False):
	return (W-K+2*P)/S+1 if(deconv==False) else S*(W-1)+K

def get_def(args,i,default):
	if default == None and len(args) <= i:
		raise Exception("Missing argument.")
	return default if(len(args) <= i) else args[i]

def get_tuple(string):
	return literal_eval(string)

layers = []
# Prints the network built so far
def p(args):
	global layers
	input_shape = None
	print "%-5s%-12s\t%-12s"%("#", "layer type", "output shape")
	print "----------------------------------------"
	for i, layer in enumerate(layers):
		if input_shape == None:
			if layer['type'] != "input":
				raise Exception("First layer must be an input layer.")
			input_shape = layer['input_shape'] 
		elif layer['type'] == 'conv' or layer['type'] == 'pool' or layer['type'] == 'deconv':
			h,w,d = input_shape
			d = d if(layer['type'] != 'conv') else layer['num_output']
			if layer['padding'] == 'valid':
				input_shape = [get_shape(h,layer['filter'][0],layer['stride'][0],0,deconv=(layer['type'] == 'deconv')),
						   get_shape(w,layer['filter'][1],layer['stride'][1],0,deconv=(layer['type'] == 'deconv')),
						   d]
			else:
				input_shape = [h,w,d]
			h,w,d = input_shape
		elif layer['type'] == 'flatten':
			dim = 1
			for a in input_shape:
				dim *= a
			input_shape = [1, dim]
		elif layer['type'] == 'dense':
			input_shape = [1, layer['num_output']]
		print "%-5d%-12s\t%-12s"%(i, layer['type'], input_shape)

def s(args):
	global layers
	with open(args[0], 'w') as outfile:
		json.dump(layers, outfile)

def l(args):
	global layers
	with open(args[0]) as data_file:    
		layers = json.load(data_file)

def d(args):
	del layers[int(args[0])]

# Print the help for a function
def h(args):
	helps = {'a': 'Add one of the following using the command\n\ta <name_layer> [options]',
			 'p': 'Print the network built so far\n\tp',
			 's': 'Save the network in a file\n\ts <output_file>',
			 'd': 'Delete a layer from the network\n\td <layer_index>',
			 'c': 'Clear the console\n\tc',
			 'ls': 'List all the files satisfying the pattern.\n\tls [pattern]'}
	if len(args) == 0:
		args = helps.keys()
	for command in args:
		print helps[command]

# Add a layer to the cnn
def a(args):
	layer = {"type":get_def(args,0,None)}
	if args[0] == "input":
		layer['input_shape'] = get_tuple(get_def(args,1,None))
	elif args[0] == "conv":
		layer['num_output'] = int(get_def(args,1,None))
		layer['filter'] = get_tuple(get_def(args,2,'[2,2]'))
		layer['stride'] = get_tuple(get_def(args,3,'[1,1]'))
		layer['padding'] = get_def(args,4,'same')
	elif args[0] == "pool":
		layer['filter'] = get_tuple(get_def(args,1,'[2,2]'))
		layer['stride'] = get_tuple(get_def(args,2,'[2,2]'))
		layer['padding'] = get_def(args,3,'valid')
	elif args[0] == "drop":
		layer["drop_ratio"] = float(get_def(args,1,0.3))
	elif args[0] == "flatten":
		pass
	elif args[0] == "dense":
		layer['num_output'] = int(get_def(args,1,None))
	elif args[0] == "deconv":
		layer['num_output'] = int(get_def(args,1,None))
		layer['filter'] = get_tuple(get_def(args,2,'[2,2]'))
		layer['stride'] = get_tuple(get_def(args,3,'[2,2]'))
		layer['padding'] = get_def(args,4,'valid')
	else:
		print "No layer found named", layer['type']
		return
	layers.append(layer)
	p([])

def q(args):
	exit()

def c(args):
	sp.call('clear',shell=True)

def ls(args):
	text = "" if(len(args) == 0) else args[0]
	for i, a in enumerate(glob.glob(text+'*')):
		if i%3 == 0 and i > 0:
			print
		print a+"\t",
	print

def cl(args):
	global layers
	layers = []

def m(args):
	global layers
	i = int(args[0])
	for k in layers[i]:
		res = raw_input("\t"+k+"("+str(layers[i][k])+"): ")
		if res != "":
			if type(layers[i][k]) == unicode or type(layers[i][k]) == str:
				layers[i][k] = res
			else:
				layers[i][k] = literal_eval(res)

# Command  prompt
h([])
while True:
	input = raw_input("> ").split(" ")
	readline.write_history_file(history_file)
	if len(input) == 0:
		continue
	command, args = input[0], []
	if len(input) > 1:
		args = input[1:]
	try:
		to_print = eval(command)(args)
	except NameError:
		print "No function named '"+command+"' exists."
	except Exception as e:
		print "The following error occured:"
		print e
