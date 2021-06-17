from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import functions
from Bio.Seq import Seq
from tkinter import ttk
from ttkthemes import ThemedTk

# MAIN FRAME
window = ThemedTk(theme="adapta")

window.title("PCR simulator")
window.configure(background="#fafbfc")
window.iconphoto(False, PhotoImage(file='otter_icon.png'))

########## ########## ########## ########## ########## ########## ########## ########## ########## ##########

# input variables
input_sequence = ""
input_primers = []

#
checkbox_values = [[],[]]
products = []

########## ########## ########## ########## ########## ########## ########## ########## ########## ##########

# add primers to globally saved list of primers
def use_primer():
    global input_primers, checkbox_values
    used_primers = [[],[]]
    k = 0
    for i in checkbox_values[0]:
        if i.get():
            used_primers[0].append(input_primers[k])
        k += 1
    k = 0
    for i in checkbox_values[1]:
        if i.get():
            used_primers[1].append(input_primers[k])
        k += 1
    return(used_primers)

# submit button functions
def click_sequence():
    global input_sequence
    entered_text=textentry1.get(1.0, END)
    #output_sequence.delete(0.0, END)
    #output_sequence.insert(END, entered_text)
    input_sequence = functions.read_sequence(entered_text)
    canvas.delete("seq_length")
    canvas.create_text(
    1000,50, # (identical offset to 0 : 980,50) , for long seqs overlap with line
    fill="black",
    font="none 10 italic",
    text=len(input_sequence),
    tags = "seq_length")
def read_sequence_file():
    global input_sequence
    tf = filedialog.askopenfilename(
        title="Open FASTA file", 
        filetypes=(("FASTA Files", "*.fasta"),)
        )
    data = functions.parse_fasta(tf)[0][1]
    input_sequence = functions.read_sequence(data)
    textentry1.delete(1.0, END)
    textentry1.insert(1.0, input_sequence)
    canvas.delete("seq_length")
    canvas.create_text(
    1000,50,
    fill="black",
    font="none 10 italic",
    text=len(input_sequence),
    tags = "seq_length")
def read_primer_file():
    tf = filedialog.askopenfilename(
        title="Open FASTA file", 
        filetypes=(("FASTA Files", "*.fasta"),)
        )
    data = functions.parse_fasta(tf)
    primers = ""
    for i in data:
        primers += (i[1] + ", ")
    if textentry2.get("1.0", END) != "\n": # empty field
        primers = ", " + primers
    textentry2.insert(END, primers[:-2]) #  remove last char: is one , to much
    click_primers()

def click_primers():
    global input_primers, checkbox_values
    entered_text=textentry2.get(1.0,END)
    input_primers = functions.read_primers(entered_text)
    checkbox_values = [[],[]]
    delete()
    list_primers(input_primers)
def click_covid():
    global input_primers, checkbox_values
    covid_primers = "ACCTACTGTCTTATT, ACCTACTGTCTTATT, TCATTTGAGTTATAGTAG, TTAGATGAACCTGTT, GTGTTGTCTGTAGTAAT, TCTCCTAAGAAGCT, TCTTGTAGATCTGTTC, TGATAGTGTTACAGTG, GTACAACATTTACTTATG, TTCAGTGTGTAGACTT, TAATTAGAGGTGATGA, TGGATTTGTCTTCT"
    if textentry2.get("1.0", END) != "\n": # empty field
        covid_primers = ", " + covid_primers
    textentry2.insert(END, covid_primers)
    input_primers = functions.read_primers(covid_primers)
    checkbox_values = [[],[]]
    delete()
    list_primers(input_primers)

def calculate_aligns(seq, prim, max_ham):
    Bars = functions.align_hamming(seq, prim, max_ham)
    return Bars

# find primer positions and add them to chart: forward primers: f=true, else reverse primers
def add_Bars(seq, prim, max_ham, f):
    if f:
        fill_color = "#4DA6FF"
        outline_color = "#0080FF"
        tag_name = "blueBar"
    else:
        fill_color = "#57DA3D"
        outline_color = "#46AC31"
        tag_name = "greenBar"
        prim = functions.build_rerverse_primers(prim)

    canvas.delete(tag_name)
    Bars = calculate_aligns(seq, prim, max_ham)
    for i in Bars:
        start = i[0]*(940/len(input_sequence)) + 30 # adjust position according to length of sequence and given space
        end = i[1]*(940/len(input_sequence)) + 30
        canvas.create_rectangle(
            start, 45, end, 55,
            outline = outline_color,
            fill = fill_color,
            tags = tag_name)  
    return Bars

# add chimerism model 1 to chart
def add_chimerism_model_1():
    global input_sequence, products
    chimerisms = functions.chimera_model_1(products)
    canvas.delete("c1")
    for i in chimerisms:
        start = i[0]*(940/len(input_sequence)) + 30 # adjust position according to length of sequence and given space
        end = i[1]*(940/len(input_sequence)) + 30
        canvas.create_rectangle(
            start, 45, end, 55,
            outline = "red",
            tag = "c1")

# calculate function
def calc():
    global input_sequence, products
    primers = use_primer()
    hamnum = ham_num.get()
    if len(input_sequence) == 0 or len(primers) == 0:
        print("You have to submit a sequence and at least 1 primer")
    else:
        forward = add_Bars(input_sequence, primers[0], hamnum, True)   #forward
        reverse = add_Bars(input_sequence, primers[1], hamnum, False)  #reverse
    
    products = primer_products(forward, reverse)
    product_sequences = get_product_sequences(products)
    g = 0
    product_output.delete(1.0, END)
    for i in product_sequences:
        product_output.insert("end", "> " + str(g))
        g = g + 1
        product_output.insert("end", "\n")
        product_output.insert("end", i)
        product_output.insert("end", "\n")
    
