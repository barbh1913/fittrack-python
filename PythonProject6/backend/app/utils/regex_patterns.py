"""
Regex patterns for input validation.
Centralized location for all regex patterns used across the application.
"""
import re

# Email validation: standard email format
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Phone validation: Israeli format (0X-XXXXXXX)
PHONE_PATTERN_IL = re.compile(r'^0[2-9]\d{7,8}$')

# Phone validation: International format
PHONE_PATTERN_INTL = re.compile(r'^\+?[1-9]\d{1,14}$')

# Member ID validation: exactly 9 digits
ID_PATTERN = re.compile(r'^\d{9}$')

# Full name validation: 2-100 characters, letters and spaces only
FULLNAME_PATTERN = re.compile(r'^[a-zA-Z\s]{2,100}$')

# Password validation: strong password requirements
# - At least one lowercase letter
# - At least one uppercase letter
# - At least one digit
# - At least one special character (@$!%*?&)
# - Minimum 8 characters
PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
