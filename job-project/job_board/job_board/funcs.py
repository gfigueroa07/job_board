# helper functions to avoid reusing code


def review_sanitization(num):
    if num < 1 or num > 5:
        print('Please enter a number betwewen 1-5')
    else:
        pass