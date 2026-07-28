import time 
from itertools import cycle 
name= input("enter your name :")
user_input= ("are you ('ready or not ready')? ")
if user_input== "not ready" :
    print (" no worries ! come back when you are ready ")
else:
    start = [
        ('on your keyboard:', 2),
        ('get set:', 0.5),
        ('go', 2)
        ]
    for message, delay in start:
        print(message)
        time.sleep(delay)
        start_time =time.time()
        typed_text = input ("type A to Z:")
        end_time= time.time()
        time_taken =end_time - start_time
        print(f"\n{name}, you completed it in {time_taken:.2f} seconds!")

        


 

 