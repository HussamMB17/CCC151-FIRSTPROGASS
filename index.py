import sys
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog, QWidget, QComboBox

# Constants for student fields and database files
STUDENT_FIELDS = ['Name', 'ID', 'Year Level', 'Gender', 'Program Code', 'Course']
STUDENT_DATABASE = 'students.csv'
COURSE_FIELDS = ['Course Code', 'Course Name']
COURSE_DATABASE = 'courses.csv'


def get_course_codes():
    """Retrieve course codes from the CSV file."""
    course_codes = []
    with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if row:
                course_codes.append(row[0])  # Assuming course code is the first column
    return course_codes


class StudentManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Get course codes
        self.course_codes = get_course_codes()

        self.init_ui()

    def init_ui(self):
        # Create buttons
        self.add_student_button = QPushButton("Add New Student")
        self.view_students_button = QPushButton("View Students")
        self.search_student_button = QPushButton("Search Student")
        self.update_student_button = QPushButton("Update Student")
        self.delete_student_button = QPushButton("Delete Student")
        self.add_course_button = QPushButton("Add New Course")
        self.view_courses_button = QPushButton("View Courses")
        self.search_course_button = QPushButton("Search Course")
        self.update_course_button = QPushButton("Update Course")
        self.delete_course_button = QPushButton("Delete Course")
        self.quit_button = QPushButton("Quit")

        # Add buttons to layout
        self.layout.addWidget(self.add_student_button)
        self.layout.addWidget(self.view_students_button)
        self.layout.addWidget(self.search_student_button)
        self.layout.addWidget(self.update_student_button)
        self.layout.addWidget(self.delete_student_button)
        self.layout.addWidget(self.add_course_button)
        self.layout.addWidget(self.view_courses_button)
        self.layout.addWidget(self.search_course_button)
        self.layout.addWidget(self.update_course_button)
        self.layout.addWidget(self.delete_course_button)
        self.layout.addWidget(self.quit_button)

        # Connect button signals to slots
        self.add_student_button.clicked.connect(self.add_student_dialog)
        self.view_students_button.clicked.connect(self.view_students)
        self.search_student_button.clicked.connect(self.search_student_dialog)
        self.update_student_button.clicked.connect(self.update_student_dialog)
        self.delete_student_button.clicked.connect(self.delete_student_dialog)
        self.add_course_button.clicked.connect(self.add_course_dialog)
        self.view_courses_button.clicked.connect(self.view_courses)
        self.search_course_button.clicked.connect(self.search_course_dialog)
        self.update_course_button.clicked.connect(self.update_course_dialog)
        self.delete_course_button.clicked.connect(self.delete_course_dialog)
        self.quit_button.clicked.connect(self.close)

    def add_student_dialog(self):
        dialog = AddStudentDialog(self)
        dialog.exec_()

    def view_students(self):
        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            dialog = DisplayDataDialog(data, self)
            dialog.exec_()

    def search_student_dialog(self):
        name, ok = QInputDialog.getText(self, "Search Student", "Enter name to search:")
        if ok:
            self.search_student_by_name(name)

    def search_student_by_name(self, name):
        students = []
        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and name.lower() in row[0].lower():
                    students.append(row)
        if students:
            dialog = DisplayDataDialog(students, self)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Search Result", f"No student with name containing {name} found.")

    def update_student_dialog(self):
        dialog = UpdateStudentDialog(self)
        dialog.exec_()

    def delete_student_dialog(self):
        dialog = DeleteStudentDialog(self)
        dialog.exec_()

    def add_course_dialog(self):
        dialog = AddCourseDialog(self)
        dialog.exec_()

    def view_courses(self):
        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            dialog = DisplayDataDialog(data, self)
            dialog.exec_()

    def search_course_dialog(self):
        code, ok = QInputDialog.getText(self, "Search Course", "Enter course code to search:")
        if ok:
            self.search_course_by_code(code)

    def search_course_by_code(self, code):
        courses = []
        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and code.lower() in row[0].lower():
                    courses.append(row)
        if courses:
            dialog = DisplayDataDialog(courses, self)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Search Result", f"No course with code containing {code} found.")

    def update_course_dialog(self):
        dialog = UpdateCourseDialog(self)
        dialog.exec_()

    def delete_course_dialog(self):
        dialog = DeleteCourseDialog(self)
        dialog.exec_()


