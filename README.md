# CSVStreamValidator
A CSV file validator written in Python.

# Key Features

### Field-level validation
- Declaratively apply any boolean validation function taking a field value as its single argument
- Apply multiple field validation rules to each field
### Row-level validation
- Declaratively apply any boolean validation function taking a row (a list of field values) as its single argument
- Apply multiple row validation rules to each row
### User-friendly error messages
- Pair a custom user message with each validation rule
### Accessible validation results
- Validation object generated for each row with attributes `line_number`, `fields`, `is_valid`, `error_messages`
### Streaming
- Suitable for very large csv files; yields one row validation object at a time
### Exhaustive validation testing
- Apply all validation rules to each row and field wherever possible 
- Multiple error messages per row
### Flexible csv file formats
- Specify any csv dialect and formatting paremeters supported by the Python `csv` module
### Flexible, explicit header processing
- Validate header, skip header, or no header

# Tutorial
In this tutorial we'll validate a sample csv file using `CSVStreamValidator`. We'll stop at each step to explain what's going on and describe how to use all of `CSVStreamValidator's` features. 

First, let's see what an example usage looks like from beginning to end.

#### test.csv
```
first_name,  last_name,   phone,  birthday,occupation
Sarah, Hardy, 019287124331, 11-25-1979, plumber
Dalia,Wright,5126521872, 1951,
Raju,Mehashi,5112987328, 08-31-1994, artist
Mahelia,   Sanders,4018889151,08-22-1991,nurse
Mike, Simpson, 5126218721, 02-11-1952, engineer
Pete,,,,receptionist
```

#### code.py
```
from datetime import datetime, date
import io

from CSVStreamValidator import CSVStreamValidator, RowStatus 
    
MAX_ENGINEER_AGE = 30

def is_valid_phone(phone):
    if len(phone) == 10 and phone.isdigit():
        return True
    return False

def is_valid_job_length(occupation):
    if len(occupation) < 10:
        return True
    return False   

def is_valid_job_title(occupation):
    if occupation in ['artist', 'plumber', 'nurse', 'engineer']:
        return True
    return False

def is_valid_birthday(birthday):
    try:
        datetime.strptime(birthday, '%m-%d-%Y')
    except ValueError:
        return False
    return True

def is_employee_on_roster(row):
    full_name = '{} {}'.format(row[0], row[1])
    roster = ['Sandra Ornila', 'Sarah Hardy', 'Mike Simpson', 'Pete Ott', 'Mahelia Sanders', 'Vanessa Ivey']
    if full_name in roster:
        return True
    return False

def get_age(birthday):
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

def is_valid_engineer_age(row):
    if (row[4] == 'engineer') and is_valid_birthday(row[3]) and \
       (get_age(datetime.strptime(row[3], '%m-%d-%Y')) > MAX_ENGINEER_AGE):
        return False
    return True        

field_specs = [
    ('name', True, []),
    ('last name', True, []),
    ('phone', True, [(is_valid_phone, 'Phone number must be 10 digits')]),
    ('brithday', True, [(is_valid_birthday, 'Birthday must be a valid date of the form \'MM-DD-YYYY\'')]),
    ('occupation', True, [(is_valid_job_length, 'Occupation must be less than 10 characters'),
                          (is_valid_job_title, "Occupation must be 'artist', 'plumber', 'nurse' or 'engineer'")])]
row_validations = [
    (is_employee_on_roster, 'Employee not found on roster'),
    (is_valid_engineer_age, 'Why is this engineer not a manager? No engineers over 30 allowed.')]
    
with io.open('test.csv', newline='') as csvfile:
    validator = CSVStreamValidator(csvfile, field_specs, row_validations=row_validations)
    validator.skip_header()
    for row in validator.validate_rows():
        if row.is_valid:
            print('Valid row. Line {}: {}'.format(row.line_number, row.fields))
        else:
            print('Invalid row. Line {}: {}'.format(row.line_number, row.fields))
            for error in row.error_messages:
                print('\t{}'.format(error))
```

#### Output

```
Invalid row. Line 2: ['Sarah', 'Hardy', '019287124331', '11-25-1979', 'plumber']
	Phone number must be 10 digits
Invalid row. Line 3: ['Dalia', 'Wright', '5126521872', '1951', '']
	Birthday must be a valid date of the form 'MM-DD-YYYY'
	Missing 'occupation' value
	Employee not found on roster
Invalid row. Line 4: ['Raju', 'Mehashi', '5112987328', '08-31-1994', 'artist']
	Employee not found on roster
Valid row. Line 5: ['Mahelia', 'Sanders', '4018889151', '08-22-1991', 'nurse']
Invalid row. Line 6: ['Mike', 'Simpson', '5126218721', '02-11-1952', 'engineer']
	Why is this engineer not a manager? No engineers over 30 allowed.
Invalid row. Line 7: ['Pete', '', '', '', 'receptionist']
	Missing 'last name' value
	Missing 'phone' value
	Missing 'brithday' value
	Occupation must be less than 10 characters
	Occupation must be 'artist', 'plumber', 'nurse' or 'engineer'
	Employee not found on roster
  ```
