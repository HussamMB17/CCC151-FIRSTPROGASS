from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QWidget, QComboBox, QHeaderView
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QColor, QFont
import csv
import re
from dialogs import AddStudentDialog, UpdateStudentDialog, AddCourseDialog, UpdateCourseDialog

# Constants for student fields and database files
STUDENT_FIELDS = ['First Name', 'Middle Initial', 'Last Name', 'ID', 'Year Level', 'Gender', 'Course Code']
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
        self.setWindowTitle("University Student Management System")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Get course data
        self.course_data = get_course_data()
        self.signal = Signal()

        self.init_ui()

        # Reload course data into the table
        self.course_data = get_course_data()
        self.populate_course_table(self.course_data)  # Refresh course table

        # Refresh student data in the table
        self.load_student_data()  # Refresh student table     
        self.scroll_position = 0  

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

            # Apply styles
        self.apply_styles()

    def apply_styles(self):
        # Set background color and font for the main window
        self.setStyleSheet("background-color: #f0f0f0; font-family: Arial, sans-serif; font-size: 12px;")
        self.central_widget.setStyleSheet("background-color: #f0f0f0;")

        # Set styles for buttons
        button_style = "QPushButton { background-color: #007BFF; color: white; border: 1px solid #007BFF; border-radius: 5px; padding: 8px 16px; }"
        button_hover_style = "QPushButton:hover { background-color: #0056b3; border: 1px solid #0056b3; }"
        self.add_button.setStyleSheet(button_style + button_hover_style)
        self.quit_button.setStyleSheet(button_style + button_hover_style)
        self.toggle_button.setStyleSheet(button_style + button_hover_style)

        # Set styles for search components
        search_style = "QLineEdit { background-color: white; border: 1px solid #ced4da; border-radius: 5px; padding: 8px; }"
        search_button_style = "QPushButton { background-color: #28a745; color: white; border: 1px solid #28a745; border-radius: 5px; padding: 8px 16px; }"
        search_button_hover_style = "QPushButton:hover { background-color: #218838; border: 1px solid #218838; }"
        self.search_line_edit.setStyleSheet(search_style)
        self.search_button.setStyleSheet(search_button_style + search_button_hover_style)

        # Set styles for table headers
        header_style = "QHeaderView::section { background-color: #007BFF; color: white; border: none; padding: 8px; }"
        self.student_table.horizontalHeader().setStyleSheet(header_style)

        # Set styles for table rows
        row_style = "QTableWidget::item { padding: 6px; border: none; }"
        self.student_table.setStyleSheet(row_style)

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
        fields = ['First Name', 'Middle Initial', 'Last Name', 'ID', 'Year Level', 'Gender', 'Course Code']
        return fields.index(criteria)

    def populate_student_table(self, students_data):
        """Populate the student table with the provided student data."""
        num_rows = len(students_data)
        num_cols = len(STUDENT_FIELDS)

        self.student_table.setRowCount(num_rows)
        self.student_table.setColumnCount(num_cols)
        self.student_table.setHorizontalHeaderLabels(STUDENT_FIELDS)

        for row_index, row_data in enumerate(students_data):
            for col_index, col_data in enumerate(row_data):
                item = QTableWidgetItem(col_data)
                self.student_table.setItem(row_index, col_index, item)

        # Adjust column widths to fit content
        self.student_table.resizeColumnsToContents()
        self.student_table.horizontalHeader().setStretchLastSection(True)

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
        
        # Extract course codes from course_data for validation
        valid_course_codes = [course[0] for course in self.course_data]

        for row in data[1:]:  # Exclude the header row
            if len(row) >= 7:  # Check if the row has at least 7 elements
                first_name = row[0]
                middle_initial = row[1]
                last_name = row[2]
                id_value = row[3]
                year_level = row[4]
                gender = row[5]
                course_code = row[6]

                # Determine status based on course
                if course_code.lower() != "none":
                    status = "Enrolled"
                else:
                    status = "Unenrolled"

                # Append data including status to students_data
                students_data.append([first_name, middle_initial, last_name, id_value, year_level, gender, course_code, status])
            else:
                # Handle rows that don't have enough elements (e.g., missing course code)
                # You can choose to skip these rows or handle them differently based on your requirements
                print(f"Skipping row due to insufficient data: {row}")

        return students_data

    def populate_student_table(self, students_data):
        """Populate the student table with data including the 'Status' column."""
        self.student_table.clear()  # Clear existing data
        num_columns = len(STUDENT_FIELDS) + 3  # Additional columns for 'Status', 'Update', and 'Delete'
        self.student_table.setColumnCount(num_columns)
        self.student_table.setRowCount(len(students_data))

        headers = STUDENT_FIELDS + ["Status", "Action", "Action"]
        self.student_table.setHorizontalHeaderLabels(headers)

        for i, row_data in enumerate(students_data):
            for j, cell in enumerate(row_data):
                item = QTableWidgetItem(cell)
                self.student_table.setItem(i, j, item)

            # Compute status based on course code (index 6 is the course code column)
            course_code = row_data[6].strip().lower()
            if course_code != "none":
                status = "Enrolled"
            else:
                status = "Unenrolled"

            # Add status item to the 'Status' column
            status_item = QTableWidgetItem(status)
            self.student_table.setItem(i, len(STUDENT_FIELDS), status_item)

            # Add update button
            update_button = QPushButton("Update")
            update_button.clicked.connect(lambda _, row=i: self.update_student_dialog(row))
            self.student_table.setCellWidget(i, len(STUDENT_FIELDS) + 1, update_button)

            # Add delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, row=i: self.confirm_delete_student(row))
            self.student_table.setCellWidget(i, len(STUDENT_FIELDS) + 2, delete_button)

        # Hide update and delete buttons for course entries
        self.update_delete_buttons_visibility(False)

    def populate_course_table(self, data):
        """Populate the course table with data and dynamically resize columns."""
        num_rows = len(data)
        num_cols = len(COURSE_FIELDS) + 2  # Additional columns for 'Update' and 'Delete'

        self.student_table.clear()  # Clear existing data
        self.student_table.setRowCount(num_rows)
        self.student_table.setColumnCount(num_cols)
        headers = COURSE_FIELDS + ["Update", "Delete"]
        self.student_table.setHorizontalHeaderLabels(headers)

        # Populate table data and determine initial column widths
        column_widths = [0] * num_cols
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                self.student_table.setItem(i, j, item)

                # Update column width based on content length
                column_widths[j] = max(column_widths[j], len(cell) * 10)  # Adjust multiplier as needed

            # Add 'Update' button
            update_button = QPushButton("Update")
            update_button.clicked.connect(lambda _, idx=i: self.update_course_dialog(idx))
            self.student_table.setCellWidget(i, num_cols - 2, update_button)

            # Add 'Delete' button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, idx=i: self.confirm_delete_course(idx))
            self.student_table.setCellWidget(i, num_cols - 1, delete_button)

        # Set column widths based on calculated maximums
        for col in range(num_cols):
            self.student_table.setColumnWidth(col, column_widths[col])

        # Set horizontal header resize mode to stretch last section
        header = self.student_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Resize columns to fit content
        self.resize_columns_to_fit()

    def resize_columns_to_fit(self):
        """Resize each column in the table to fit its content."""
        header = self.student_table.horizontalHeader()
        for col in range(self.student_table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
    
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
            num_columns = self.student_table.columnCount()
            for i in range(self.student_table.rowCount()):
                update_button = self.student_table.cellWidget(i, num_columns - 2)
                delete_button = self.student_table.cellWidget(i, num_columns - 1)
                if update_button:
                    update_button.setVisible(not hide)
                if delete_button:
                    delete_button.setVisible(not hide)

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
        """Delete a course from the CSV file and update student data."""
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

            # Update student data where necessary
            updated_students = []
            with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[6] == course_code_to_delete:
                        # If student was enrolled in the deleted course, update their course to "None"
                        row[6] = "None"
                    updated_students.append(row)

            # Write updated student data back to the CSV file
            with open(STUDENT_DATABASE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(updated_students)

            QMessageBox.information(self, "Success", "Course deleted successfully.")

            # Reload course data into the table
            self.course_data = get_course_data()
            self.populate_course_table(self.course_data)  # Refresh course table
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
        # Save the current scroll position
        scroll_position = self.student_table.verticalScrollBar().value()

        dialog = UpdateStudentDialog(self, row, self.course_data)
        dialog.exec_()

        # Reload student data into the table
        self.load_student_data()

        # Restore the scroll position
        self.student_table.verticalScrollBar().setValue(scroll_position)

    def confirm_delete_student(self, row):
        """Confirm deletion of a student."""
        confirmation = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete this student?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.delete_student(row + 1)

    def delete_student(self, row):
        """Delete a student."""
        # Save the current scroll position
        scroll_position = self.student_table.verticalScrollBar().value()

        with open(STUDENT_DATABASE, "r", newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)

        # Check if the row index is within the data range
        if 0 < row <= len(data):
            del data[row]  # Adjusted index to match list indexing (0-based)

            with open(STUDENT_DATABASE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(data)

            # Reload student data into the table
            self.load_student_data()

            # Restore the scroll position
            self.student_table.verticalScrollBar().setValue(scroll_position)
        else:
            QMessageBox.warning(self, "Error", "Invalid row index for student deletion.")



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = StudentManagementApp()
    window.show()
    sys.exit(app.exec_())
