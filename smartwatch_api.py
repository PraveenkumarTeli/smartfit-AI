import random
current_heart_rate=90
def get_heart_rate():
    global current_heart_rate
    change= random.randint(-3,3)
    current_heart_rate=current_heart_rate+change
    if current_heart_rate< 60 :
        current_heart_rate=60
    if current_heart_rate > 160:
        current_heart_rate=160
    return current_heart_rate
