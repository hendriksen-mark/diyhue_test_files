test = 1

def rule():
    print("test")
    try: 
        if test == 1:
            return [False, x]
        elif test == 2:
            return [False, 0]
        elif test == 3:
            return [False, 0]
        elif test == 4:
            return [False, 0]
        elif test == 5:
            return [False, 0]
        elif test == 6:
            return [False, 0]
        elif test == 7:
            return [False, 0]
        elif test == 8:
            return [False, 0]
        elif test == 9:
            return [False, 0]
    except Exception as e:
        print(type(e).__name__, "–", e)
        return e
    
print(rule())
#rule()