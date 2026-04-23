import webbrowser
import os
import tkinter as tk
from tkinter import ttk, messagebox
import json
from PIL import ImageTk, Image

from EDA import EDA
from cluster_map import generate_cluster_map


# ---------------- LOAD CATEGORIES ----------------
def load_categories(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    categories = {}
    for item in data['foursquare_venues']:
        main_category, main_id = list(item['main_category'].items())[0]
        sub_categories = item['sub_categories']

        categories[main_category] = {
            'id': main_id,
            'sub_categories': sub_categories
        }

    return categories


# ---------------- EVENT HANDLERS ----------------
def on_main_category_change(event=None):
    selected_main_category = main_category_var.get()
    sub_category_dropdown['values'] = list(
        categories[selected_main_category]['sub_categories'].keys()
    )
    sub_category_dropdown.current(0)



def show_dashboard(visuals):
    if not visuals:
        return

    dashboard = tk.Toplevel(root)
    dashboard.title("Venue Sentiment & Popularity Analytics")
    dashboard.geometry("900x600")
    
    # Title
    tk.Label(dashboard, text="NLP Analysis Results", font=("Arial", 16, "bold")).pack(pady=10)

    # Container for images
    frame = tk.Frame(dashboard)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Display images
    # We need to keep references to prevent garbage collection
    dashboard.images = []

    if "graph" in visuals:
        img_path = visuals["graph"]
        img = Image.open(img_path)
        img = img.resize((400, 300))
        photo = ImageTk.PhotoImage(img)
        dashboard.images.append(photo)
        
        lbl_frame = tk.Frame(frame)
        lbl_frame.pack(side="left", padx=10)
        tk.Label(lbl_frame, text="Sentiment Distribution", font=("Arial", 12)).pack()
        tk.Label(lbl_frame, image=photo).pack()

    if "wordcloud" in visuals:
        img_path = visuals["wordcloud"]
        img = Image.open(img_path)
        img = img.resize((400, 300))
        photo = ImageTk.PhotoImage(img)
        dashboard.images.append(photo)
        
        lbl_frame = tk.Frame(frame)
        lbl_frame.pack(side="right", padx=10)
        tk.Label(lbl_frame, text="Keyword Cloud", font=("Arial", 12)).pack()
        tk.Label(lbl_frame, image=photo).pack()

def submit_form():
    place = place_entry.get().strip()

    if not place:
        messagebox.showerror("Input Error", "Please enter a place name")
        return

    main_category = main_category_var.get()
    sub_category = sub_category_var.get()

    main_category_id = categories[main_category]['id']
    sub_category_id = categories[main_category]['sub_categories'][sub_category]

    try:
        # Generate maps
        eda_map, visuals = EDA(place=place, category_id=sub_category_id, category_name=sub_category)
        here_map = generate_cluster_map(place=place)

        if not eda_map or not here_map:
            messagebox.showerror("Error", "Maps could not be generated")
            return

        # Save maps
        eda_file = "foursquare_map.html"
        cluster_file = "cluster_map.html"

        eda_map.save(eda_file)
        here_map.save(cluster_file)

        # 🔥 OPEN MAPS & DASHBOARD
        webbrowser.open(f"file:///{os.path.abspath(eda_file)}")
        webbrowser.open(f"file:///{os.path.abspath(cluster_file)}")
        
        if visuals:
            show_dashboard(visuals)

        messagebox.showinfo(
            "Success",
            "Analysis complete! Maps and dashboard opened."
        )

        print(f"Place: {place}")
        print(f"Main Category: {main_category}")
        print(f"Sub Category: {sub_category}")
        print("Analysis generated.")

    except Exception as e:
        messagebox.showerror("Application Error", str(e))


# ---------------- MAIN UI ----------------
categories = load_categories('foursquare_venue_categories.json')

root = tk.Tk()
root.title("Exploratory Data Analysis On Geolocational Data")
root.geometry("1000x800")
root.resizable(False, False)

# Background image
bg_image = Image.open("assets/bg3.jpeg")
bg_image = bg_image.resize((1000, 800))
background_photo = ImageTk.PhotoImage(bg_image)
background_label = tk.Label(root, image=background_photo)
background_label.place(x=0, y=0)

# Place input
tk.Label(
    root,
    text="Enter Place Name:",
    fg="Black",
    font=("Times New Roman", 16, "bold")
).place(x=400, y=100)

place_entry = tk.Entry(
    root,
    width=30,
    fg="Green",
    font=("Times New Roman", 16, "bold")
)
place_entry.place(x=590, y=100)

# Main category
tk.Label(
    root,
    text="Select Main Category:",
    fg="Black",
    font=("Times New Roman", 16, "bold")
).place(x=350, y=200)

custom_font = ("Times New Roman", 15)
style = ttk.Style()
style.configure("TCombobox", foreground="#186A3B")

main_category_var = tk.StringVar()
main_category_dropdown = ttk.Combobox(
    root,
    textvariable=main_category_var,
    values=list(categories.keys()),
    state="readonly",
    width=20,
    font=custom_font
)
main_category_dropdown.place(x=580, y=200)
main_category_dropdown.bind("<<ComboboxSelected>>", on_main_category_change)
main_category_dropdown.current(0)

# Sub category
tk.Label(
    root,
    text="Select Sub Category:",
    fg="Black",
    font=("Times New Roman", 16, "bold")
).place(x=350, y=250)

sub_category_var = tk.StringVar()
sub_category_dropdown = ttk.Combobox(
    root,
    textvariable=sub_category_var,
    state="readonly",
    width=20,
    font=custom_font
)
sub_category_dropdown.place(x=580, y=250)

on_main_category_change()

# Submit button
tk.Button(
    root,
    text="Submit",
    command=submit_form,
    fg="Purple",
    font=("Times New Roman", 16, "bold")
).place(x=500, y=350)

root.mainloop()
