from tkinter import *
from tkinter import ttk

root = Tk()
root.title("WHITE BOARD")
root.geometry("1050x570+150+50")
root.config(bg="#f2f3f5")
root.resizable(False, False)

current_x = 0
current_y = 0
color = "black"


#icon
# image_icon = PhotoImage(file="whiteboard.png")
# root.iconphoto(False,image_icon)  


# Canvas setup
canvas = Canvas(root, width=930, height=500, background="white", cursor="hand2")
canvas.place(x=100, y=10)

# Brush thickness
current_value = DoubleVar(value=5)

def locate_xy(event):
    global current_x, current_y
    current_x = event.x
    current_y = event.y

def addline(event):
    global current_x, current_y, color
    canvas.create_line((current_x, current_y, event.x, event.y),
                       fill=color,
                       width=current_value.get(),
                       capstyle=ROUND,
                       smooth=True)
    current_x = event.x
    current_y = event.y

canvas.bind('<Button-1>', locate_xy)
canvas.bind('<B1-Motion>', addline)

# Color palette
colors = Canvas(root, bg="#fff", width=37, height=300, bd=0, highlightthickness=0)
colors.place(x=30, y=60)

def show_color(new_color):
    global color
    color = new_color

def display_pallete():
    palette_colors = ["black", "yellow", "gray", "brown4", "red", "orange", "green", "blue", "purple"]
    y = 10
    for col in palette_colors:
        rect = colors.create_rectangle((10, y, 30, y+20), fill=col, outline="")
        colors.tag_bind(rect, '<Button-1>', lambda e, col=col: show_color(col))
        y += 30

display_pallete()

# Slider
def slider_changed(event):
    value_label.config(text=f"{int(current_value.get())}")

slider = ttk.Scale(root, from_=1, to=50, orient="horizontal", command=slider_changed, variable=current_value)
slider.place(x=30, y=500)

value_label = ttk.Label(root, text=f"{int(current_value.get())}")
value_label.place(x=37, y=530)

# Eraser (just sets color to white)
def use_eraser():
    global color
    color = "white"
    
eraser_btn = Button(root, text="Eraser", command=use_eraser, bg="#f2f3f5")
eraser_btn.place(x=20, y=400)

# Clear canvas
def new_canvas():
    canvas.delete("all")
    display_pallete()

clear_btn = Button(root, text="New", command=new_canvas, bg="#f2f3f5")
clear_btn.place(x=20, y=450)

root.mainloop()
