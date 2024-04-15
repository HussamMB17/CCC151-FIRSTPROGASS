from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QWidget, QComboBox, QHeaderView
from PyQt5.QtCore import pyqtSignal, QObject, Qt
import csv
import re

# Constants for student fields and database files
STUDENT_FIELDS = ['Name', 'ID', 'Year Level', 'Gender', 'Program Code', 'Course']
STUDENT_DATABASE = 'students.csv'
COURSE_FIELDS = ['Course Code', 'Course Name']
COURSE_DATABASE = 'courses.csv'


def get_course_data():
    """Retrieve course data from the CSV file."""
    course_data = []
    with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if row:
                course_data.append(row)
    return course_data


class Signal(QObject):
    course_added = pyqtSignal()


class StudentManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Get course data
        self.course_data = get_course_data()
        self.signal = Signal()

        self.init_ui()

    def init_ui(self):
        # Create buttons
        self.toggle_button = QPushButton("Switch to Courses")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)  # By default, show student data
        self.toggle_button.toggled.connect(self.toggle_data)
        self.layout.addWidget(self.toggle_button)

        self.add_button = QPushButton("Add New Student")
        self.add_button.clicked.connect(self.add_student_dialog)  # Initially set to add student
        self.quit_button = QPushButton("Quit")

        # Add buttons to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.quit_button)
        self.layout.addLayout(button_layout)

        # Connect button signals to slots
        self.quit_button.clicked.connect(self.close)

        # Initialize student table
        self.student_table = QTableWidget()
        self.layout.addWidget(self.student_table)
        self.load_student_data()  # Corrected line

        # Add search components
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText("Search...")
        self.search_line_edit.returnPressed.connect(self.search_students)
        self.search_criteria_combo = QComboBox()
        self.search_criteria_combo.addItems(STUDENT_FIELDS)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_students)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_line_edit)
        search_layout.addWidget(self.search_criteria_combo)
        search_layout.addWidget(self.search_button)
        self.layout.addLayout(search_layout)

        # Connect signal to slot
        self.signal.course_added.connect(self.load_course_data)

        # Initially hide the course management buttons
        if hasattr(self, 'student_table'):
            self.hide_course_table_buttons(True)

    def search_students(self):
        """Search for students based on the selected criteria."""
        query = self.search_line_edit.text().strip().lower()
        criteria = self.search_criteria_combo.currentText()

        if not query:
            self.load_student_data()  # Reload all student data if query is empty
            return

        filtered_students = []
        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    if self.matches_search_criteria(row, criteria, query):
                        filtered_students.append(row)

        self.populate_student_table(filtered_students)  # Update table with filtered results

    def matches_search_criteria(self, student_data, criteria, query):
        """Check if a student matches the search criteria."""
        data_value = student_data[self.get_field_index(criteria)].lower()

        if criteria == 'ID':
            # Check if query is an exact match or substring of the ID (case-insensitive)
            return query.lower() in data_value
        elif criteria == 'Name':
            # Check if query is a substring of any part of the name (Last Name, First Name, Middle Initial)
            name_parts = [part.strip().lower() for part in student_data[0].split(',')]
            return any(query.lower() in part for part in name_parts)
        elif criteria == 'Gender':
            # Check if the first character of the gender matches the query ('M' or 'F')
            return data_value.startswith(query.lower())
        else:
            # Check if query is a substring of the specified criteria (case-insensitive)
            return query.lower() in data_value


    def get_field_index(self, criteria):
        """Get the index of the field based on the criteria."""
        fields = ['Name', 'ID', 'Year Level', 'Gender', 'Program Code', 'Course']
        return fields.index(criteria)

    def populate_student_table(self, students_data):
        """Populate the student table with the provided student data."""
        self.student_table.setRowCount(len(students_data))
        for row_index, row_data in enumerate(students_data):
            for col_index, col_data in enumerate(row_data):
                item = QTableWidgetItem(col_data)
                self.student_table.setItem(row_index, col_index, item)



    def search_courses(self):
        """Search for courses based on the selected criteria."""
        query = self.search_line_edit.text().strip().lower()
        criteria = self.search_criteria_combo.currentText()

        if not query:
            self.load_course_data()  # Reload all course data if query is empty
            return

        filtered_courses = []
        with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    if criteria == 'Course Code' and query in row[0].lower():
                        filtered_courses.append(row)
                    elif criteria == 'Course Name' and query in row[1].lower():
                        filtered_courses.append(row)

        self.populate_course_table(filtered_courses)  # Update table with filtered results


    def toggle_data(self, checked):
        """Toggle between student data and course data."""
        if checked:
            self.toggle_button.setText("Switch to Students")
            self.load_course_data()
            self.add_button.setText("Add New Course")
            self.add_button.clicked.disconnect(self.add_student_dialog)
            self.add_button.clicked.connect(self.add_course_dialog)
            if hasattr(self, 'student_table'):
                self.hide_student_table_buttons(True)  # Hide student table buttons
                self.hide_course_table_buttons(False)  # Show course table buttons
                self.update_delete_buttons_visibility(course_view=True)  # Show course update and delete buttons

            # Change search criteria for course view
            self.search_criteria_combo.clear()
            self.search_criteria_combo.addItems(COURSE_FIELDS)
            self.search_button.clicked.disconnect(self.search_students)
            self.search_button.clicked.connect(self.search_courses)
        else:
            self.toggle_button.setText("Switch to Courses")
            self.load_student_data()
            self.add_button.setText("Add New Student")
            self.add_button.clicked.disconnect(self.add_course_dialog)
            self.add_button.clicked.connect(self.add_student_dialog)
            if hasattr(self, 'student_table'):
                self.hide_student_table_buttons(False)  # Show student table buttons
                self.hide_course_table_buttons(True)  # Hide course table buttons
                self.update_delete_buttons_visibility(course_view=False)  # Hide course update and delete buttons

            # Change search criteria for student view
            self.search_criteria_combo.clear()
            self.search_criteria_combo.addItems(STUDENT_FIELDS)
            self.search_button.clicked.disconnect(self.search_courses)
            self.search_button.clicked.connect(self.search_students)

    def update_delete_buttons_visibility(self, course_view):
        """Hide or show the update and delete buttons based on the view."""
        if hasattr(self, 'student_table'):
            num_cols = self.student_table.columnCount()
            for i in range(self.student_table.rowCount()):
                update_button = self.student_table.cellWidget(i, num_cols - 2)
                delete_button = self.student_table.cellWidget(i, num_cols - 1)
                if course_view:
                    # Show course update and delete buttons
                    if update_button:
                        update_button.setVisible(True)
                    if delete_button:
                        delete_button.setVisible(True)
                else:
                    # Hide course update and delete buttons
                    if update_button:
                        update_button.setVisible(False)
                    if delete_button:
                        delete_button.setVisible(False)

    def load_student_data(self):
        """Load student data into the table with 'Status' column."""
        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            students_data = self.compute_student_status(data)
            self.populate_student_table(students_data)

    def compute_student_status(self, data):
        """Compute the 'Status' (Enrolled/Unenrolled) based on the course."""
        students_data = []
        for row in data[1:]:  # Exclude the header row
            full_name = row[0]
            id_value = row[1]
            year_level = row[2]
            gender = row[3]
            program_code = row[4]
            course = row[5]

            # Determine status based on course
            if course.lower() != "none":
                status = "Enrolled"
            else:
                status = "Unenrolled"

            # Append data including status to students_data
            students_data.append([full_name, id_value, year_level, gender, program_code, course, status])

        return students_data
    
    def populate_student_table(self, students_data):
        """Populate the student table with data including the 'Status' column."""
        self.student_table.clear()  # Clear existing data
        num_columns = len(STUDENT_FIELDS) + 3  # Additional column for 'Status' and two action columns
        self.student_table.setColumnCount(num_columns)
        self.student_table.setRowCount(len(students_data))

        headers = STUDENT_FIELDS + ["Course", "Status", "Update", "Delete"]
        self.student_table.setHorizontalHeaderLabels(headers)

        for i, row_data in enumerate(students_data):
            for j, cell in enumerate(row_data):
                item = QTableWidgetItem(cell)
                self.student_table.setItem(i, j, item)

            
            # Add update button
            update_button = QPushButton("Update")
            update_button.clicked.connect(lambda _, i=i: self.update_student_dialog(i))
            self.student_table.setCellWidget(i, num_columns - 2, update_button)

            # Add delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, i=i: self.confirm_delete_student(i))
            self.student_table.setCellWidget(i, num_columns - 1, delete_button)

        # Hide update and delete buttons for course entries
        self.update_delete_buttons_visibility(False)


    def populate_course_table(self, data):
        """Populate the course table with data."""
        self.student_table.clear()  # Clear existing data
        self.student_table.setColumnCount(len(COURSE_FIELDS) + 2)  # Add two columns for actions
        self.student_table.setRowCount(len(data))
        headers = COURSE_FIELDS + ["Update", "Delete"]
        self.student_table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                self.student_table.setItem(i, j, item)

            # Add update button
            update_button = QPushButton("Update")
            update_button.clicked.connect(lambda _, i=i: self.update_course_dialog(i))
            self.student_table.setCellWidget(i, len(COURSE_FIELDS), update_button)

            # Add delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, i=i: self.confirm_delete_course(i))
            self.student_table.setCellWidget(i, len(COURSE_FIELDS) + 1, delete_button)

        # Hide the update and delete buttons for student entries
        self.update_delete_buttons_visibility(True)  # Change to True



    def hide_student_table_buttons(self, hide):
        """Hide or show the update and delete buttons in the student data table."""
        if hasattr(self, 'student_table'):
            num_columns = self.student_table.columnCount()
            for i in range(self.student_table.rowCount()):
                for j in range(num_columns - 2, num_columns):
                    item = self.student_table.cellWidget(i, j)
                    if item:
                        item.setVisible(not hide)

    def hide_course_table_buttons(self, hide):
        """Hide or show the update and delete buttons in the course data table."""
        if hasattr(self, 'student_table'):
            for i in range(self.student_table.rowCount()):
                if not hide:
                    update_button = self.student_table.cellWidget(i, len(STUDENT_FIELDS))
                    delete_button = self.student_table.cellWidget(i, len(STUDENT_FIELDS) + 1)
                    if update_button:
                        update_button.setVisible(True)
                    if delete_button:
                        delete_button.setVisible(True)
                else:
                    update_button = self.student_table.cellWidget(i, len(STUDENT_FIELDS))
                    delete_button = self.student_table.cellWidget(i, len(STUDENT_FIELDS) + 1)
                    if update_button:
                        update_button.setVisible(False)
                    if delete_button:
                        delete_button.setVisible(False)

    def load_course_data(self):
        """Load course data into the table."""
        self.course_data = get_course_data()  # Reload course data
        self.student_table.clear()  # Clear existing data
        self.student_table.setColumnCount(len(COURSE_FIELDS) + 2)  # Add two columns for actions
        self.student_table.setRowCount(len(self.course_data))
        headers = COURSE_FIELDS + ["Update", "Delete"]
        self.student_table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(self.course_data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                self.student_table.setItem(i, j, item)

            # Add update button
            update_button = QPushButton("Update")
            update_button.clicked.connect(lambda _, i=i: self.update_course_dialog(i))
            self.student_table.setCellWidget(i, len(COURSE_FIELDS), update_button)

            # Add delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, i=i: self.confirm_delete_course(i))
            self.student_table.setCellWidget(i, len(COURSE_FIELDS) + 1, delete_button)

        # Hide the update and delete buttons for student entries
        self.update_delete_buttons_visibility(False)

    def add_student_dialog(self):
        """Open dialog to add a new student."""
        dialog = AddStudentDialog(self, self.course_data)
        dialog.exec_()
        self.load_student_data()

    def add_course_dialog(self):
        """Open dialog to add a new course."""
        dialog = AddCourseDialog(self)
        dialog.exec_()

    def update_course_dialog(self, row):
        """Open dialog to update course information."""
        dialog = UpdateCourseDialog(self, row)
        dialog.exec_()
        self.load_course_data()

    def delete_course(self, row):
        """Delete a course from the CSV file and reload course data."""
        if row >= 0 and row < len(self.course_data):
            course_code_to_delete = self.course_data[row][0]

            # Remove the course from the CSV file
            with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                data = list(reader)

            updated_data = [course for course in data if course[0] != course_code_to_delete]

            with open(COURSE_DATABASE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(updated_data)

            # Notify the user that the course has been successfully deleted
            QMessageBox.information(self, "Success", "Course deleted successfully.")

            # Reload course data into the table
            self.course_data = get_course_data()
            self.populate_course_table(self.course_data)
        else:
            QMessageBox.warning(self, "Error", "Invalid row index for course deletion.")

    def confirm_delete_course(self, row):
            """Confirm deletion of a course."""
            confirmation = QMessageBox.question(
                self,
                "Confirm Deletion",
                "Are you sure you want to delete this course?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                self.delete_course(row)  # Call the delete_course method to delete the course

    def update_student_dialog(self, row):
        """Open dialog to update student information."""
        dialog = UpdateStudentDialog(self, row, self.course_data)
        dialog.exec_()
        self.load_student_data()

    def confirm_delete_student(self, row):
        """Confirm deletion of a student."""
        confirmation = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete this student?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.delete_student(row + 1)

    def delete_student(self, row):
        """Delete a student."""
        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
        del data[row]
        with open(STUDENT_DATABASE, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        self.load_student_data()


class AddStudentDialog(QDialog):
    def __init__(self, parent=None, course_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add Student")
        self.setGeometry(200, 200, 400, 350)

        self.course_data = course_data

        layout = QVBoxLayout(self)

        # Add fields for ID, first name, middle initial, last name, and program code
        self.id_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.middle_initial_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.program_code_edit = QLineEdit()

        layout.addWidget(QLabel("ID:"))
        layout.addWidget(self.id_edit)
        layout.addWidget(QLabel("First Name:"))
        layout.addWidget(self.first_name_edit)
        layout.addWidget(QLabel("Middle Initial:"))
        layout.addWidget(self.middle_initial_edit)
        layout.addWidget(QLabel("Last Name:"))
        layout.addWidget(self.last_name_edit)
        layout.addWidget(QLabel("Program Code:"))
        layout.addWidget(self.program_code_edit)

        # Add existing student fields (Year Level, Gender, Course)
        self.fields = []
        for field in ["Year Level", "Gender", "Course"]:
            label = QLabel(field)
            combo_box = QComboBox()
            if field == "Year Level":
                combo_box.addItems(['1', '2', '3', '4'])  # Restrict options to 1, 2, 3, 4
            elif field == "Gender":
                combo_box.addItems(['Male', 'Female'])  # Restrict options to Male and Female
            elif field == "Course":
                combo_box.addItem('None')
                for course in self.course_data:
                    combo_box.addItem(course[1])  # Add course name
            layout.addWidget(label)
            layout.addWidget(combo_box)
            self.fields.append(combo_box)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_data)
        layout.addWidget(self.submit_button)

    def submit_data(self):
        """Submit student data."""
        id_value = self.id_edit.text()
        first_name = self.first_name_edit.text()
        middle_initial = self.middle_initial_edit.text()
        last_name = self.last_name_edit.text()
        program_code = self.program_code_edit.text()
        year_level = self.fields[0].currentText()
        gender = self.fields[1].currentText()
        course = self.fields[2].currentText()

        # Validate required fields (ID, First Name, Last Name, Program Code)
        if not id_value or not first_name or not last_name or not program_code:
            QMessageBox.warning(self, "Error", "Please enter ID, First Name, Last Name, and Program Code.")
            return

        # Format the student's name with middle initial if provided
        if middle_initial:
            formatted_name = f"{last_name}, {first_name} {middle_initial.upper()}"
        else:
            formatted_name = f"{last_name}, {first_name}"

        # Prepare student data in the correct order for CSV writing
        student_data = [formatted_name, id_value, year_level, gender, program_code, course]

        # Validate all student data (you can implement custom validation logic here)
        if self.validate_student_data(student_data):
            try:
                # Append student data to the CSV file
                with open(STUDENT_DATABASE, "a", newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(student_data)
                    
                # Show success message
                QMessageBox.information(self, "Success", "Student added successfully.")

                # Emit signal to update the main window
                self.parent().signal.course_added.emit()
                self.accept()  # Close the dialog
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please enter valid data.")

    def validate_student_data(self, student_data):
        """Validate student data."""
        # Implement your custom validation logic here
        # For example, check for unique ID, correct format of fields, etc.
        return True


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
        course_data = [field.text() for field in self.fields]

        # Validate course data
        if self.validate_course_data(course_data):
            with open(COURSE_DATABASE, "a", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(course_data)
            QMessageBox.information(self, "Success", "Course added successfully.")
            if self.parent():
                if hasattr(self.parent(), 'signal'):
                    self.parent().signal.course_added.emit()  # Emit signal after adding a course
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Please enter valid data.")

    def validate_course_data(self, course_data):
        """Validate course data."""
        # You can add your validation logic here
        return True


class UpdateStudentDialog(QDialog):
    def __init__(self, parent=None, row=None, course_data=None):
        super().__init__(parent)
        self.setWindowTitle("Update Student")
        self.setGeometry(200, 200, 400, 350)

        self.row = row
        self.course_data = course_data

        layout = QVBoxLayout(self)

        # Add fields for ID, first name, middle initial, last name, and program code
        self.id_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.middle_initial_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.program_code_edit = QLineEdit()

        layout.addWidget(QLabel("ID:"))
        layout.addWidget(self.id_edit)
        layout.addWidget(QLabel("First Name:"))
        layout.addWidget(self.first_name_edit)
        layout.addWidget(QLabel("Middle Initial:"))
        layout.addWidget(self.middle_initial_edit)
        layout.addWidget(QLabel("Last Name:"))
        layout.addWidget(self.last_name_edit)
        layout.addWidget(QLabel("Program Code:"))
        layout.addWidget(self.program_code_edit)

        # Add existing student fields (Year Level, Gender, Course)
        self.fields = []
        for field in ["Year Level", "Gender", "Course"]:
            label = QLabel(field)
            combo_box = QComboBox()
            if field == "Year Level":
                combo_box.addItems(['1', '2', '3', '4'])  # Restrict options to 1, 2, 3, 4
            elif field == "Gender":
                combo_box.addItems(['Male', 'Female'])  # Restrict options to Male and Female
            elif field == "Course":
                combo_box.addItem('None')
                for course in self.course_data:
                    combo_box.addItem(course[1])  # Add course name
            layout.addWidget(label)
            layout.addWidget(combo_box)
            self.fields.append(combo_box)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_data)
        layout.addWidget(self.submit_button)

        # Pre-fill the dialog with existing student data
        self.populate_fields()

    def populate_fields(self):
        """Populate dialog fields with existing student data."""
        if self.row is not None:
            # Get data from the main window's student table
            id_value = self.parent().student_table.item(self.row, 1).text()  # ID
            full_name = self.parent().student_table.item(self.row, 0).text()  # Full Name
            year_level = self.parent().student_table.item(self.row, 2).text()  # Year Level
            gender = self.parent().student_table.item(self.row, 3).text()  # Gender
            program_code = self.parent().student_table.item(self.row, 4).text()  # Program Code
            course = self.parent().student_table.item(self.row, 5).text()  # Course

            # Populate the dialog fields
            self.id_edit.setText(id_value)

            if ',' in full_name:
                last_name, first_and_middle = full_name.split(',', 1)
                first_and_middle = first_and_middle.strip()
                if ' ' in first_and_middle:
                    first_name, middle_initial = first_and_middle.split(' ', 1)
                    self.middle_initial_edit.setText(middle_initial)
                else:
                    first_name = first_and_middle
                self.first_name_edit.setText(first_name)
                self.last_name_edit.setText(last_name.strip())
            else:
                self.first_name_edit.setText(full_name)

            self.program_code_edit.setText(program_code)

            year_level_index = self.fields[0].findText(year_level)  # Year Level
            if year_level_index != -1:
                self.fields[0].setCurrentIndex(year_level_index)

            gender_index = self.fields[1].findText(gender)  # Gender
            if gender_index != -1:
                self.fields[1].setCurrentIndex(gender_index)

            course_index = self.fields[2].findText(course)  # Course
            if course_index != -1:
                self.fields[2].setCurrentIndex(course_index)

    def submit_data(self):
        """Submit updated student data."""
        id_value = self.id_edit.text()
        first_name = self.first_name_edit.text()
        middle_initial = self.middle_initial_edit.text()
        last_name = self.last_name_edit.text()
        program_code = self.program_code_edit.text()
        year_level = self.fields[0].currentText()
        gender = self.fields[1].currentText()
        course = self.fields[2].currentText()

        # Validate required fields (ID, First Name, Last Name, Program Code)
        if not id_value or not first_name or not last_name or not program_code:
            QMessageBox.warning(self, "Error", "Please enter ID, First Name, Last Name, and Program Code.")
            return

        # Format the student's name with middle initial if provided
        if middle_initial:
            formatted_name = f"{last_name}, {first_name} {middle_initial.upper()}"
        else:
            formatted_name = f"{last_name}, {first_name}"

        # Prepare updated student data in the correct order for CSV writing
        updated_student_data = [formatted_name, id_value, year_level, gender, program_code, course]

        # Validate all updated student data (you can implement custom validation logic here)
        if self.validate_student_data(updated_student_data):
            try:
                # Update student data in the CSV file
                with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
                    reader = csv.reader(f)
                    data = list(reader)

                # Find the row index of the existing student data
                row_index = None
                for i, row in enumerate(data):
                    if row[1] == id_value:  # Compare by ID
                        row_index = i
                        break

                if row_index is not None:
                    data[row_index] = updated_student_data  # Update the data

                    with open(STUDENT_DATABASE, "w", newline='', encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerows(data)

                    QMessageBox.information(self, "Success", "Student updated successfully.")
                    self.accept()  # Close the dialog after successful update
                else:
                    QMessageBox.warning(self, "Error", "Student not found in the database.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please enter valid data.")

    def validate_student_data(self, student_data):
        """Validate updated student data."""
        # You can add your validation logic here
        return True

class UpdateCourseDialog(QDialog):
    def __init__(self, parent=None, row=None):
        super().__init__(parent)
        self.setWindowTitle("Update Course")
        self.setGeometry(200, 200, 400, 200)

        self.row = row

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.fields = []
        for i, field in enumerate(COURSE_FIELDS):
            label = QLabel(field)
            edit = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(edit)
            self.fields.append(edit)
            edit.setText(parent.student_table.item(self.row, i).text())

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_data)

    def submit_data(self):
        """Submit updated course data."""
        updated_data = [field.text() for field in self.fields]

        # Validate updated data
        if self.validate_course_data(updated_data):
            # Load existing course data
            with open(COURSE_DATABASE, "r", newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                data = list(reader)

            # Update data for the specific row
            data[self.row + 1] = updated_data  # Adjust row index to account for header row

            # Write updated data back to CSV file
            with open(COURSE_DATABASE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(data)

            QMessageBox.information(self, "Success", "Course updated successfully.")
            self.parent().load_course_data()  # Reload data in main window
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Please enter valid data.")

    def validate_course_data(self, course_data):
        """Validate updated course data."""
        # You can add your validation logic here
        return True


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = StudentManagementApp()
    window.show()
    sys.exit(app.exec_())
