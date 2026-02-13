"""
Student Management System 
Description: A GUI-based student management system using Tkinter and MySQL
"""

# ============================================================================
# IMPORTS
# ============================================================================
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.ttk import Treeview, Style
import mysql.connector
import time
import random
import re

# ============================================================================
# CONFIGURATION
# ============================================================================
WINDOW_WIDTH = 1174
WINDOW_HEIGHT = 700
DB_NAME = "student_management_system"
ANIMATION_COLORS = ["red", "green", "blue", "orange", "purple"]

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_mobile(mobile):
    """Validate mobile number (10 digits)"""
    return mobile.isdigit() and len(mobile) == 10

def validate_id(student_id):
    """Validate student ID (must be positive integer)"""
    try:
        return int(student_id) > 0
    except ValueError:
        return False

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================
def addstudent():
    """Open window to add a new student"""
    def submitadd():
        global con, mycursor, framedata

        # Get and strip input values
        id_val = idvalue.get().strip()
        name = namevalue.get().strip()
        gender = gendervalue.get()
        dob = dobvalue.get().strip()
        mobile = mobilevalue.get().strip()
        email = emailvalue.get().strip()

        # Validate empty fields
        if not all([id_val, name, gender, dob, mobile, email]):
            messagebox.showerror("Error", "All fields are required", parent=addstudt)
            return

        # Validate ID
        if not validate_id(id_val):
            messagebox.showerror("Error", "ID must be a positive number", parent=addstudt)
            return
        
        id_val = int(id_val)

        # Validate mobile
        if not validate_mobile(mobile):
            messagebox.showerror("Error", "Mobile must be exactly 10 digits", parent=addstudt)
            return

        # Validate email
        if not validate_email(email):
            messagebox.showerror("Error", "Invalid email format", parent=addstudt)
            return

        # Check database connection
        if mycursor is None:
            messagebox.showerror("DB Error", "Please connect to the database first.", parent=addstudt)
            return

        try:
            query = "INSERT INTO studentdata (id, name, dob, gender, mobile, email) VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor.execute(query, (id_val, name, dob, gender, mobile, email))
            con.commit()
            
            messagebox.showinfo("Success", f"Student '{name}' (ID: {id_val}) added successfully!", parent=addstudt)

            # Clear fields
            idvalue.set("")
            namevalue.set("")
            gendervalue.set("")
            dobvalue.set("")
            mobilevalue.set("")
            emailvalue.set("")
            
            # Refresh the Treeview
            showstudent()

        except mysql.connector.errors.IntegrityError:
            messagebox.showerror("Error", f"Student with ID {id_val} already exists!", parent=addstudt)
        except Exception as e:
            messagebox.showerror("Error", f"Database error:\n{str(e)}", parent=addstudt)

    # ========== GUI Setup ==========
    addstudt = Toplevel(master=DataEntryFrame)
    addstudt.grab_set()
    addstudt.geometry("470x520+220+200")
    addstudt.title("Add Student")
    addstudt.config(bg="blue")
    addstudt.resizable(False, False)
    
    # Set icon (with error handling)
    try:
        addstudt.iconbitmap("student.ico")
    except:
        pass  # Icon file not found

    # Variables
    idvalue = StringVar()
    namevalue = StringVar()
    gendervalue = StringVar()
    dobvalue = StringVar()
    mobilevalue = StringVar()
    emailvalue = StringVar()

    # Labels and Entries
    fields = [
        ("Enter Id :", idvalue, None),
        ("Enter Name :", namevalue, None),
        ("Enter Gender :", gendervalue, ["Male", "Female", "Other"]),
        ("Enter D.O.B :", dobvalue, None),
        ("Enter Mobile :", mobilevalue, None),
        ("Enter Email :", emailvalue, None),
    ]

    y_pos = 15
    for label_text, var, options in fields:
        Label(addstudt, text=label_text, bg="gold2", font=("times", 20, "bold"),
              relief=GROOVE, borderwidth=3, width=12, anchor="w").place(x=10, y=y_pos)
        
        if options:  # Create dropdown for gender
            ttk.Combobox(addstudt, font=("roman", 15, "bold"), textvariable=var, 
                        values=options, state="readonly").place(x=250, y=y_pos)
        else:  # Create entry field
            Entry(addstudt, font=("roman", 15, "bold"), bd=5, textvariable=var).place(x=250, y=y_pos)
        
        y_pos += 60

    # Help text
    Label(addstudt, text="Format: DOB (DD/MM/YYYY), Mobile (10 digits)", 
          bg="blue", fg="white", font=("arial", 10)).place(x=50, y=390)

    # Submit Button
    Button(addstudt, text="Submit", font=("roman", 15, "bold"), width=20, bd=5,
           activebackground="blue", activeforeground="white", bg="green", 
           command=submitadd).place(x=150, y=440)

    addstudt.mainloop()


