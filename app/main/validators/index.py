import re

def is_contains_only_alphabetic_chars(value):
    pattern = r"^[A-Za-z\s]+$"
    regex = re.compile(pattern)
    result = regex.fullmatch(value)
    return result is not None


def is_valid_email_pattern(email):
    pattern = "^[a-zA-Z0-9._-]+@{1}[a-zA-Z0-9.-]+$"
    regex = re.compile(pattern)
    result = regex.fullmatch(email)
    return result is not None


def is_empty(value):
    return value is None or value.strip() == ""


def validate_create_record_form(form_data):
    errors = {}

    if not is_contains_only_alphabetic_chars(form_data.get("requestor_name")):
        errors["requestor_name"] = "Please enter a valid full name. It should only contain alphabetic characters"
    if not is_valid_email_pattern(form_data.get("requestor_email")):
        errors["requestor_email"] = "Please enter a valid email address"
    if is_empty(form_data.get("dns_record")):
        errors["dns_record"] = "Please enter a valid DNS record"
        
    return errors
