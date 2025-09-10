from planificador.exceptions.validation import validate_email_format, FormatValidationError

email = 'invalid-email'
print(f'Testing email: {email}')
try:
    validate_email_format(email)
    print('No exception raised!')
except FormatValidationError as e:
    print(f'Exception raised: {e}')
    print(f'Details: {e.details}')
    print(f'Type: {type(e)}')
except Exception as e:
    print(f'Other exception: {e}')
    print(f'Type: {type(e)}')