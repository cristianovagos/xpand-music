from datetime import date

def calculateAge(birthDate):
    today = date.today()

    return today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))

def calculateDeathAge(birthDate, deathDate):
    if not birthDate:
        return None
    return deathDate.year - birthDate.year - ((deathDate.month, deathDate.day) < (birthDate.month, birthDate.day))