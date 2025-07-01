def translate_field(field, convert):
    if convert == 'gujarati':
        if field.gujarati:
            return field.gujarati
        else:
            return field.name
    elif convert == 'hindi':
        if field.hindi:
            return field.hindi
        else:
            return field.name
    else:
        return field.name

def meal_type(field,convert,object):
    vals_gujarati={
    'early_morning_tea':'અરલી મોર્નિંગ ટી ',
    'breakfast':'બ્રેકફાસ્ટ',
    'brunch':'બ્રંચ',
    'mini_meals': 'મીની મિલ',
    'lunch':'લંચ',
    'hi-tea':'હી-ટી',
    'dinner':'ડિનર',
    'late_night_snacks':'લેટ નાઈટ સ્નેકસ  '}

    vals_hindi={
    'early_morning_tea':'अर्ली मॉर्निंग टी ',
    'breakfast':'ब्रेकफ़ास्ट ',
    'brunch':'ब्रंच',
    'mini_meals': 'मिनी मिल',
    'lunch':'लंच ',
    'hi-tea':'ही-टी ',
    'dinner':'डिनर ',
    'late_night_snacks':'लेट नाईट स्नेक्स '}

    if convert == 'gujarati':
        return vals_gujarati.get(field)
    elif convert == 'hindi':
        return vals_hindi.get(field)
    else:
        return dict(object._fields['meal_type'].selection).get(object.meal_type) 

def utensils_type(field,convert,object):
    vals_gujarati={
    'ground':'ગ્રાઉન્ડ ',
    'kitche':'કીટચન ',
    'disposable':'ડીસ્પોસેબલ ',
    'decoration':'ડેકોરેશન '}

    vals_hindi={
    'ground':'ग्राउंड ',
    'kitche':'किचन ',
    'disposable':'डिस्पोसेबल',
    'decoration':'डेकोरेशन'}

    if convert == 'gujarati':
        return vals_gujarati.get(field)
    elif convert == 'hindi':
        return vals_hindi.get(field)
    else:
        return dict(object._fields['utensils_type'].selection).get(object.utensils_type) 
    
def location_field(field,convert,object):
    vals_gujarati={
    'add_venue':'એડ વેનુ ',
    'add_godown':'એડ ગોડાઉન '}

    vals_hindi={
    'add_venue':'ऐड वेन्यू ',
    'add_godown':'ऐड गोडाउन '}

    if convert == 'gujarati':
        return vals_gujarati.get(field)
    elif convert == 'hindi':
        return vals_hindi.get(field)
    else:
        return dict(object._fields['location'].selection).get(object.location) 