class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Student")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.fields = []
        for field in STUDENT_FIELDS:
            if field == 'Course':
                label = QLabel(field)
                combo_box = QComboBox()
                # Populate the dropdown menu with courses from the courses CSV file
                self.populate_course_dropdown(combo_box)
                layout.addWidget(label)
                layout.addWidget(combo_box)
                self.fields.append(combo_box)
            else:
                label = QLabel(field)
                edit = QLineEdit()
                layout.addWidget(label)
                layout.addWidget(edit)
                self.fields.append(edit)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_data)

    def populate_course_dropdown(self, combo_box):
        """Populate the dropdown menu with courses from the courses CSV file."""
        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    combo_box.addItem(row[1])  # Assuming course name is the second column

    def submit_data(self):
        student_data = [field.currentText() if isinstance(field, QComboBox) else field.text() for field in self.fields]
        with open(STUDENT_DATABASE, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(student_data)
        QMessageBox.information(self, "Success", "Student added successfully.")
        self.close()


class UpdateStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Student")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.id_edit = QLineEdit()
        layout.addWidget(QLabel("Student ID:"))
        layout.addWidget(self.id_edit)

        self.fields = []
        for field in STUDENT_FIELDS[1:]:  # Exclude ID field
            label = QLabel(field)
            edit = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(edit)
            self.fields.append(edit)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_data)

    def submit_data(self):
        student_id = self.id_edit.text()
        updated_student_data = [field.text() for field in self.fields]

        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)

        found = False
        updated_data = []
        for row in data:
            if row and student_id == row[1]:
                found = True
                updated_row = [row[0]] + updated_student_data
                updated_data.append(updated_row)
                print("Student Found:")
                print("\t".join(row))
            else:
                updated_data.append(row)

        if found:
            with open(STUDENT_DATABASE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(updated_data)
            QMessageBox.information(self, "Success", "Student updated successfully.")
        else:
            QMessageBox.information(self, "Error", "Student not found.")

        self.close()


class DeleteStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Student")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.id_edit = QLineEdit()
        layout.addWidget(QLabel("Student ID:"))
        layout.addWidget(self.id_edit)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_data)

    def submit_data(self):
        student_id = self.id_edit.text()

        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)

        found = False
        updated_data = []
        for row in data:
            if row and student_id == row[1]:
                found = True
                print("Student Found:")
                print("\t".join(row))
            else:
                updated_data.append(row)

        if found:
            with open(STUDENT_DATABASE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(updated_data)
            QMessageBox.information(self, "Success", "Student deleted successfully.")
        else:
            QMessageBox.information(self, "Error", "Student not found.")

        self.close()


class AddCourseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Course")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.fields = []
        for field in COURSE_FIELDS:
            label = QLabel(field)
            edit = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(edit)
            self.fields.append(edit)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_data)

    def submit_data(self):
        course_data = [field.text() for field in self.fields]
        with open(COURSE_DATABASE, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(course_data)
        QMessageBox.information(self, "Success", "Course added successfully.")
        self.close()


class UpdateCourseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Course")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.code_edit = QLineEdit()
        layout.addWidget(QLabel("Course Code:"))
        layout.addWidget(self.code_edit)

        self.fields = []
        for field in COURSE_FIELDS[1:]:  # Exclude Course Code field
            label = QLabel(field)
            edit = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(edit)
            self.fields.append(edit)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_data)

    def submit_data(self):
        course_code = self.code_edit.text()
        updated_course_data = [field.text() for field in self.fields]

        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)

        found = False
        updated_data = []
        for row in data:
            if row and course_code == row[0]:
                found = True
                updated_row = [row[0]] + updated_course_data
                updated_data.append(updated_row)
                print("Course Found:")
                print("\t".join(row))
            else:
                updated_data.append(row)

        if found:
            with open(COURSE_DATABASE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(updated_data)
            QMessageBox.information(self, "Success", "Course updated successfully.")
        else:
            QMessageBox.information(self, "Error", "Course not found.")

        self.close()


class DeleteCourseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Course")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.code_edit = QLineEdit()
        layout.addWidget(QLabel("Course Code:"))
        layout.addWidget(self.code_edit)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_data)

    def submit_data(self):
        course_code = self.code_edit.text()

        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)

        found = False
        updated_data = []
        for row in data:
            if row and course_code == row[0]:
                found = True
                print("Course Found:")
                print("\t".join(row))
            else:
                updated_data.append(row)

        if found:
            with open(COURSE_DATABASE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(updated_data)
            QMessageBox.information(self, "Success", "Course deleted successfully.")
        else:
            QMessageBox.information(self, "Error", "Course not found.")

        self.close()


class DisplayDataDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Display Data")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        table_widget = QTableWidget()
        table_widget.setColumnCount(len(data[0]) + 1)  # Additional column for enrollment status
        table_widget.setRowCount(len(data))
        headers = data[0] + ["Enrollment Status"]  # Additional header
        table_widget.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(data[1:]):
            for j, cell in enumerate(row):
                table_widget.setItem(i, j, QTableWidgetItem(cell))

            # Check if the last column (course) is empty or not to determine enrollment status
            enrollment_status = "Enrolled" if row[-1] else "Not Enrolled"
            item = QTableWidgetItem(enrollment_status)
            table_widget.setItem(i, len(row), item)

        layout.addWidget(table_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentManagementApp()
    window.show()
    sys.exit(app.exec_())
