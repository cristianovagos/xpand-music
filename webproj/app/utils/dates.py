from datetime import date

def calculateAge(birthDate):
    today = date.today()

    return today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))