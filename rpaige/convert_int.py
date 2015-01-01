def sum(num_1,num_2):
    num1_int = convert_integer(num_1)
    num2_int = convert_integer(num_2)
    result = num_1_int + num2_int
    return result

def convert_integer(num_string):
    converted_int = int(num_string)
    return converted_int
answer = sum("1","2")
    
    