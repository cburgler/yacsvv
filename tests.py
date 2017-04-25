from datetime import datetime, date
import io

from CSVValidator import CSVValidator, RowStatus 


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
    roster = ['Sandra Ornila', 'Sarah Hardy', 'Mike Sanderson', 'Pete Ott', 'Mahelia Sanders', 'Vanessa Ivey']
    if full_name in roster:
        return True
    return False

def get_age(birthday):
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

def is_valid_engineer_birthday(row):
    if (row[4] == 'engineer') and is_valid_birthday(row[3]) and ((datetime.strptime(row[3], '%m-%d-%Y')).month != 4):
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
    (is_valid_engineer_birthday, 'Engineers must be born in April')]
           
no_errors = True
with io.open('test.csv', newline='') as csvfile:
    validator = CSVValidator(csvfile, field_specs, delimiter=',', row_validations=row_validations, 
                    strip_whitespace=True, header_fields=['first_name', 'last_name', 'phone', 'birthday', 'occupation'])
    expected_header_rowstatus = RowStatus(line_number=1, fields=['first_name', 'last_name', 'phone', 'birthday', 'occupation'], 
                                          is_valid=True, error_messages='')
    header = validator.validate_header()
    if header != expected_header_rowstatus:
        no_errors = False
        print('Unexpected validate_header:\n\tExpected: {}\n\tGot: {}'.format(expected_header_rowstatus, header))

    expected_data_rowstatus = \
        [RowStatus(line_number=2, fields=['Mike', 'Simpson', '5126218721', '02-11-1952', 'engineer'], is_valid=False, error_messages=['Employee not found on roster', 'Engineers must be born in April']),
         RowStatus(line_number=3, fields=['Sarah', 'Hardy', '019287124331', '11-25-1979', 'plumber'], is_valid=False, error_messages=['Phone number must be 10 digits']),
         RowStatus(line_number=4, fields=[], is_valid=True, error_messages=[]),
         RowStatus(line_number=5, fields=[''], is_valid=False, error_messages=['Unexpected number of fields: Expected 5, Got 1']),
         RowStatus(line_number=6, fields=['Dalia', 'Wright', '51265218721', 'teacher'], is_valid=False, error_messages=['Unexpected number of fields: Expected 5, Got 4']),
         RowStatus(line_number=7, fields=['Raju', 'Mehashi', '5112987328', 'April 1st', 'artist'], is_valid=False, error_messages=["Birthday must be a valid date of the form 'MM-DD-YYYY'", 'Employee not found on roster']),
         RowStatus(line_number=8, fields=['Mahelia', 'Sanders', '4018889151', '08-22-1991', 'nurse'], is_valid=True, error_messages=[]),
         RowStatus(line_number=9, fields=['Pete', '', '', '', 'receptionist'], is_valid=False, error_messages=["Missing 'last name' value", "Missing 'phone' value", "Missing 'brithday' value", 'Occupation must be less than 10 characters', "Occupation must be 'artist', 'plumber', 'nurse' or 'engineer'", 'Employee not found on roster'])]
         
    for (row, expected_row_rowstatus) in zip(validator.validate_rows(), expected_data_rowstatus):
        if row != expected_row_rowstatus:
            no_errors = False
            print('Unexpected validate_row:\n\tExpected: {}\n\tGot: {}'.format(expected_row_rowstatus, row))
            
    if no_errors:
        print('All tests passed!')