def searchstudent():
    """Search for a student by ID"""
    def search():
        global con, mycursor

        student_id = idvalue.get().strip()

        if not student_id:
            messagebox.showerror("Error", "Please enter a student ID", parent=searchwin)
            return

        if not validate_id(student_id):
            messagebox.showerror("Error", "ID must be a valid number", parent=searchwin)
            return

        try:
            query = "SELECT * FROM studentdata WHERE id = %s"
            mycursor.execute(query, (student_id,))
            data = mycursor.fetchall()

            if not data:
                messagebox.showinfo("No Result", f"No student found with ID {student_id}", parent=searchwin)
                return

            # Clear Treeview and show search result
            framedata.delete(*framedata.get_children())
            for item in data:
                framedata.insert('', END, values=item)
            
            searchwin.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Database error:\n{str(e)}", parent=searchwin)

    # ========== GUI Setup ==========
    searchwin = Toplevel()
    searchwin.title("Search Student by ID")
    searchwin.geometry("450x200+300+200")
    searchwin.config(bg="blue")
    searchwin.resizable(False, False)
    
    try:
        searchwin.iconbitmap("student.ico")
    except:
        pass

    idvalue = StringVar()

    Label(searchwin, text="Enter ID :", bg="gold2", font=("times", 20, "bold"),
          relief=GROOVE, borderwidth=3, width=12, anchor="w").place(x=10, y=40)

    Entry(searchwin, font=("roman", 15, "bold"), bd=5, textvariable=idvalue).place(x=220, y=40)

    Button(searchwin, text="Search", font=("roman", 15, "bold"), width=15, bd=5,
           activebackground="blue", activeforeground="white", bg="green", 
           command=search).place(x=120, y=120)


def deletestudent():
    """Delete a student record"""
    def delete():
        global mycursor, con
        
        student_id = idvalue.get().strip()
        
        if not student_id:
            messagebox.showerror("Error", "ID is required to delete", parent=deletestudentwin)
            return
        
        if not validate_id(student_id):
            messagebox.showerror("Error", "ID must be a valid number", parent=deletestudentwin)
            return

        try:
            # Check if record exists
            mycursor.execute("SELECT name FROM studentdata WHERE id=%s", (student_id,))
            result = mycursor.fetchone()
            
            if result is None:
                messagebox.showerror("Error", f"No student found with ID {student_id}", parent=deletestudentwin)
                return
            
            student_name = result[0]
            
            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete:\n\nID: {student_id}\nName: {student_name}",
                parent=deletestudentwin
            )
            
            if not confirm:
                return
            
            # Delete the record
            query = "DELETE FROM studentdata WHERE id=%s"
            mycursor.execute(query, (student_id,))
            con.commit()
            
            messagebox.showinfo("Success", f"Student '{student_name}' deleted successfully", parent=deletestudentwin)
            idvalue.set("")
            
            # Refresh Treeview
            showstudent()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record:\n{e}", parent=deletestudentwin)

    # ========== GUI Setup ==========
    deletestudentwin = Toplevel(master=DataEntryFrame)
    deletestudentwin.grab_set()
    deletestudentwin.geometry("400x200+500+300")
    deletestudentwin.title("Delete Student")
    deletestudentwin.config(bg="blue")
    
    try:
        deletestudentwin.iconbitmap("student.ico")
    except:
        pass

    Label(deletestudentwin, text="Enter Id : ", bg="gold2", font=("times", 20, "bold"), 
          relief=GROOVE, borderwidth=3, width=9, anchor="w").place(x=10, y=40)

    idvalue = StringVar()
    Entry(deletestudentwin, font=("roman", 15, "bold"), bd=5, textvariable=idvalue).place(x=180, y=40)

    Button(deletestudentwin, text="Delete", font=("roman", 15, "bold"), width=15, bd=5,
           activebackground="blue", activeforeground="white", bg="red", 
           command=delete).place(x=120, y=120)


