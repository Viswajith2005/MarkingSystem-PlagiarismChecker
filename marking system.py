import os
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set up paths
ASSIGNMENTS_FOLDER = "assignments"

# Ensure folder for assignments exists
os.makedirs(ASSIGNMENTS_FOLDER, exist_ok=True)

# Initialize CSV if it doesn't exist
if not os.path.exists("student_data.csv"):
    with open("student_data.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Roll Number", "Name", "Class", "Assignment File", "Marks", "Plagiarism"])

# Function to register a student
def register_student():
    name = input("Enter student name: ").strip()
    roll_number = input("Enter roll number: ").strip()
    student_class = input("Enter class: ").strip()

    # Check if the student already exists
    student_exists = False
    with open("student_data.csv", mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 3 and row[0] == roll_number and row[2] == student_class:
                student_exists = True
                break

    if student_exists:
        print("Student is already registered with this roll number in the same class.")
    else:
        with open("student_data.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([roll_number, name, student_class, "", "", ""])
        print(f"Student {name} registered successfully.")

# Function to upload assignment and check plagiarism
def upload_assignment():
    student_class = input("Enter class: ").strip()
    roll_number = input("Enter roll number: ").strip()

    # Check if the student exists
    student_exists = False
    with open("student_data.csv", mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 3 and row[0] == roll_number and row[2] == student_class:
                student_exists = True
                break

    if not student_exists:
        print("Student does not exist. Please upload the assignment of an existing student.")
        return

    file_path = input("Enter path to the assignment (.txt file): ").strip()
    if not os.path.exists(file_path) or not file_path.endswith('.txt'):
        print("Invalid file path or format. Please ensure it's a .txt file.")
        return

    folder_path = input("Enter the path of the folder to compare with: ").strip()
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("Invalid folder path.")
        return

    print("Assignment uploaded successfully.")
    highest_plagiarism = check_plagiarism(file_path, folder_path)

    # Auto-assign marks based on the highest plagiarism percentage
    auto_marks = assign_auto_marks(highest_plagiarism)

    # Update the student data with plagiarism information and marks
    update_plagiarism_and_marks(roll_number, highest_plagiarism, auto_marks, file_path, student_class)

# Function to check plagiarism
def check_plagiarism(new_file, folder_path):
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]
    contents = []
    
    for file in all_files:
        with open(file, 'r', encoding='utf-8') as f:
            contents.append(f.read())

    with open(new_file, 'r', encoding='utf-8') as f:
        contents.append(f.read())

    # Compute cosine similarity
    vectorizer = TfidfVectorizer().fit_transform(contents)
    similarities = cosine_similarity(vectorizer[-1], vectorizer[:-1]).flatten()

    highest_plagiarism = 0
    print("Plagiarism results:")
    for i, sim in enumerate(similarities):
        print(f"Plagiarism with {os.path.basename(all_files[i])}: {sim * 100:.2f}%")
        if sim > highest_plagiarism:
            highest_plagiarism = sim
    
    return highest_plagiarism * 100  # Return the highest plagiarism percentage

# Function to assign marks based on plagiarism percentage
def assign_auto_marks(plagiarism_percentage):
    if plagiarism_percentage < 20:
        return "100"
    elif 20 <= plagiarism_percentage < 40:
        return "80"
    elif 40 <= plagiarism_percentage < 60:
        return "60"
    elif 60 <= plagiarism_percentage < 80:
        return "40"
    elif 80 <= plagiarism_percentage <= 100:
        return "20"
    else:
        return "0"

# Function to update the plagiarism value and marks in the CSV
def update_plagiarism_and_marks(roll_number, plagiarism, marks, assignment_file, student_class):
    updated = False
    rows = []
    with open("student_data.csv", mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3 and row[0] == roll_number and row[2] == student_class:
                row[3] = assignment_file
                row[4] = marks
                row[5] = f"{plagiarism:.2f}"
                updated = True
            rows.append(row)

    if updated:
        with open("student_data.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        print(f"Plagiarism percentage updated for roll number {roll_number}: {plagiarism:.2f}%.")
        print(f"Marks for roll number {roll_number} have been auto-assigned: {marks}")
    else:
        print("Student not found.")

# Function to assign or update marks for a student
def assign_marks():
    student_class = input("Enter class: ").strip()
    roll_number = input("Enter roll number: ").strip()

    student_exists = False
    with open("student_data.csv", mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 3 and row[0] == roll_number and row[2] == student_class:
                student_exists = True
                break

    if not student_exists:
        print("Student does not exist. Please assign marks for an existing student.")
        return

    marks = input("Enter marks to assign (this will replace existing marks): ").strip()

    updated = False
    rows = []
    with open("student_data.csv", mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3 and row[0] == roll_number and row[2] == student_class:
                row[4] = marks
                updated = True
            rows.append(row)

    if updated:
        with open("student_data.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        print(f"Marks for roll number {roll_number} have been updated successfully.")
    else:
        print("Student not found.")

# Function to retrieve student data by class and roll number
def get_student_data():
    student_class = input("Enter class: ").strip()
    roll_number = input("Enter roll number: ").strip()

    found_student = False
    with open("student_data.csv", mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 3 and row[0] == roll_number and row[2] == student_class:
                found_student = True
                print("Student Details:")
                print("Roll Number:", row[0])
                print("Name:", row[1] if row[1] else "still not assigned")
                print("Class:", row[2] if row[2] else "still not assigned")
                print("Assignment File:", row[3] if row[3] else "still not assigned")
                print("Marks:", row[4] if row[4] else "still not assigned")
                print("Plagiarism:", row[5] if row[5] else "still not assigned")
                return

    if not found_student:
        print("Student not found.")

# Main menu
def main():
    while True:
        print("\n--- Student Marking System ---")
        print("1. Register a student")
        print("2. Upload assignment and check plagiarism")
        print("3. Assign marks")
        print("4. Retrieve student data")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            register_student()
        elif choice == '2':
            upload_assignment()
        elif choice == '3':
            assign_marks()
        elif choice == '4':
            get_student_data()
        elif choice == '5':
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the program
if __name__ == "__main__":
    main()
