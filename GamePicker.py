from tkinter import simpledialog, messagebox
import tkinter as tk
import random
import pickle
import os

def save_data(categories):
    # Save data to file using pickle
    script_dir = os.path.dirname(__file__)
    filename = os.path.join(script_dir, "data.pkl")
    with open(filename, "wb") as file:
        pickle.dump(categories, file)


def load_data():
    # Load data from file using pickle
    script_dir = os.path.dirname(__file__)
    filename = os.path.join(script_dir, "data.pkl")
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


class Category:
    def __init__(self, name, weight=1):
        self.name = name
        self.weight = weight
        self.games = []

    def add_game(self, game):
        self.games.append(game)

    def modify_name(self, name):
        self.name = name

    def modify_weight(self, weight):
        self.weight = weight

    def delete(self, container):
        container.remove(self)


class Game:
    def __init__(self, name, weight=1):
        self.name = name
        self.weight = weight

    def modify_name(self, name):
        self.name = name

    def modify_weight(self, weight):
        self.weight = weight

    def delete(self, container):
        container.remove(self)


def weighted_choice(items):
    # Randomly select an item from a list based on weight
    total = sum(item.weight for item in items)
    r = random.uniform(0, total)
    upto = 0
    for item in items:
        if upto + item.weight >= r:
            return item
        upto += item.weight


