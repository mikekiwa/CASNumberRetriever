import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import requests
from tqdm import tqdm
from datetime import datetime

def retrieveCAS(querywords):
    merged_df = pd.DataFrame()

    # Initialize progress bar
    progress_bar["maximum"] = len(querywords)
    progress_bar["value"] = 0

    for queryword in querywords:
        base_url = 'https://rboq1qukh0.execute-api.us-east-2.amazonaws.com/default/search?q=' + queryword + '*&offset=0&size=100'
        headers = {"Content-Type": "application/json"}
        r = requests.get(base_url, headers=headers)
        count = r.json()['count']

        for i in tqdm(range(0, count, 100)):
            iter_base_url = 'https://rboq1qukh0.execute-api.us-east-2.amazonaws.com/default/search?q=' + queryword + '*&offset=' + str(i) + '&size=100'
            iter_r = requests.get(iter_base_url, headers=headers)
            current_df = pd.DataFrame(iter_r.json()['results'])
            merged_df = pd.concat([current_df, merged_df], ignore_index=True, sort=True)

        # Update the progress bar after each query word is processed
        progress_bar["value"] += 1
        root.update_idletasks()

    merged_df.rename(columns={'rn': 'CAS#', 'image': 'Image', 'name': 'Name'}, inplace=True)
    merged_df.drop(columns='Image', inplace=True)
    merged_df.sort_index(axis=1, inplace=True)

    tags_list = ['<p>', '</p>', '<p*>', '<ul>', '</ul>', '<li>', '</li>', '<br>', '<strong>', '</strong>', '<span*>',
                 '</span>', '<a href*>', '</a>', '<em>', '</em>', '<sup>', '</sup>', '<sub>', '</sub>',
                 '<span class="text-smallcaps">', '</smallcap>']

    for tag in tags_list:
        merged_df['Name'] = merged_df['Name'].replace(to_replace=tag, value=' ', regex=True)

    merged_df['Name'] = merged_df['Name'].str.upper()
    merged_df['CAS#'] = merged_df['CAS#'].str.replace('-', '')

    # Show a message box when retrieval is complete
    messagebox.showinfo("Retrieval Complete", "Data retrieval is complete.")
    
    return merged_df

def on_retrieve():
    querywords = entry_query.get().split(',')
    querywords = [word.strip() for word in querywords]  # Remove any surrounding whitespace
    if querywords:
        try:
            global result_df
            result_df = retrieveCAS(querywords)
            display_results(result_df)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Input Error", "Please enter at least one query word.")

def display_results(df):
    # Clear the previous results
    for row in tree.get_children():
        tree.delete(row)

    # Insert new results
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

def export_to_csv():
    if 'result_df' in globals():
        filename = f'result_{datetime.now().strftime("%d_%m_%Y-%I_%M_%S_%p")}.csv'
        result_df.to_csv(filename, index=False)
        messagebox.showinfo("Export Successful", f"Data exported to {filename}")
    else:
        messagebox.showwarning("Export Error", "No data to export.")

def export_to_excel():
    if 'result_df' in globals():
        filename = f'result_{datetime.now().strftime("%d_%m_%Y-%I_%M_%S_%p")}.xlsx'
        result_df.to_excel(filename, index=False)
        messagebox.showinfo("Export Successful", f"Data exported to {filename}")
    else:
        messagebox.showwarning("Export Error", "No data to export.")

# Set up the main application window
root = tk.Tk()
root.title("CAS Number Retriever")
root.geometry("800x600")  # Set the window size

# Create and place the input field
label_query = tk.Label(root, text="Enter Query Words (comma-separated):")
label_query.pack(pady=10)

entry_query = tk.Entry(root)
entry_query.pack(pady=10)

# Create and place the retrieve button
button_retrieve = tk.Button(root, text="Retrieve CAS#", command=on_retrieve)
button_retrieve.pack(pady=20)

# Create a Treeview to display results
columns = ('CAS#', 'Name')
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading('Name', text='Name')
tree.heading('CAS#', text='CAS#')
tree.pack(pady=20, fill=tk.BOTH, expand=True)

# Create and place the progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Create and place the export buttons
button_export_csv = tk.Button(root, text="Export to CSV", command=export_to_csv)
button_export_csv.pack(pady=10)

button_export_excel = tk.Button(root, text="Export to Excel", command=export_to_excel)
button_export_excel.pack(pady=10)

# Start the GUI event loop
root.mainloop()
