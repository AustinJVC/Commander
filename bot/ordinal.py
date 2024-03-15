def get_ordinal(n):
    if 10 <= n % 100 <= 13:
        return str(n) + "th"

    # Get the last digit
    last_digit = n % 10

    # Use appropriate suffix based on the last digit
    if last_digit == 1:
        return str(n) + "st"
    elif last_digit == 2:
        return str(n) + "nd"
    elif last_digit == 3:
        return str(n) + "rd"
    else:
        return str(n) + "th"
