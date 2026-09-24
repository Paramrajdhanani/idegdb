import json
import os


class Student:
    def __init__(self, student_id, name, age, course, marks):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.course = course
        self.marks = marks

    def calculate_percentage(self):
        if not self.marks:
            return 0

        total = sum(self.marks.values())
        subjects = len(self.marks)

        return total / subjects

    def calculate_grade(self):
        percentage = self.calculate_percentage()

        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        elif percentage >= 50:
            return "D"
        else:
            return "F"

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "course": self.course,
            "marks": self.marks
        }

    def display(self):
        print("\n" + "=" * 50)
        print("Student ID :", self.student_id)
        print("Name       :", self.name)
        print("Age        :", self.age)
        print("Course     :", self.course)

        print("\nMarks:")
        for subject, marks in self.marks.items():
            print(f"  {subject}: {marks}")

        print("\nPercentage :", round(self.calculate_percentage(), 2))
        print("Grade      :", self.calculate_grade())
        print("=" * 50)


class StudentManagementSystem:

    FILE_NAME = "students.json"

    def __init__(self):
        self.students = []
        self.load_data()

    # -----------------------------------------
    # LOAD DATA
    # -----------------------------------------

    def load_data(self):

        if not os.path.exists(self.FILE_NAME):
            self.students = []
            return

        try:
            with open(self.FILE_NAME, "r") as file:
                data = json.load(file)

            for student_data in data:

                student = Student(
                    student_data["student_id"],
                    student_data["name"],
                    student_data["age"],
                    student_data["course"],
                    student_data["marks"]
                )

                self.students.append(student)

        except (json.JSONDecodeError, KeyError):
            print("Error while loading student data.")

    # -----------------------------------------
    # SAVE DATA
    # -----------------------------------------

    def save_data(self):

        data = []

        for student in self.students:
            data.append(student.to_dict())

        with open(self.FILE_NAME, "w") as file:
            json.dump(data, file, indent=4)

    # -----------------------------------------
    # ADD STUDENT
    # -----------------------------------------

    def add_student(self):

        print("\n========== ADD STUDENT ==========")

        student_id = input("Enter Student ID: ")

        for student in self.students:
            if student.student_id == student_id:
                print("Student ID already exists.")
                return

        name = input("Enter Name: ")

        while True:
            try:
                age = int(input("Enter Age: "))

                if age <= 0:
                    print("Age must be greater than 0.")
                    continue

                break

            except ValueError:
                print("Please enter a valid number.")

        course = input("Enter Course: ")

        marks = {}

        subjects = ["Python", "Django", "SQL", "HTML", "JavaScript"]

        print("\nEnter marks:")

        for subject in subjects:

            while True:
                try:
                    mark = float(input(f"{subject}: "))

                    if mark < 0 or mark > 100:
                        print("Marks must be between 0 and 100.")
                        continue

                    marks[subject] = mark
                    break

                except ValueError:
                    print("Please enter a valid number.")

        student = Student(
            student_id,
            name,
            age,
            course,
            marks
        )

        self.students.append(student)

        self.save_data()

        print("\nStudent added successfully!")

    # -----------------------------------------
    # DISPLAY ALL STUDENTS
    # -----------------------------------------

    def display_all(self):

        print("\n========== ALL STUDENTS ==========")

        if not self.students:
            print("No students found.")
            return

        for student in self.students:
            student.display()

    # -----------------------------------------
    # SEARCH STUDENT
    # -----------------------------------------

    def search_student(self):

        print("\n========== SEARCH STUDENT ==========")

        keyword = input("Enter Student ID or Name: ").lower()

        found = False

        for student in self.students:

            if (
                keyword == student.student_id.lower()
                or keyword in student.name.lower()
            ):
                student.display()
                found = True

        if not found:
            print("Student not found.")

    # -----------------------------------------
    # UPDATE STUDENT
    # -----------------------------------------

    def update_student(self):

        print("\n========== UPDATE STUDENT ==========")

        student_id = input("Enter Student ID: ")

        student = None

        for item in self.students:
            if item.student_id == student_id:
                student = item
                break

        if student is None:
            print("Student not found.")
            return

        print("\nCurrent Details:")
        student.display()

        print("\nWhat do you want to update?")

        print("1. Name")
        print("2. Age")
        print("3. Course")
        print("4. Marks")
        print("5. Cancel")

        choice = input("Enter choice: ")

        if choice == "1":

            student.name = input("Enter new name: ")

        elif choice == "2":

            try:
                student.age = int(input("Enter new age: "))
            except ValueError:
                print("Invalid age.")
                return

        elif choice == "3":

            student.course = input("Enter new course: ")

        elif choice == "4":

            subjects = list(student.marks.keys())

            for subject in subjects:

                try:
                    mark = float(
                        input(f"Enter new marks for {subject}: ")
                    )

                    if 0 <= mark <= 100:
                        student.marks[subject] = mark
                    else:
                        print("Marks must be between 0 and 100.")

                except ValueError:
                    print("Invalid marks.")

        elif choice == "5":

            return

        else:

            print("Invalid choice.")
            return

        self.save_data()

        print("\nStudent updated successfully!")

    # -----------------------------------------
    # DELETE STUDENT
    # -----------------------------------------

    def delete_student(self):

        print("\n========== DELETE STUDENT ==========")

        student_id = input("Enter Student ID: ")

        for student in self.students:

            if student.student_id == student_id:

                print("\nStudent Found:")
                student.display()

                confirm = input(
                    "\nAre you sure you want to delete? (yes/no): "
                ).lower()

                if confirm == "yes":

                    self.students.remove(student)

                    self.save_data()

                    print("Student deleted successfully.")

                else:

                    print("Delete cancelled.")

                return

        print("Student not found.")

    # -----------------------------------------
    # TOP STUDENT
    # -----------------------------------------

    def top_student(self):

        print("\n========== TOP STUDENT ==========")

        if not self.students:
            print("No students available.")
            return

        top = max(
            self.students,
            key=lambda student: student.calculate_percentage()
        )

        top.display()

    # -----------------------------------------
    # COURSE FILTER
    # -----------------------------------------

    def filter_by_course(self):

        print("\n========== COURSE SEARCH ==========")

        course = input("Enter course: ").lower()

        found = False

        for student in self.students:

            if student.course.lower() == course:

                student.display()

                found = True

        if not found:
            print("No students found for this course.")

    # -----------------------------------------
    # STATISTICS
    # -----------------------------------------

    def statistics(self):

        print("\n========== STATISTICS ==========")

        if not self.students:
            print("No student data available.")
            return

        percentages = [
            student.calculate_percentage()
            for student in self.students
        ]

        average = sum(percentages) / len(percentages)

        passed = 0
        failed = 0

        for student in self.students:

            if student.calculate_grade() == "F":
                failed += 1
            else:
                passed += 1

        print("Total Students :", len(self.students))
        print("Average        :", round(average, 2))
        print("Passed         :", passed)
        print("Failed         :", failed)

    # -----------------------------------------
    # MENU
    # -----------------------------------------

    def menu(self):

        while True:

            print("\n")
            print("=" * 60)
            print("       STUDENT MANAGEMENT SYSTEM")
            print("=" * 60)

            print("1. Add Student")
            print("2. Display All Students")
            print("3. Search Student")
            print("4. Update Student")
            print("5. Delete Student")
            print("6. Top Student")
            print("7. Filter By Course")
            print("8. Statistics")
            print("9. Exit")

            print("=" * 60)

            choice = input("Enter your choice: ")

            if choice == "1":

                self.add_student()

            elif choice == "2":

                self.display_all()

            elif choice == "3":

                self.search_student()

            elif choice == "4":

                self.update_student()

            elif choice == "5":

                self.delete_student()

            elif choice == "6":

                self.top_student()

            elif choice == "7":

                self.filter_by_course()

            elif choice == "8":

                self.statistics()

            elif choice == "9":

                print("\nThank you for using the system!")

                break

            else:

                print("\nInvalid choice.")

            input("\nPress Enter to continue...")


# =============================================
# PROGRAM START
# =============================================

if __name__ == "__main__":

    system = StudentManagementSystem()

    system.menu()