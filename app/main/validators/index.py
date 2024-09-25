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

def validate_domain(domain, hosted_zones):
    for hosted_zone in hosted_zones:
        if domain.endswith(hosted_zone):
            return True
        
    return False


def validate_create_record_form(form_data, hosted_zones):
    errors = {}
    dns_record = form_data.get("dns_record")

    if not is_contains_only_alphabetic_chars(form_data.get("requestor_name")):
        errors["requestor_name"] = "Please enter a valid full name. It should only contain alphabetic characters"
    if not is_valid_email_pattern(form_data.get("requestor_email")):
        errors["requestor_email"] = "Please enter a valid email address"
# 
    if is_empty(dns_record):
        errors["dns_record"] = "Please enter a domain name"
    elif not validate_domain(dns_record, hosted_zones):
        errors["dns_record"] = f"Please enter a valid domain name: {dns_record} does not belong to an existing hosted zone."

    return errors
