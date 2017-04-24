# CSVStreamValidator
A CSV file validator written in Python.

## Key Features

### Field-level validation: 
- Apply any boolean validation function taking a field value as its single argument
- Apply multiple field validation rules to each field
### Row-level validation: 
- Apply any boolean validation function taking a row (a list of field values) as its single argument
- Apply multiple row validation rules to each row
### User-friendly error messages: 
- Pair a custom user message with each validation rule
### Accessible validation results: 
- Validation object generated for each row with attributes `line_number`, `fields`, `is_valid`, `error_messages`
### Streaming:
- Suitable for very large csv files; yields one row validation object at a time
### Exhaustive validation testing: 
- Apply all validation rules to each row and field wherever possible 
- Multiple error messages per row
### Flexible csv file formats:
- Specify any csv dialect and formatting paremeters supported by the Python `csv` module
### Flexible, explicit header processing: 
- Validate header, skip header, or no header
