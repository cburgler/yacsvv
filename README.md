# yacsvv
A CSV validator written in Python.

# Key Features

### Fully customizable field-level validation
- Declaratively apply any single-argument (`field_value`) boolean validation function to a field
- Apply multiple field validation rules to each field
### Fully customizable row-level validation
- Declaratively apply any single-argument (`row_value`) boolean validation function to a row
- Apply multiple row validation rules to each row
### User-friendly error messages
- Pair a custom user message with each validation rule
### Accessible validation results
- Receive one validation object for each row of data. Each validation object has the following attributes: `line_number`, `fields`, `is_valid`, `error_messages`
### Streaming
- Suitable for very large csv files. `yacsvv` lazily validates one row at a time so memory is not an issue.
### Exhaustive validation testing
- Apply all validation rules to each row and field wherever possible 
- Multiple error messages per row and field
### Flexible csv file formats
- Specify any csv dialect and formatting parameters supported by the Python `csv` module
### Flexible, explicit header processing
- Validate header, skip header, or no header
### Compatible with both Python 2 & 3

# Example Usage
Let's see what an example usage looks like from beginning to end.

#### sample.csv
```
first_name,  last_name,   phone,  birthday,occupation
Sarah, Hardy, 019287124331, 11-25-1979, plumber
Dalia,Wright,5126521872, 1951,
Raju,Mehashi,08-31-1994, artist
Mahelia,   Sanders,4018889151,08-22-1991,nurse
Mike, Simpson, 5126218721, 02-11-1952, engineer
Pete,  Ott  ,,,receptionist
```

#### validation_functions.py
```
from datetime import datetime

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

def is_valid_engineer_birthday(row):
    if (row[4] == 'engineer') and is_valid_birthday(row[3]) and ((datetime.strptime(row[3], '%m-%d-%Y')).month != 4):
        return False
    return True
```

#### myvalidator.py
```
import io
from CSVValidator import CSVValidator
from validation_functions import (is_valid_phone, is_valid_birthday, is_valid_job_length, is_valid_job_title,
                                  is_employee_on_roster, is_valid_engineer_birthday)

# Define field specs. Each field spec is a tuple of the form (
#    name - user-friendly field name used in error reporting, may be different than the field header value
#    is_required - if True, a row is invalid if the field does not have a value
#    list of (field validation function, error message) tuples, where
#        field_validation_function - a function that accepts the field value as its only argument; a row is
#            invalid if field_validation_function returns False
#        error_message - user-friendly description of the field validation rule and/or error condition 
#    )
# The order of each field spec tuple is the order of the fields in the csv file.
field_specs = [
    ('first name', True, []),
    ('last name', True, []),
    ('phone #', True, [(is_valid_phone, 'Phone # must be 10 digits')]),
    ('birthday', True, [(is_valid_birthday, 'Birthday must be a valid date of the form \'MM-DD-YYYY\'')]),
    ('occupation', True, [(is_valid_job_length, 'Occupation must be less than 10 characters'),
                          (is_valid_job_title, "Occupation must be 'artist', 'plumber', 'nurse' or 'engineer'")])
    ]
    
# Define row specs. Each row spec is a tuple of the form (
#     row_validation_function - a function that accepts the row (a list of field values) as its only 
#         argument; a row is invalid if row_validation_function returns False
#     error_message - user-friendly description of the row validation rule and/or error condition 
#     )
row_validations = [
    (is_employee_on_roster, 'Employee not found on roster'),
    (is_valid_engineer_birthday, 'Engineers must be born in April')
    ]

# validate 'sample.csv'
with io.open('sample.csv', newline='') as csvfile:
    validator = CSVValidator(csvfile, field_specs, row_validations=row_validations)
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
	Phone # must be 10 digits
Invalid row. Line 3: ['Dalia', 'Wright', '5126521872', '1951', '']
	Birthday must be a valid date of the form 'MM-DD-YYYY'
	Missing 'occupation' value
	Employee not found on roster
Invalid row. Line 4: ['Raju', 'Mehashi', '08-31-1994', 'artist']
	Unexpected number of fields: Expected 5, Got 4
Valid row. Line 5: ['Mahelia', 'Sanders', '4018889151', '08-22-1991', 'nurse']
Invalid row. Line 6: ['Mike', 'Simpson', '5126218721', '02-11-1952', 'engineer']
	Engineers must be born in April
Invalid row. Line 7: ['Pete', 'Ott', '', '', 'receptionist']
	Missing 'phone #' value
	Missing 'birthday' value
	Occupation must be less than 10 characters
	Occupation must be 'artist', 'plumber', 'nurse' or 'engineer'
  ```