def get_product_sequences(products):
    global input_sequence
    subsequences  = []
    for i in products:
        subsequences.append(input_sequence[i[0][0]:i[1][1]])
    return(subsequences)

# delete primers
def delete():
    checkboxframe0.delete(1.0,"end")
    checkboxframe1.delete(1.0,"end")

# primers check boxes
def list_primers(primers):
    global checkboxes, checkbox_values
    checkboxes0 = [IntVar()] * len(primers)
    checkboxes1 = [IntVar()] * len(primers)
    k=0
    for i in primers:
        var0 = IntVar(value=1)
        var1 = IntVar(value=1)
        checkbox_values[0].append(var0)
        checkbox_values[1].append(var1)
        box0 = ttk.Checkbutton(window, text=i, variable=var0)
        i_seq = Seq(i)
        i_seq = str(i_seq.reverse_complement())
        box1 = ttk.Checkbutton(window, text=i_seq, variable=var1)
        checkboxframe0.window_create("end", window = box0)
        checkboxframe0.insert("end", "\n")
        checkboxframe1.window_create("end", window = box1)
        checkboxframe1.insert("end", "\n")
        k += 1

# primer products
def primer_products(forward, reverse):
    products = []
    
    for i in forward:
        for j in reverse:
            if i[1] < j[0]:
                products.append([i,j])                           

    return (products)   # form: [[f_start,fw_end],[rv_s,rv_e]],...

# clear input fields
def clears():
    textentry1.delete(1.0,"end")
def clearp():
    textentry2.delete(1.0,"end")
    checkboxframe0.delete(1.0,"end")
    checkboxframe1.delete(1.0,"end")

########## ########## ########## ########## ########## ########## ########## ########## ########## ##########

# visual representation
    
# text 1: sequence
ttk.Label(window, text="RNA sequence:", font="none 12 bold").grid(row=1, column=0, sticky=W)
# text input 1
textentry1 = ScrolledText(window, width=80, height=5)
textentry1.grid(row=2, column=0, columnspan=3, sticky=W)
    
# text 2: primers
ttk.Label(window, text="primers: (primer1, primer2, ...)", font="none 12 bold").grid(row=3, column=0, sticky=W)
# text input 2
textentry2 = ScrolledText(window, width=80, height=3)
textentry2.grid(row=4, column=0, columnspan=4, sticky=W)

# Buttons 
buttoncol = 3
ttk.Button(window, text="clear", width=15, command=clears).grid(row=2, column=buttoncol-1)
ttk.Button(window, text="submit sequence", width=15, command=click_sequence).grid(row=2, column=buttoncol)
ttk.Button(window, text="load file", width=15, command=read_sequence_file).grid(row=2, column=buttoncol+1)

ttk.Button(window, text="clear", width=15, command=clearp).grid(row=4, column=buttoncol-1)
ttk.Button(window, text="submit primers", width=15, command=click_primers).grid(row=4, column=buttoncol)
ttk.Button(window, text="load file", width=15, command=read_primer_file).grid(row=4, column=buttoncol+1)
ttk.Button(window, text="use covid primers", width=15, command=click_covid).grid(row=4, column=buttoncol+2)
    
# checkbox buttons for primers
ttk.Label(window, text="forward primers:", font="none 12 bold", foreground="#0080FF").grid(row=5, column=0, sticky=W)
ttk.Label(window, text="reverse primers:", font="none 12 bold", foreground="#46AC31").grid(row=5, column=1, sticky=W)

checkboxframe0 = ScrolledText(window, width = 40, height = 10)
checkboxframe0.grid(row=6,column=0, sticky=W)

checkboxframe1 = ScrolledText(window, width = 40, height = 10)
checkboxframe1.grid(row=6,column=1, sticky=W)

#primer product output
ttk.Label(window, text="primer products:", font="none 12 bold").grid(row=12, column=0, sticky=W)
product_output = ScrolledText(window, width=200, height=10)
product_output.grid(row=13, column=0, columnspan=7, sticky=W)

# define number of mismatches
ttk.Label(window, text="Number of allowed mismatches:", font="none 12 bold").grid(row=7, column=0, sticky=W)
ham_num = Scale(window, from_=0, to=5, orient=HORIZONTAL, length=240,background="#fafbfc", troughcolor="#1ee9b7",sliderlength=40)
ham_num.grid(row=8,column=0, sticky="W")

ttk.Button(window, text="calculate", width=15, command=calc).grid(row=9, column=1)
ttk.Button(window, text="Chimerism 1", width=15, command=add_chimerism_model_1).grid(row=9, column=2)

# set up canvas
canvas = Canvas(window, width=1030, height=100, background="#fafbfc") # used to be 1000, added with to make space for number
# 0 mark
canvas.create_text(
    20,50,
    fill="black",
    font="none 10 italic",
    text="0")
# axis
line = canvas.create_line(30,50,970,50) #(x1,y1, ..., xn, yn)
# add canvas to grid
canvas.grid(row=11,column=0, columnspan=6)

########## ########## ########## ########## ########## ########## ########## ########## ########## ##########

# RUN MAIN FRAME
window.mainloop()
