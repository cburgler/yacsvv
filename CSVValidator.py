'''
CSVValidator.py - Define the CSVValidator class used to validate csv files.
'''
from collections import namedtuple
import csv
import io

FieldSpec = namedtuple('FieldSpec', 'name is_required validation_rules')
RowStatus = namedtuple('RowStatus', 'line_number fields is_valid error_messages')


class CSVValidator:
    '''
    CSVValidator - Orchestrate csv file validation.
    
    Define a public method 'validate_rows' which yields a RowStatus validation object for each data row in the csv file.
    
    Also define three public header methods:
        validate_header - Return a RowStatus validation object for the header row.
        skip_header - Skip the header row.
        no_header - Specify that the csv file does not have a header row.
    Exactly one of these header methods must be called exactly once prior to calling 'validate_rows', subject to 
    a RuntimeError.
    '''
    
    def __init__(self, csv_file, field_specs, row_validations=[], strip_whitespace=True, allow_empty_rows=True, 
                 header_fields=[], **kwargs):
        '''
        csv_file - Object to be validated. This parameter is used as the 'csvfile' argument to 'csv.reader()'. 
            As per the Python docs: 
                "[csv_file] can be any object which supports the iterator protocol and returns a string each time its
                __next__ method is called - file objects and list objects are both suitable. If [csv_file] is a file
                object, it should be opened with newline=''." 
            'newline' is not a parameter of the builtin 'open()' function in Python 2. So use 'io.open()' 
            with the newline='' argument when creating a file object in Python 2 (2.6+).
        field_specs - List of (name, is_required, validation_rules) tuples that specify the validation criteria 
            for each field. The order of each tuple is the order of the fields in the file. Tuple items are:
            name - user-friendly field name used in error reporting, may be different than the field header value
            is_required - if True, a row is invalid if the field does not have a value
            validation_rules - list of (field_validation_function, error_message) tuples, where
                field_validation_function - a function that accepts the field value as its only argument; a row is
                    invalid if field_validation_function returns False
                error_message - user-friendly description of the field validation rule and/or error condition 
        row_validations - List of (row_validation_function, error_message) tuples, where
            row_validation_function - a function that accepts the row (a list of field values) as its only 
                argument; a row is invalid if row_validation_function returns False
            error_message - user-friendly description of the row validation rule and/or error condition 
        strip_whitespace - if True, leading and trailing whitespace is removed from all field and header values
        allow_empty_rows - if True, a row with no fields (ie a line containing only a new line character) is valid.
            Otherwise, a row with no fields is invalid.
        header_fields - List of valid header values. Only used by CSVValidator.validate_header().
        kwargs - Any keyword arguments supported by 'csv.reader'
        
        Exception raised
            csv.Error
        '''
        self._line_number = 0
        self._field_specs = [FieldSpec(*field_spec) for field_spec in field_specs]
        self._expected_field_count = len(self._field_specs)
        self._row_validations = row_validations
        self._strip_whitespace = strip_whitespace
        self._allow_empty_rows = allow_empty_rows
        self._header_fields = header_fields
        self._header_processed = False
        
        self._csv_reader = csv.reader(csv_file, **kwargs) 
            
    def _validate_field_count(self, row):
        '''
        _validate_field_count - Return (True, '') if the given row has the expected number of fields.
                                Return (False, error_message) otherwise.
        '''
        row_field_count = len(row)
        if row_field_count != self._expected_field_count:
            return (False, 'Unexpected number of fields: Expected {}, Got {}'.format(self._expected_field_count, row_field_count))
        return (True, '')  
            
    def _validate_row(self, row):
        '''
        _validate_row - Return a RowStatus object for the given row. 
        '''
        if (not row) and self._allow_empty_rows:
            return RowStatus(self._line_number, row, True, [])
        valid_field_count, error_message = self._validate_field_count(row)
        if not valid_field_count:
            return RowStatus(self._line_number, row, False, [error_message])
        row_errors = []
        for (field_spec, value) in zip(self._field_specs, row):
            if field_spec.is_required and (not value):
                row_errors.append('Missing \'{}\' value'.format(field_spec.name))
            elif value and field_spec.validation_rules:
                row_errors.extend(self._get_field_validation_errors(field_spec.validation_rules, value))
        row_errors.extend(self._get_row_validation_errors(row))
        if row_errors:
            return RowStatus(self._line_number, row, False, row_errors)
        else:
            return RowStatus(self._line_number, row, True, [])
            
    def _verify_header_processing_status(self):
        '''
        _verify_header_processing_status - Raise a RunTimeError if the header has not yet been processed by a
            header method.
        '''
        if not self._header_processed:
            raise RuntimeError('One of \'validate_header\', \'skip_header\', or \'no_header\' must be called ' +\
                               'prior to data row validation.')
    
    def validate_rows(self):
        '''
        validate_rows - Yield a RowStatus validation object for each data row in the csv file. A RowStatus object has 
            the following attributes: 
            line_number - the position of the given row in the csv file
            fields - list of field values for the given row
            is_valid - True if the given row is valid, False otherwise
            error_messages - list of user-friendly descriptions for each unmet validation criterion; 
                non-empty list iff (is_valid == False), empty list iff (is_valid == True)
                
        Exceptions raised
            RuntimeError - Raised if a header method has not yet been called
            csv.Error
        '''
        self._verify_header_processing_status()
        for row in self._csv_reader:
            self._line_number += 1
            if self._strip_whitespace:
                row = [r.strip() for r in row]
            yield self._validate_row(row)
    
    def _set_header_process_status(self):
        if self._header_processed:
            raise RuntimeError('Only one header method may be called per csv file.')
        else:
            self._header_processed = True
                    
    def no_header(self):
        '''
        no_header - Specify that this csv file does not have a header row.
        
        Exception raised
            RuntimeError - Raised if a header method has already been called.
        '''
        self._set_header_process_status()
              
    def skip_header(self):
        '''
        skip_header - Skip the header row. The header row is the first row.
        
        Exceptions raised 
            RuntimeError - Raised if a header method has already been called.
            csv.Error
        '''
        self._set_header_process_status()
        next(self._csv_reader)
        self._line_number += 1
              
    def validate_header(self):
        '''
        validate_header - Return a RowStatus object for the header row. The header row is the first row. 
            A header RowStatus object has the following attributes: 
            line_number - always 1
            fields - list of header row values
            is_valid - True if the header is valid, False otherwise
            error_message - 'Unexpected headers:\n\tExpected: {}\n\tGot: {}' iff (is_valid == False), '' iff (is_valid == True)
            
        Exceptions raised 
            RuntimeError - Raised if a header method has already been called.
            csv.Error
        '''
        self._set_header_process_status()
        header = next(self._csv_reader)
        self._line_number += 1
        if self._strip_whitespace:
            header = [h.strip() for h in header]
        if header != self._header_fields:
            error_message = 'Unexpected headers:\n\tExpected: {}\n\tGot: {}'.format(self._header_fields, header)
            return RowStatus(self._line_number, header, False, error_message)
        return RowStatus(self._line_number, header, True, '')
    
    def _get_field_validation_errors(self, field_validations, value):
        return [error_message for (validator, error_message) in field_validations if not validator(value)] 
    
    def _get_row_validation_errors(self, row):
        return [error_message for (validator, error_message) in self._row_validations if not validator(row)]                
                
