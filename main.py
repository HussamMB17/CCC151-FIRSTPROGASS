import sys
import csv
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog, QWidget, QComboBox, QHeaderView

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
        """Open dialog to add a new student."""
        dialog = AddStudentDialog(self)
        dialog.exec_()

    def view_students(self):
        """View all students."""
        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            dialog = DisplayDataDialog(data, self)
            dialog.exec_()

    def search_student_dialog(self):
        """Open dialog to search for a student by name."""
        name, ok = QInputDialog.getText(self, "Search Student", "Enter name to search:")
        if ok:
            self.search_student_by_name(name)

    def search_student_by_name(self, name):
        """Search for a student by name."""
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
        """Open dialog to update student information."""
        dialog = UpdateStudentDialog(self)
        dialog.exec_()

    def delete_student_dialog(self):
        """Open dialog to delete a student."""
        dialog = DeleteStudentDialog(self)
        dialog.exec_()

    def add_course_dialog(self):
        """Open dialog to add a new course."""
        dialog = AddCourseDialog(self)
        dialog.exec_()

    def view_courses(self):
        """View all courses."""
        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            dialog = DisplayDataDialog(data, self)
            dialog.exec_()

    def search_course_dialog(self):
        """Open dialog to search for a course by code."""
        code, ok = QInputDialog.getText(self, "Search Course", "Enter course code to search:")
        if ok:
            self.search_course_by_code(code)

    def search_course_by_code(self, code):
        """Search for a course by code."""
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
        """Open dialog to update course information."""
        dialog = UpdateCourseDialog(self)
        dialog.exec_()

    def delete_course_dialog(self):
        """Open dialog to delete a course."""
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
            if field == 'Year Level':
                label = QLabel(field)
                combo_box = QComboBox()
                combo_box.addItems(['1', '2', '3', '4'])  # Restrict options to 1, 2, 3, 4
                layout.addWidget(label)
                layout.addWidget(combo_box)
                self.fields.append(combo_box)
            elif field == 'Gender':
                label = QLabel(field)
                combo_box = QComboBox()
                combo_box.addItems(['Male', 'Female'])  # Restrict options to Male and Female
                layout.addWidget(label)
                layout.addWidget(combo_box)
                self.fields.append(combo_box)
            elif field == 'Course':
                label = QLabel(field)
                combo_box = QComboBox()
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
        course_codes = []
        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    course_codes.append(row[1])  # Assuming course name is the second column
        combo_box.addItems(course_codes)

    def submit_data(self):
        """Submit student data."""
        student_data = [field.currentText() if isinstance(field, QComboBox) else field.text() for field in self.fields]
        
        # Validate student data
        if self.validate_student_data(student_data):
            with open(STUDENT_DATABASE, "a", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(student_data)
            QMessageBox.information(self, "Success", "Student added successfully.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Please enter valid data. Student ID should be in the format XXXX-XXXX.")

    def validate_student_data(self, student_data):
        """Validate student data."""
        name, student_id, year_level, gender, program_code, course = student_data
        # Validate student ID format (XXXX-XXXX)
        if not re.match(r'^\d{4}-\d{4}$', student_id):
            return False
        # Add more validation rules as needed
        return True
    
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

        self.name_edit = QLineEdit()  # Name field
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_edit)

        self.year_level_combo = QComboBox()  # Year Level dropdown
        layout.addWidget(QLabel("Year Level:"))
        layout.addWidget(self.year_level_combo)
        self.year_level_combo.addItems(['1', '2', '3', '4'])  # Restrict options to 1, 2, 3, 4

        self.gender_combo = QComboBox()  # Gender dropdown
        layout.addWidget(QLabel("Gender:"))
        layout.addWidget(self.gender_combo)
        self.gender_combo.addItems(['Male', 'Female'])  # Restrict options to Male and Female

        self.course_combo_box = QComboBox()  # Course dropdown
        layout.addWidget(QLabel("Course:"))
        layout.addWidget(self.course_combo_box)
        self.populate_course_dropdown()  # Populate course dropdown

        self.fields = []
        for field in STUDENT_FIELDS[2:]:  # Exclude ID and Name fields
            if field in ['Year Level', 'Gender', 'Course']:
                continue  # Year Level, Gender, and Course fields already added as dropdowns
            label = QLabel(field)
            edit = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(edit)
            self.fields.append(edit)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_data)

    def populate_course_dropdown(self):
        """Populate the dropdown menu with courses from the courses CSV file."""
        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    self.course_combo_box.addItem(row[1])  # Assuming course name is the second column

    def submit_data(self):
        """Submit updated student data."""
        student_id = self.id_edit.text()
        updated_name = self.name_edit.text()  # Get updated name
        updated_year_level = self.year_level_combo.currentText()  # Get selected year level from dropdown
        updated_gender = self.gender_combo.currentText()  # Get selected gender from dropdown
        updated_course = self.course_combo_box.currentText()  # Get selected course from dropdown

        updated_student_data = [updated_name, updated_year_level, updated_gender, updated_course]  # Add selected data to updated list

        for field in self.fields:
            updated_student_data.append(field.text())

        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)

        found = False
        updated_data = []
        for row in data:
            if row and student_id == row[1]:
                found = True
                updated_row = [row[0], student_id] + updated_student_data  # Keep original ID, update other fields
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
        """Delete a student."""
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
        """Submit course data."""
        course_code = self.fields[0].text().strip()
        if not self.validate_course_code(course_code):
            QMessageBox.warning(self, "Error", "Invalid course code format. Please enter a code in the format CCC151 or GEC109.")
            return

        course_data = [field.text() for field in self.fields]
        with open(COURSE_DATABASE, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(course_data)
        QMessageBox.information(self, "Success", "Course added successfully.")
        self.close()

    def validate_course_code(self, course_code):
        """Validate the format of the course code."""
        return re.match(r'^[A-Z]{3}\d{3}$', course_code) is not None

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
        """Submit updated course data."""
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
        """Delete a course."""
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
        num_columns = len(data[0])
        table_widget.setColumnCount(num_columns + 1)  # Additional column for enrollment status
        table_widget.setRowCount(len(data))
        headers = data[0] + ["Enrollment Status"]  # Additional header
        table_widget.setHorizontalHeaderLabels(headers)

        # Set data and adjust column widths
        for i, row in enumerate(data[1:]):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                table_widget.setItem(i, j, item)

            # Determine enrollment status
            enrollment_status = "Enrolled" if row[-1] else "Unenrolled"
            status_item = QTableWidgetItem(enrollment_status)
            table_widget.setItem(i, num_columns, status_item)

        # Check and adjust column widths based on content
        for j in range(num_columns + 1):
            max_width = 0
            for i in range(len(data)):
                item = table_widget.item(i, j)
                if item is not None:
                    max_width = max(max_width, table_widget.fontMetrics().boundingRect(item.text()).width())
            table_widget.setColumnWidth(j, max_width + 20)  # Add some extra space for better readability

        # Adjust column header sizes to content
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addWidget(table_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentManagementApp()
    window.show()
    sys.exit(app.exec_())