def updatestudent():
    """Update student information"""
    def load_student():
        """Load existing student data into form"""
        sid = idvalue.get().strip()
        
        if not sid:
            messagebox.showerror("Error", "Enter Student ID first", parent=updatewin)
            return
        
        if not validate_id(sid):
            messagebox.showerror("Error", "ID must be a valid number", parent=updatewin)
            return
        
        try:
            mycursor.execute("SELECT * FROM studentdata WHERE id = %s", (sid,))
            result = mycursor.fetchone()
            
            if result:
                namevalue.set(result[1])
                dobvalue.set(result[2])
                gendervalue.set(result[3])
                mobilevalue.set(result[4])
                emailvalue.set(result[5])
                messagebox.showinfo("Success", "Student data loaded", parent=updatewin)
            else:
                messagebox.showerror("Error", f"No student found with ID {sid}", parent=updatewin)
                
        except Exception as e:
            messagebox.showerror("Error", f"Database error:\n{str(e)}", parent=updatewin)

    def update():
        """Update student record"""
        global mycursor, con

        sid = idvalue.get().strip()
        name = namevalue.get().strip()
        gender = gendervalue.get()
        dob = dobvalue.get().strip()
        mobile = mobilevalue.get().strip()
        email = emailvalue.get().strip()

        # Validate inputs
        if not all([sid, name, gender, dob, mobile, email]):
            messagebox.showerror("Error", "All fields are required", parent=updatewin)
            return

        if not validate_id(sid):
            messagebox.showerror("Error", "ID must be a valid number", parent=updatewin)
            return

        if not validate_mobile(mobile):
            messagebox.showerror("Error", "Mobile must be exactly 10 digits", parent=updatewin)
            return

        if not validate_email(email):
            messagebox.showerror("Error", "Invalid email format", parent=updatewin)
            return

        try:
            # Check if student exists
            mycursor.execute("SELECT * FROM studentdata WHERE id = %s", (sid,))
            if mycursor.fetchone() is None:
                messagebox.showerror("Error", f"No student found with ID {sid}", parent=updatewin)
                return

            # Update the record
            query = """
                UPDATE studentdata 
                SET name=%s, gender=%s, dob=%s, mobile=%s, email=%s 
                WHERE id=%s
            """
            mycursor.execute(query, (name, gender, dob, mobile, email, sid))
            con.commit()

            messagebox.showinfo("Success", f"Student ID {sid} updated successfully!", parent=updatewin)

            # Clear fields
            idvalue.set("")
            namevalue.set("")
            gendervalue.set("")
            dobvalue.set("")
            mobilevalue.set("")
            emailvalue.set("")

            # Refresh Treeview
            showstudent()

        except Exception as e:
            messagebox.showerror("Error", f"Database error:\n{str(e)}", parent=updatewin)

    # ========== GUI Setup ==========
    updatewin = Toplevel(master=DataEntryFrame)
    updatewin.grab_set()
    updatewin.geometry("470x550+220+200")
    updatewin.title("Update Student")
    updatewin.config(bg="blue")
    updatewin.resizable(False, False)
    
    try:
        updatewin.iconbitmap("student.ico")
    except:
        pass

    # Variables
    idvalue = StringVar()
    namevalue = StringVar()
    gendervalue = StringVar()
    dobvalue = StringVar()
    mobilevalue = StringVar()
    emailvalue = StringVar()

    # ID field with Load button
    Label(updatewin, text="Enter Id :", bg="gold2", font=("times", 20, "bold"),
          relief=GROOVE, borderwidth=3, width=12, anchor="w").place(x=10, y=15)
    Entry(updatewin, font=("roman", 15, "bold"), bd=5, textvariable=idvalue).place(x=250, y=15)
    Button(updatewin, text="Load", font=("roman", 12, "bold"), width=8, bd=3,
           bg="orange", command=load_student).place(x=250, y=55)

    # Other fields
    fields = [
        ("Enter Name :", namevalue, 105, None),
        ("Enter Gender :", gendervalue, 165, ["Male", "Female", "Other"]),
        ("Enter D.O.B :", dobvalue, 225, None),
        ("Enter Mobile :", mobilevalue, 285, None),
        ("Enter Email :", emailvalue, 345, None),
    ]

    for label_text, var, y_pos, options in fields:
        Label(updatewin, text=label_text, bg="gold2", font=("times", 20, "bold"),
              relief=GROOVE, borderwidth=3, width=12, anchor="w").place(x=10, y=y_pos)
        
        if options:
            ttk.Combobox(updatewin, font=("roman", 15, "bold"), textvariable=var,
                        values=options, state="readonly").place(x=250, y=y_pos)
        else:
            Entry(updatewin, font=("roman", 15, "bold"), bd=5, textvariable=var).place(x=250, y=y_pos)

    # Update Button
    Button(updatewin, text="Update", font=("roman", 15, "bold"), width=20, bd=5,
           activebackground="blue", activeforeground="white", bg="green", 
           command=update).place(x=150, y=410)


