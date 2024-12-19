import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

# Global variable to store customer data
customer_data = None

# Initialize the app window
window = ctk.CTk()
window.title("Customer Segmentation Tool")
window.geometry("900x700")
window.resizable(True, True)
ctk.set_appearance_mode("dark")  # Dark theme
ctk.set_default_color_theme("blue")  # Blue accents

# Global variables for frames
welcome_frame = None
data_frame = None
result_frame = None

# Variables for clustering inputs
col1_var = tk.StringVar()
col2_var = tk.StringVar()
num_clusters_var = tk.StringVar()

# Function to show a frame
def show_frame(frame):
    frame.tkraise()

# Function to upload file and load data
def upload_file():
    global customer_data
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            customer_data = pd.read_csv(file_path)
            display_data_in_table(customer_data)  # Display data in Treeview
            column_names = customer_data.columns.tolist()
            column_dropdown['values'] = column_names
            column_dropdown_2['values'] = column_names
            show_frame(data_frame)
        except pd.errors.EmptyDataError:
            messagebox.showerror("Error", "The file is empty or not a valid CSV.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load the file: {e}")

# Function to handle null values
def handle_null_values():
    global customer_data
    if customer_data.isnull().sum().sum() > 0:
        choice = messagebox.askquestion("Handle Missing Values",
                                        "Data has missing values. Would you like to drop or fill them?")
        if choice == 'yes':
            customer_data.dropna(inplace=True)
        else:
            customer_data.fillna(customer_data.mean(), inplace=True)
        display_data_in_table(customer_data)
        messagebox.showinfo("Info", "Missing values handled successfully.")

# Function to display data in Treeview
def display_data_in_table(data):
    # Clear existing data in the table
    for col in data_table.get_children():
        data_table.delete(col)

    # Set table headers
    data_table["columns"] = list(data.columns)
    for col in data.columns:
        data_table.heading(col, text=col)
        data_table.column(col, width=120, anchor="center")

    # Insert rows into the table
    for _, row in data.iterrows():
        data_table.insert("", "end", values=list(row))

# Function to style the table
def style_table():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="gray30",
                    foreground="white",
                    rowheight=25,
                    fieldbackground="gray20")
    style.map("Treeview",
              background=[('selected', 'gray50')],
              foreground=[('selected', 'white')])

# Function to plot Elbow graph
def plot_elbow_graph():
    try:
        col1 = col1_var.get()
        col2 = col2_var.get()
        if not col1 or not col2:
            raise ValueError("Please select both columns for clustering.")
        X = customer_data[[col1, col2]].values
        wcss = []
        for i in range(1, 11):
            kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
            kmeans.fit(X)
            wcss.append(kmeans.inertia_)
        plt.figure(figsize=(8, 5))
        sns.set(style="darkgrid")
        plt.plot(range(1, 11), wcss, marker='o', color='blue', linewidth=2)
        plt.title('Elbow Point Graph for Optimal Clusters')
        plt.xlabel('Number of Clusters')
        plt.ylabel('WCSS')
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to plot Elbow graph: {e}")

# Function to perform KMeans clustering
def perform_clustering():
    try:
        num_clusters = int(num_clusters_var.get())
        col1 = col1_var.get()
        col2 = col2_var.get()
        if not col1 or not col2:
            raise ValueError("Please select both columns for clustering.")
        if num_clusters <= 0:
            raise ValueError("Number of clusters must be greater than 0.")
        X = customer_data[[col1, col2]].values
        kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=0)
        y_kmeans = kmeans.fit_predict(X)
        plt.figure(figsize=(8, 8))
        colors = ['blue', 'green', 'orange', 'purple', 'cyan', 'yellow', 'magenta']
        for i in range(num_clusters):
            plt.scatter(X[y_kmeans == i, 0], X[y_kmeans == i, 1],
                        s=70, color=colors[i % len(colors)], label=f'Cluster {i+1}')
        plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1],
                    s=200, c='red', marker='X', label='Centroids')
        plt.title('Customer Segmentation')
        plt.xlabel(col1)
        plt.ylabel(col2)
        plt.legend()
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Welcome Frame
welcome_frame = ctk.CTkFrame(window, fg_color="gray20")
welcome_frame.place(relwidth=1, relheight=1)
welcome_label = ctk.CTkLabel(welcome_frame, text="Welcome to Customer Segmentation Tool",
                             font=("Arial", 32, "bold"), text_color="white")
welcome_label.pack(pady=50)
upload_button = ctk.CTkButton(welcome_frame, text="Upload CSV File", command=upload_file, height=40, width=200)
upload_button.pack(pady=20)

# Data Frame
data_frame = ctk.CTkFrame(window, fg_color="gray20")
data_frame.place(relwidth=1, relheight=1)
data_label = ctk.CTkLabel(data_frame, text="Data Preview & Configuration", font=("Arial", 28, "bold"), text_color="white")
data_label.pack(pady=20)

# Data Table Frame
data_table_frame = ctk.CTkFrame(data_frame, fg_color="gray30")
data_table_frame.pack(pady=10, fill="both", expand=True)
data_table = ttk.Treeview(data_table_frame, show="headings")
data_table.pack(side="left", fill="both", expand=True)
style_table()
scrollbar_y = ttk.Scrollbar(data_table_frame, orient="vertical", command=data_table.yview)
scrollbar_y.pack(side="right", fill="y")
data_table.configure(yscrollcommand=scrollbar_y.set)

handle_null_button = ctk.CTkButton(data_frame, text="Handle Null Values", command=handle_null_values, height=30)
handle_null_button.pack(pady=10)
column_label = ctk.CTkLabel(data_frame, text="Select Columns for Clustering:", text_color="white")
column_label.pack(pady=5)
column_dropdown = ttk.Combobox(data_frame, textvariable=col1_var, state="readonly")
column_dropdown.pack(pady=5)
column_dropdown_2 = ttk.Combobox(data_frame, textvariable=col2_var, state="readonly")
column_dropdown_2.pack(pady=5)
elbow_button = ctk.CTkButton(data_frame, text="Plot Elbow Graph", command=plot_elbow_graph, height=40, width=150)
elbow_button.pack(pady=20)
next_button = ctk.CTkButton(data_frame, text="Next", command=lambda: show_frame(result_frame), height=30, width=100)
next_button.pack(pady=20)

# Result Frame
result_frame = ctk.CTkFrame(window, fg_color="gray20")
result_frame.place(relwidth=1, relheight=1)
clusters_label = ctk.CTkLabel(result_frame, text="Enter Number of Clusters:", text_color="white")
clusters_label.pack(pady=10)
clusters_entry = ctk.CTkEntry(result_frame, textvariable=num_clusters_var, placeholder_text="e.g., 3")
clusters_entry.pack(pady=5)
cluster_button = ctk.CTkButton(result_frame, text="Perform Clustering", command=perform_clustering, height=40, width=200)
cluster_button.pack(pady=20)
back_button = ctk.CTkButton(result_frame, text="Back", command=lambda: show_frame(data_frame), height=30, width=100)
back_button.pack(pady=20)

# Show the welcome frame initially
show_frame(welcome_frame)

# Run the application
window.mainloop()