# GUI
class App(tk.Tk):
    WEIGHT_TO_COLOR = {1: "#ff6666", 2: "orange", 3: "yellow", 4: "#bfff00", 5: "green"}

    def __init__(self):
        super().__init__()

        self.title("Game Picker")
        self.geometry("800x800")
        self.picking_game = False
        self.selected_category = None
        self.selected_item = None
        self.category_buttons = []
        self.game_buttons = []

        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(pady=20)

        self.add_category_button = tk.Button(self, text="Add Category", command=self.add_category, width=15)
        self.add_category_button.pack(pady=5)

        self.add_game_button = tk.Button(self, text="Add Game", command=self.add_game, state=tk.DISABLED, width=15)
        self.add_game_button.pack(pady=5)

        self.home_button = tk.Button(self, text="Home", command=self.home, width=15)
        self.home_button.pack(pady=5)

        self.reset_button = tk.Button(self, text="Reset", command=self.reset, width=15)
        self.reset_button.pack(pady=5)

        self.pick_button = tk.Button(self, text="Pick For Me!", command=self.pick, width=15)
        self.pick_button.pack(pady=5)

        # Category context menu (right click)
        self.category_context_menu = tk.Menu(self, tearoff=0)
        self.category_context_menu.add_command(label="Modify Name", command=lambda: self.modify_item_name(self.selected_item))
        self.category_context_menu.add_command(label="Modify Weight", command=lambda: self.modify_item_weight(self.selected_item))
        self.category_context_menu.add_separator()
        self.category_context_menu.add_command(label="Delete", command=lambda: self.delete_item(self.selected_item))

        # Game context menu (right click)
        self.game_context_menu = tk.Menu(self, tearoff=0)
        self.game_context_menu.add_command(label="Modify Name", command=lambda: self.modify_item_name(self.selected_item))
        self.game_context_menu.add_command(label="Modify Weight", command=lambda: self.modify_item_weight(self.selected_item))
        self.game_context_menu.add_separator()
        self.game_context_menu.add_command(label="Delete", command=lambda: self.delete_item(self.selected_item))

        self.categories = load_data()
        self.display(self.categories)


    def select_category(self, category):
        # Selects category and displays its games
        if not self.picking_game:
            self.picking_game = True
            self.add_game_button.config(state=tk.NORMAL)
            self.add_category_button.config(state=tk.DISABLED)
            self.selected_category = category
            self.display(self.selected_category.games)


    def display(self, type):
        # Displays categories or games in grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.category_buttons.clear()
        self.game_buttons.clear()

        for i, type_item in enumerate(type):
            font_size = self.adjust_font_size(type_item.name, "Helvetica")
            if type == self.categories:
                button = tk.Button(self.grid_frame, text=type_item.name, bg=self.WEIGHT_TO_COLOR[type_item.weight],
                                   command=lambda category=type_item: self.select_category(category), font=("Helvetica", font_size),
                                   width=15, height=2)
                button.bind("<Button-3>", lambda event, category=type_item: self.show_category_context_menu(event, category))
                self.category_buttons.append(button)

            elif type == self.selected_category.games:
                button = tk.Button(self.grid_frame, text=type_item.name, bg=self.WEIGHT_TO_COLOR[type_item.weight],
                                   command=lambda game=type_item: self.select_game(game), font=("Helvetica", font_size),
                                   width=15, height=2)
                button.bind("<Button-3>", lambda event, game=type_item: self.show_game_context_menu(event, game))
                self.game_buttons.append(button)

            button.grid(row=i//4, column=i%4, padx=10, pady=10, stick="nsew")


    def add_category(self):
        name = simpledialog.askstring("Category Name", "Enter category name:")
        weight = simpledialog.askinteger("Category Weight", "Enter category weight (1-5):", minvalue=1, maxvalue=5)
        if name and weight:
            category = Category(name, weight)
            self.categories.append(category)
            save_data(self.categories)
            self.display(self.categories)


    def add_game(self):
        category = self.selected_category
        if not category:
            messagebox.showerror("Error", "Select a category first!")
            return
        name = simpledialog.askstring("Game Name", "Enter game name:")
        weight = simpledialog.askinteger("Game Weight", "Enter game weight (1-5):", minvalue=1, maxvalue=5)
        if name and weight:
            game = Game(name, weight)
            category.add_game(game)
            save_data(self.categories)  
            self.display(self.selected_category.games)


    def pick(self):
        if not self.picking_game:
            self.pick_animation(self.category_buttons, self.categories)
        else:
            self.pick_animation(self.game_buttons, self.selected_category.games)


    def pick_animation(self, buttons, type, iteration=0, delay=70, current_button=None, button_color=None):
        if current_button:
            current_button.config(bg=button_color)

        available_buttons = [button for button in buttons if button != current_button]
        random_button = random.choice(available_buttons)
        button_color = random_button.cget("bg")
        random_button.config(bg="blue")

        if iteration < 23:
            self.after(delay, lambda: self.pick_animation(buttons, type, iteration+1, round(delay*1.1), random_button, button_color))
        else:
            random_button.config(bg=button_color)
            final_choice = weighted_choice(type)
            for button, type_item in zip(buttons, type):
                if type_item == final_choice:
                    button.config(bg="blue")
                    if type == self.categories:
                        messagebox.showinfo("Picked Category", final_choice.name)
                        self.select_category(final_choice)
                    elif type == self.selected_category.games:
                        messagebox.showinfo("Picked Game", final_choice.name)
                        self.home()
                    break


    def show_category_context_menu(self, event, category):
        self.selected_item = category
        self.category_context_menu.post(event.x_root, event.y_root)


    def show_game_context_menu(self, event, game):
        self.selected_item = game
        self.game_context_menu.post(event.x_root, event.y_root)


    def modify_item_name(self, item):
        new_name = simpledialog.askstring("Modify Name", "Enter new name:", initialvalue=item.name)
        if new_name:
            item.modify_name(new_name)
            save_data(self.categories)
            if isinstance(item, Category):
                self.display(self.categories)
            else:
                self.display(self.selected_category.games)


    def modify_item_weight(self, item):
        new_weight = simpledialog.askinteger("Modify Weight", "Enter new weight (1-5):", minvalue=1, maxvalue=5, initialvalue=item.weight)
        if new_weight:
            item.modify_weight(new_weight)
            if isinstance(item, Category):
                self.display(self.categories)
            else:
                self.display(self.selected_category.games)
            save_data(self.categories)


    def delete_item(self, item):
        if isinstance(item, Category):
            item.delete(self.categories)
            self.display(self.categories)
        else:
            item.delete(self.selected_category.games)
            self.display(self.selected_category.games)
        save_data(self.categories)


    def adjust_font_size(self, text, font):
        # Adjust font size to fit button width
        font_size = 14
        while font_size > 1:
            if self.measure_text_width(text, (font, font_size)) < 180:
                return font_size
            font_size -= 1
        return font_size


    def measure_text_width(self, text, font):
        # Create temporary canvas to measure text width
        canvas = tk.Canvas(self)
        width = canvas.bbox(canvas.create_text(0, 0, text=text, font=font, anchor='nw'))[2]
        canvas.destroy()
        return width


    def home(self):
        # Goes back to home screen
        self.picking_game = False
        self.selected_category = None
        self.add_game_button.config(state=tk.DISABLED)
        self.add_category_button.config(state=tk.NORMAL)
        self.display(self.categories)


    def reset(self):
        # Resets saved data
        answer = messagebox.askyesno("Reset", "Are you sure you want to reset?")
        if answer:
            self.categories = []
            save_data(self.categories)
            self.home()


if __name__ == "__main__":
    app = App()
    app.mainloop()