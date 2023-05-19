import os
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import re

def levenshtein_distance(word1, word2):
    m = len(word1)
    n = len(word2)

    # Initialize the rolling array with dimensions (m+1) x 2
    matrix = [[0] * 2 for _ in range(m + 1)]

    # Initialize the first row with values from 0 to m
    for i in range(m + 1):
        matrix[i][0] = i

    # Iterate through the characters of the second word
    for j in range(1, n + 1):
        # Swap the rows in the matrix
        matrix[0][1] = j
        for i in range(1, m + 1):
            # Calculate the minimum edit distance at each position
            if word1[i - 1] == word2[j - 1]:
                matrix[i][1] = matrix[i - 1][0]
            else:
                matrix[i][1] = min(
                    matrix[i - 1][0] + 1,      # Deletion
                    matrix[i][0] + 1,          # Insertion
                    matrix[i - 1][0] + 1       # Substitution
                )

        # Swap the columns in the matrix for the next iteration
        for i in range(m + 1):
            matrix[i][0] = matrix[i][1]

    # Return the Levenshtein distance (bottom-right cell)
    return matrix[m][0]


def calculate_metrics(ground_truth_text, corrected_text):
    ground_truth_tokens = re.findall(r'\w+', ground_truth_text)
    corrected_tokens = re.findall(r'\w+', corrected_text)

    tp = sum(token in ground_truth_tokens for token in corrected_tokens)
    fp = len(corrected_tokens) - tp
    fn = len(ground_truth_tokens) - tp

    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    f1_score = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0.0

    return precision, recall, f1_score


def choose_correct_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    correct_file_var.set(file_path)
    
    correct_file_label.configure(text=file_path)

def choose_text_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    text_file_var.set(file_path)
    
    text_file_label.configure(text = file_path)

def process_paragraphs():
    correct_file = correct_file_var.get()
    text_file = text_file_var.get()

    if not correct_file or not text_file:
        return

    vocab = {}
    with open(correct_file, 'r', encoding="UTF-8") as file:
        text = file.read()
        words = re.findall(r'\w+', text)  # Split words without punctuation
        total_words = len(words)
        for word in words:
            if word not in vocab:
                vocab[word] = 1
            else:
                vocab[word] += 1
        for word in vocab:
            vocab[word] /= total_words

    corectat_file = os.path.join(os.path.expanduser("~"), "Desktop", "corectat.txt")
    with open(corectat_file, 'w', encoding="UTF-8") as fileW:
        corrected_text = ''
        correct = ''
        ground_truth_text = ''
        with open(text_file, 'r', encoding="UTF-8") as file:
            paragraphs = file.readlines()
            num_paragraphs = len(paragraphs)
            progress_bar['maximum'] = num_paragraphs

            for index, paragraph in enumerate(paragraphs):
                tokens = re.findall(r'\w+|[^\w\s]', paragraph)

                for i in range(len(tokens)):
                    token = tokens[i]
                    if token.isalpha() and token not in vocab:
                        best_token = token
                        best_distance = float('inf')

                        # Find the best correction based on Levenshtein distance
                        for candidate in vocab:
                            distance = levenshtein_distance(token, candidate)
                            if distance < best_distance:
                                best_token = candidate
                                best_distance = distance

                        # Update the token if a better correction is found
                        if best_token != token:
                            tokens[i] = best_token

                corrected_text += ' '.join(tokens)
                ground_truth_text += paragraph
                correct += corrected_text

                fileW.write(corrected_text)
                fileW.write("\n")
                corrected_text = ''

                progress_bar['value'] = index + 1
                window.update()

        # Calculate metrics for the final result
        precision, recall, f1_score = calculate_metrics(ground_truth_text, correct)
        precision_label['text'] = f"Precision score is: {precision:.2f}"
        recall_label['text'] = f"Recall score is: {recall:.2f}"
        f1_score_label['text'] = f"F1 score is: {f1_score:.2f}"
        file_saved_label['text'] = "Textul corectat este salvat pe Desktop, fișierul corectat.txt"
        


# Create the main window
window = tk.Tk()
window.title("Text Correction")
window.configure(bg= '#2E282A')
window.resizable(False, False)

# Define a custom style for labels
custom_label1_style = ttk.Style()
custom_label1_style.configure('CustomLabel1.TLabel', foreground='#76B041', font=('Arial', 12, 'bold'))
custom_label2_style = ttk.Style()
custom_label2_style.configure('CustomLabel2.TLabel', foreground='#76B041', font=('Arial', 12, 'bold'), background = '#2E282A')

# Variables to store file paths
correct_file_var = tk.StringVar()
text_file_var = tk.StringVar()

# Label and Button for choosing the file with correct text
correct_file_label = ttk.Label(window, text="Alegeti textul corect:", width= 50, style='CustomLabel1.TLabel' )
correct_file_label.grid(row=0, column=0, sticky="w")
correct_file_button = tk.Button(window, text="Choose file", command=choose_correct_file)
correct_file_button.grid(row=0, column=1, padx=5)

# Label and Button for choosing the file with text to correct
text_file_label = ttk.Label(window, text="Alegeti textul greșit:", width = 50, style='CustomLabel1.TLabel')
text_file_label.grid(row=1, column=0, sticky="w")
text_file_button = tk.Button(window, text="Choose file", command=choose_text_file)
text_file_button.grid(row=1, column=1, padx=5)

# Button for processing paragraphs
process_button = tk.Button(window, text="Procesare", command=process_paragraphs)
process_button.grid(row=2, column=0, columnspan=2, pady=10)

# Progress Bar
progress_bar = ttk.Progressbar(window, length=200)
progress_bar.grid(row=3, column=0, columnspan=2, pady=10)

# Label for Precision score
precision_label = ttk.Label(window, text="Precision score: ", style='CustomLabel2.TLabel')
precision_label.grid(row=4, column=0, sticky="w")

# Label for Recall score
recall_label = ttk.Label(window, text="Recall score: ", style='CustomLabel2.TLabel')
recall_label.grid(row=5, column=0, sticky="w")

# Label for F1 score
f1_score_label = ttk.Label(window, text="F1 score: ", style='CustomLabel2.TLabel')
f1_score_label.grid(row=6, column=0, sticky="w")

file_saved_label = ttk.Label(window, style = 'CustomLabel2.TLabel')
file_saved_label.grid(row = 7, column=0, sticky='nsew', columnspan= 2)

window.mainloop()