def showstudent():
    """Display all students in the Treeview"""
    try:
        if mycursor is None:
            messagebox.showerror("Error", "Please connect to the database first")
            return
        
        query = "SELECT * FROM studentdata ORDER BY id"
        mycursor.execute(query)
        data = mycursor.fetchall()
        
        # Clear existing data
        framedata.delete(*framedata.get_children())
        
        # Insert all records
        for item in data:
            framedata.insert('', END, values=item)
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")


def exitstudent():
    """Exit the application"""
    res = messagebox.askyesnocancel("Exit Confirmation", "Do you want to exit?")
    if res == True:
        root.destroy()


def connectdb():
    """Connect to MySQL database"""
    def submitdb():
        global con, mycursor

        host = hostval.get().strip()
        user = userval.get().strip()
        password = passwordval.get()

        if not host or not user:
            messagebox.showerror("Input Error", "Host and User are required", parent=dbroot)
            return

        try:
            # Establish connection
            con = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                port=3306
            )
            mycursor = con.cursor()
            
            # Create database if not exists
            mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            mycursor.execute(f"USE {DB_NAME}")
            
            # Create table with consistent column names (lowercase)
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS studentdata (
                    id INT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    dob VARCHAR(15) NOT NULL,
                    gender VARCHAR(20) NOT NULL,
                    mobile VARCHAR(15) NOT NULL,
                    email VARCHAR(50) NOT NULL
                )
            """)
            con.commit()
            
            messagebox.showinfo("Success", "Database connected successfully!", parent=dbroot)
            
            # Auto-load existing data
            showstudent()
            
            dbroot.destroy()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Connection Failed", f"MySQL Error:\n{str(e)}", parent=dbroot)
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{str(e)}", parent=dbroot)

    # ========== GUI Setup ==========
    dbroot = Toplevel()
    dbroot.grab_set()
    dbroot.geometry("470x250+800+230")
    dbroot.resizable(False, False)
    dbroot.config(bg="blue")
    dbroot.title("Database Connection")
    
    try:
        dbroot.iconbitmap("student.ico")
    except:
        pass

    # Labels
    Label(dbroot, text="Enter Host:", bg="gold2", font=("times", 20, "bold"),
          relief=GROOVE, borderwidth=3, width=13, anchor="w").place(x=10, y=10)
    Label(dbroot, text="Enter User:", bg="gold2", font=("times", 20, "bold"),
          relief=GROOVE, borderwidth=3, width=13, anchor="w").place(x=10, y=70)
    Label(dbroot, text="Enter Password:", bg="gold2", font=("times", 20, "bold"),
          relief=GROOVE, borderwidth=3, width=13, anchor="w").place(x=10, y=130)

    # Entry Fields with default values
    hostval = StringVar(value="localhost")
    userval = StringVar(value="root")
    passwordval = StringVar()

    Entry(dbroot, font=("roman", 15, "bold"), bd=5, textvariable=hostval).place(x=250, y=10)
    Entry(dbroot, font=("roman", 15, "bold"), bd=5, textvariable=userval).place(x=250, y=70)
    Entry(dbroot, font=("roman", 15, "bold"), bd=5, textvariable=passwordval, show="*").place(x=250, y=130)

    # Submit Button
    Button(dbroot, text="Connect", font=("roman", 15, "bold"), width=20,
           activebackground="blue", activeforeground="white", bg="green", bd=5,
           command=submitdb).place(x=150, y=190)


# ============================================================================
# ANIMATION FUNCTIONS
# ============================================================================
def tick():
    """Update clock display"""
    time_string = time.strftime("%H:%M:%S")
    date_string = time.strftime("%d/%m/%Y")
    clock.config(text=f"Date: {date_string}\nTime: {time_string}")
    clock.after(200, tick)


def introlabelcolortick():
    """Animate slider label color"""
    clr = random.choice(ANIMATION_COLORS)
    sliderLabel.config(fg=clr)
    sliderLabel.after(200, introlabelcolortick)


def introlabeltick():
    """Animate slider label text"""
    global count, text
    if count >= len(head):
        count = 0
        text = ""
        sliderLabel.config(text=text)
    else:
        text = text + head[count]
        sliderLabel.config(text=text)
        count += 1
    sliderLabel.after(200, introlabeltick)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Initialize global variables
con = None
mycursor = None

# Create main window
root = Tk()
root.title("Student Management System")
root.config(bg='gold2')
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+200+50")
root.resizable(False, False)

try:
    root.iconbitmap("student.ico")
except:
    pass

# ========== Data Entry Frame (Left Panel) ==========
DataEntryFrame = Frame(root, bg="gold2", relief=GROOVE, borderwidth=5)
DataEntryFrame.place(x=10, y=80, width=350, height=600)

Label(DataEntryFrame, text="---------- Welcome ----------", width=25,
      font=("arial", 22, "italic bold"), bg="gold2").pack(side=TOP, expand=True)

# Buttons
buttons = [
    ("1. Add Student", addstudent),
    ("2. Search Student", searchstudent),
    ("3. Delete Student", deletestudent),
    ("4. Update Student", updatestudent),
    ("5. Show All", showstudent),
    ("6. Exit", exitstudent),
]

for text, command in buttons:
    Button(DataEntryFrame, text=text, width=20, font=("chiller", 18, "bold"),
           bd=6, bg="skyblue3", activebackground="blue", relief=RIDGE,
           activeforeground="white", command=command).pack(side=TOP, expand=True)


# ========== Show Data Frame (Right Panel) ==========
ShowDataFrame = Frame(root, bg="gold2", relief=GROOVE, borderwidth=5)
ShowDataFrame.place(x=400, y=80, width=750, height=600)

# Treeview styling
style = ttk.Style()
style.configure("Treeview.Heading", font=('roman', 12, 'bold'), foreground='blue')
style.configure("Treeview", font=('times', 12, 'bold'), foreground='black', background='cyan')

# Scrollbars
scroll_x = Scrollbar(ShowDataFrame, orient=HORIZONTAL)
scroll_y = Scrollbar(ShowDataFrame, orient=VERTICAL)

# Treeview
framedata = Treeview(ShowDataFrame,
                     columns=("Id", "Name", "Gender", "D.O.B", "Mobile.No", "Email"),
                     yscrollcommand=scroll_y.set,
                     xscrollcommand=scroll_x.set)

scroll_x.pack(side=BOTTOM, fill=X)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_x.config(command=framedata.xview)
scroll_y.config(command=framedata.yview)

# Configure columns
columns = ["Id", "Name", "Gender", "D.O.B", "Mobile.No", "Email"]
for col in columns:
    framedata.heading(col, text=col)
    framedata.column(col, width=150, anchor="center")

framedata["show"] = "headings"
framedata.pack(fill=BOTH, expand=1)


# ========== Top Section (Slider and Clock) ==========
head = "Welcome To Student Management System"
count = 0
text = ""

sliderLabel = Label(root, text=head, font=("chiller", 30, "italic bold"),
                    relief=GROOVE, borderwidth=5, width=35, bg="cyan")
sliderLabel.place(x=260, y=0)

clock = Label(root, font=("times", 14, "bold"), relief=RIDGE, borderwidth=5, bg="lawn green")
clock.place(x=0, y=0)

connectbutton = Button(root, text="Connect To Database", width=23,
                       font=("chiller", 19, "italic bold"), relief=RIDGE,
                       borderwidth=4, bg="green2", activebackground="blue",
                       activeforeground="white", command=connectdb)
connectbutton.place(x=930, y=0)

# Start animations
introlabeltick()
introlabelcolortick()
tick()

# Run application
root.mainloop()
