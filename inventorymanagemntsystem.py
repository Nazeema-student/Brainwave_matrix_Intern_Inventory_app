import tkinter as tk 
from tkinter import messagebox, ttk
import json
import os 


DATA_FILE = "inventory_data.json"
USER_FILE = "users.json"
LOW_STOCK_THRESHOLD = 5 


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.laod(file)
        
    return{}

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent = 4)


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as file:
            return json.load(file) 
        
    return{"admin": "password"} 

def save_users(users):
    with open(USER_FILE, 'w') as file:
        json.dump(users, file, indent = 4)

inventory = load_data()
users = load_users()

def authenticate(username, password):
    return users.get(username) == password 

class InventoryApp:
    def __init__(self, root):
        self.root = root 
        self.root.title("Inventory Mananagement System")

        self.login_frame = tk.Frame(root)
        self.login_frame.pack(pady = 20)

        tk.Label(self.login_frame, text = "username:").grid(row = 0, column = 0, padx = 5, pady = 5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row = 0, column = 1, padx = 5, pady = 5)

        tk.Label(self.login_frame, text = "Password:").grid(row = 1, column = 0, padx = 5, pady = 5)
        self.password_entry = tk.Entry(self.login_frame, show = "*")
        self.password_entry.grid(row = 1, column = 1, padx = 5, pady = 5) 

        tk.Button(self.login_frame, text = "Login", command = self.login).grid(row =2, column = 0, columnSpan = 2, pady = 10 ) 

        self.main_frame = tk.Frame(root) 

        self.tree = ttk.Treeview(self.main_frame, columns = ("ID", "Name", "Quantity", "Price"), show = "headings") 
        self.tree.heading("ID", text = "ID")
        self.tree.heading("Name",text = "Name")
        self.tree.heading("Quantity", text = "Quantity")
        self.tree.heading("Price", text = "Price")
        self.tree.pack(pady = 10) 

        tk.Button(self.main_frame, text = "Add Product", comamnd = self.add_product).pack(pady = 5)
        tk.Button(self.main_frame, text = "Edit Product", command = self.edit_product).pack(pady = 5)
        tk.Button(self.main_frame, text = "Delete Product", command = self.delete_product).pack(pady = 5)
        tk.Button(self.main_frame, text = "Generate Report", command = self.genrate_report).pack(pady = 5)

        self.load_inventory()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get() 

        if authenticate(username, password):
            self.login_frame.pack_forget()
            self.main_frame.pack(pady = 20)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def load_inventory(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for product_id, product in inventory.items():
            self.tree.insert("", "end", values = (product_id, product['name'], product['quantity'], product['price']))

    def add_product(self):
        self.open_product_window("Add Product")

    def edit_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No product selected")
            return 
        product_id = self.tree.item(selected_item, "values")[0] 
        self.open_product_window("Edit product", product_id)

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("warning", "No product selected")
            return 

        product_id = self.tree.item(selected_item, "values")[0] 
        confirm = messagebox.askyesno("confirm", f"Are you sure you want to delete product{product_id}?")

        if confirm:
            del inventory[product_id]
            save_data(inventory)
            self.load_inventory()

    def open_product_window(self, title, product_id = None):
        window = tk.Toplevel(self.root)
        window.title(title) 

        tk.Label(window, text = "productId:").grid(row= 0, column = 0, padx = 5, pady = 5)
        id_entry = tk.Entry(window)
        id_entry.grid(row = 0, column = 1, padx = 5, pady = 5)

        tk.Label(window, text = "Name:").grid(row = 1, column = 0, padx = 5, pady = 5) 
        name_entry = tk.Entry(window)
        name_entry.grid(row = 1, column = 1, padx = 5, pady = 5)  

        tk.Label(window, text = "Quantity:").grid(row = 2, column = 0, padx = 5, pady = 5)
        quantity_entry = tk.Entry(window)
        quantity_entry.grid(row = 2, column = 1, padx = 5, pady = 5)

        tk.Label(window, text = "Price:").grid(row = 3, column = 0, padx = 5, pady = 5)
        price_entry = tk.Entry(window)
        price_entry.grid(row = 3, column = 1, padx = 5, pady = 5) 
 

        if product_id:
            product = inventory[product_id]
            id_entry.insert(0, product_id)
            id_entry.config(state = "disabled")
            name_entry.insert(0, product['name'])
            quantity_entry.insert(0, product['quantity'])
            price_entry.insert(0, product['price'])

        def save_product():
            product_id_value = id_entry.get()
            name_value = name_entry.get()
            quantity_value = quantity_entry.get()
            price_value = price_entry.get()

            if not product_id_value or not name_value or not quantity_value or not price_value:
                messagebox.showerror("Error", "all Fields are required")
                return 
            try:
                quantity_value   = int(quantity_value)
                price_value = float(price_value)

            except ValueError:
                messagebox.showerror("Error", "Quantity must be an integer and price must be a number")
                return 
            inventory[product_id_value] = {
                "name": name_value,
                "quantity": quantity_value,
                "price": price_value 
            } 
            save_data(inventory)
            self.load_inventory()
            window.destroy()

            tk.Button(window, text = "Save", command = save_product).grid(row = 4, column = 0, columnspan = 2, pady = 10)

        def generate_report(self):
            low_stock = [prod for prod in inventory.values() if prod['quantity'] <= LOW_STOCK_THRESHOLD]
            if low_stock:
                report = "Low stock products:\n" + "\n".join([f"{prod['name']}(qty: {prod['quantity']})" for prod in low_stock])
            else:
                report = "No products are low on stock."
            messagebox.showinfo("Report", report)

if __name__=="__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()                                                                    
                    