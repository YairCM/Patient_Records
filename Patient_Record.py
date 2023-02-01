from tkinter import *
from tkinter import ttk
import sqlite3

class MainWindow:
    
    # Assign the database file name to a variable
    db_name = 'database.db'

    def __init__(self, window):
        self.wind = window
        self.wind.title('Patient Records')

        # Create a container 
        frame = LabelFrame(self.wind, text="REGISTER A NEW PATIENT")
        frame.grid(row = 0, column=0, padx=20, pady=10, sticky=E)

        # Name Input
        Label(frame, text="Name:").grid(row=0, column=0, sticky=E)
        self.Name = Entry(frame)
        self.Name.grid(row=0, column=1, sticky=W)

        # Create a variable to store the selected gender value
        self.GenderValue = IntVar(self.wind)
        self.GenderValue.set('Female')

        # Gender Input
        Label(frame, text="Gender:").grid(row=1, column=0, sticky=E)
        self.Gender = OptionMenu(frame, self.GenderValue, 'Male', 'Female')
        self.Gender.grid(row=1, column=1, sticky=W+E)

        # Age Input
        Label(frame, text="Age:").grid(row=2, column=0, sticky=E)
        self.Age = Entry(frame)
        self.Age.grid(row=2, column=1, sticky=W)

        # Create a container
        buttons = LabelFrame(self.wind, text='BUTTONS')
        buttons.grid(row = 0, column=1, padx=20, pady=10, sticky=W)

        # New Button
        New = Button(buttons, text='New', width=10, command=self.add)
        New.grid(row=0, column=0, pady=5, sticky=W+E)

        # New Button
        Delete = Button(buttons, text='Delete', width=10, command=self.delete)
        Delete.grid(row=1, column=0, pady=5, sticky=W+E)

        # Output Messages 
        self.message = Label(text = 'Ready for a new record', fg = 'gray')
        self.message.grid(row = 3, sticky = W + E, columnspan=2)

        # Table
        columns = ['NAME','<4','5-9','10-14','15-19','20-24','25-44','45-49','50-59','60-64', '>65']
        self.tree = ttk.Treeview(height=15, columns=columns, show = 'tree headings')
        self.tree.grid(row = 4, columnspan=2)
        
        # Define headings
        self.tree.column('#0', width=100)
        for i in columns:
            self.tree.column('NAME', width=200)
            self.tree.column(i, width=55)
            self.tree.heading(i, text=i, anchor= CENTER)

        # Insert "Male" and "Female" as root elements
        self.tree.insert('', 'end', text='Male', iid = 'Male')
        self.tree.insert('', 'end', text='Female', iid = 'Female')

        # Filling the Rows
        self.get_data()


    # User Input Validation
    def validation(self):
        return len(self.Name.get()) != 0 and len(self.Age.get()) != 0    

    # Function to Execute Database Querys
    def run_query(self, query, parameters_value = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters_value)
            conn.commit()
        return result  

    # Add Patient into the database
    def add(self):
        if self.validation():
            #Insert values into records
            query = """
            INSERT INTO Records 
            VALUES(NULL,?,?,?)
            """
            parameters =  (self.Name.get(), self.Gender['text'], self.Age.get())
            self.run_query(query, parameters)    

            #Print message
            self.message['text'] = 'Successfully added: {}-year-old {} patient'.format(parameters[2], parameters[1])
            self.message.config(fg='blue')

            #Clean entries
            self.Name.delete(0, END)
            self.GenderValue.set('Female')
            self.Age.delete(0, END)
        
        else:
            #Print message
            self.message['text'] = 'Name and Age are required'
            self.message.config(fg='red')
        
        
        #Insert values into Table
        self.get_data()
        
    # Get Products from Database
    def get_data(self):
        Gender = ['Female', 'Male']
        # Clean table
        for parent in Gender:
                self.tree.delete(*self.tree.get_children(parent))

        # Getting data
        query = 'SELECT * FROM Records ORDER BY ID DESC'
        db_rows = self.run_query(query)
        db_rows = db_rows.fetchall()

        # Count age ranges
        self.age_range(db_rows)
        self.count_patient()

 
    def age_range(self, db_rows):
        # Define a dictionary that maps age ranges to numerical indices
        age_ranges = {
            "0-4": 0,
            "5-9": 1,
            "10-14": 2,
            "15-19": 3,
            "20-24": 4,
            "25-44": 5,
            "45-49": 6,
            "50-59": 7,
            "60-64": 8,
            "65+": 9
        }
        # Iterate through each row in the database
        for row in db_rows:
            # Determine the gender of the person in the current row
            gender = "Male" if row[2] == "Male" else "Female"
            age = row[3]
            # Iterate through the age ranges and their corresponding indices
            for age_range, index in age_ranges.items():
                if '+' in age_range:
                    age_range = int(age_range.split("+")[0]), 100
                else:
                    age_range = int(age_range.split("-")[0]), int(age_range.split("-")[1]) + 1
                # Check if the age in the current row falls within the current age range
                if age in range(age_range[0], age_range[1]):
                    # Insert the current row into the tree with the appropriate values
                    self.tree.insert(gender, 'end', values=(row[1],) + tuple(["" if i != index else age for i in range(len(age_ranges))]))
                    # Break out of the loop since we've found the correct age range
                    break

    
    def count_patient(self):
        self.count_columns()
        #MALE Patients counting
        query = """
        SELECT COUNT(NAME) 
        FROM Records 
        WHERE GENDER = 'Male'
        """
        count = self.run_query(query)
        count = count.fetchone()[0]
        self.count_male = count

        #Add counting in parent columns
        columns = ['{} Total Male Patients'.format(self.count_male), '{}'.format(self.male_range[0][0]), '{}'.format(self.male_range[1][0]),
                   '{}'.format(self.male_range[2][0]), '{}'.format(self.male_range[3][0]), '{}'.format(self.male_range[4][0]), 
                   '{}'.format(self.male_range[5][0]), '{}'.format(self.male_range[6][0]), '{}'.format(self.male_range[7][0]),
                   '{}'.format(self.male_range[8][0]), '{}'.format(self.male_range[9][0])]
        self.tree.item('Male', values=columns)

        #FEMALE Patients counting
        query = """
        SELECT COUNT(NAME) 
        FROM Records 
        WHERE GENDER = 'Female'
        """
        count = self.run_query(query)
        count = count.fetchone()[0]
        self.count_female = count

        #Add counting in parent columns
        columns = ['{} Total Female Patients'.format(self.count_female), '{}'.format(self.female_range[0][0]), '{}'.format(self.female_range[1][0]),
                   '{}'.format(self.female_range[2][0]), '{}'.format(self.female_range[3][0]), '{}'.format(self.female_range[4][0]), 
                   '{}'.format(self.female_range[5][0]), '{}'.format(self.female_range[6][0]), '{}'.format(self.female_range[7][0]),
                   '{}'.format(self.female_range[8][0]), '{}'.format(self.female_range[9][0])]
        self.tree.item('Female', values=columns)

    
    def count_columns(self):
        # Age Ranges Count
        query = """
        SELECT 
            CASE
                WHEN age BETWEEN 0 AND 4 THEN '0-4'
                WHEN age BETWEEN 5 AND 9 THEN '5-9'
                WHEN age BETWEEN 10 AND 14 THEN '10-14'
                WHEN age BETWEEN 15 AND 19 THEN '15-19'
                WHEN age BETWEEN 20 AND 24 THEN '20-24'
                WHEN age BETWEEN 25 AND 44 THEN '25-44'
                WHEN age BETWEEN 45 AND 49 THEN '45-49'
                WHEN age BETWEEN 50 AND 59 THEN '50-59'
                WHEN age BETWEEN 60 AND 64 THEN '60-64'
                WHEN age >= 65 THEN '65+'
            END AS age_range,
            GENDER,
            COUNT(*) as count
        FROM Records
        GROUP BY age_range, GENDER
        """
        count = self.run_query(query)
        count = count.fetchall()

        # Insert values in AgeRanges Table
        for age_range, gender, count in count:
            query = f"UPDATE AgeRanges SET COUNT_{gender} = {count} WHERE RANGES = '{age_range}'"
            self.run_query(query)
        
        self.parent()
    
    def parent(self):
        query = """
        SELECT COUNT_MALE FROM AgeRanges
        """
        male_range = self.run_query(query)
        male_range = male_range.fetchall()
        self.male_range = male_range


        query = """
        SELECT COUNT_FEMALE FROM AgeRanges
        """
        female_range = self.run_query(query)
        female_range = female_range.fetchall()
        self.female_range = female_range

    
    def delete (self):
        
        # Get the selected item
        selection = self.tree.selection()[0]
        if selection == 'Male' or selection == 'Female':
            #Print message
            self.message['text'] = 'This item cannot be deleted'
            self.message.config(fg='red')
        else:
            parameters = [value for value in self.tree.item(selection, "values") if value != '']


            self.message['text'] = 'Deleted Successfully: {}-year-old {} patient'.format(parameters[1], parameters[0])
            self.message.config(fg='blue')

        # Delete selected in Records Table
        query = """
        DELETE FROM Records 
        WHERE NAME = ? AND AGE = ?
        """
        self.run_query(query, (parameters[0], parameters[1]))

        # "Decrement count of female patients in AgeRanges table for non-zero values"
        query = """
        UPDATE AgeRanges
        SET COUNT_FEMALE = CASE
            WHEN COUNT_FEMALE = 1 THEN NULL
            ELSE COUNT_FEMALE - 1
        END
        WHERE COUNT_FEMALE > 0
        """
        self.run_query(query)

        # "Decrement count of male patients in AgeRanges table for non-zero values"
        query = """
        UPDATE AgeRanges
        SET COUNT_MALE = CASE
            WHEN COUNT_MALE = 1 THEN NULL
            ELSE COUNT_MALE - 1
        END
        WHERE COUNT_MALE > 0
        """
        self.run_query(query)

        self.get_data()
 

if __name__ == '__main__':
    window = Tk()
    application = MainWindow(window)
    window.mainloop()