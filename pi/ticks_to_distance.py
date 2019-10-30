# CICS 503 Fall 2019 DuckieTown Group 4
# Ticks to Distance
# Function: Covert the number of ticks counted by the wheel encoder into distance(cm)
# Last update: 10/25/2019


# input:
#		ticks : int, the number of ticks
# return:
#		distance traveled in centimeter(cm) 
def tick_to_centimeter(ticks):
        # based on the circumfrance of the wheel and the number of steps on encoder
        distance_per_tick = 22.0/26.0
        return ticks*distance_per_tick

# input:
#		left_ticks: int, the number of ticks from teh left wheel encoder
#		right_ticks: int, the number of ticks from teh right wheel encoder
# return:
#		the distances traveled by each wheel in centimeter(cm)
def get_distances(left_ticks, right_ticks):
        left_distance = tick_to_centimeter(left_ticks)
        right_distance = tick_to_centimeter(right_ticks)
        return left_distance, right_distance


