# import random
# import matplotlib.pyplot as plt

# # Set the arrival rate (passengers per hour)
# arrival_rate = 20

# # Set the rate parameter for the Poisson process
# lambda_value = arrival_rate / 3600  # Convert arrival rate to passengers per second

# # Simulation for 1 hour (3600 seconds)
# total_time = 3600
# arrival_times = []
# current_time = 0 

# # Generate random inter-arrival times using exponential distribution
# while current_time < total_time:
#     inter_arrival_time = random.expovariate(lambda_value)
#     current_time += inter_arrival_time

#     # If the next arrival time is within the simulation period, add it to the list
#     if current_time < total_time:
#         arrival_times.append(int(current_time))

# print(arrival_times)

# # Plot the Poisson process
# # plt.step(arrival_times, range(1, len(arrival_times) + 1), where='post')
# # plt.xlabel('Time (seconds)')
# # plt.ylabel('Number of passengers')
# # plt.title('Simulated Passenger Arrival at Bus Stop')
# # plt.show()

# # print('1/3600: ', 1/3600)
# # print(int('-410464251'))

# test = 'hello'
# s = test.split('.')
# print(s)
# print(s[0])
# # print(s[1])


# l = ['1','1','2','4','4','4','5','5','6','7','7','7','7']

# dups = {x:l.count(x) for x in l if l.count(x) > 1}
# print(dups)
# for key in dups.keys():
#     i = l.index(key)
#     for z in range(dups[key]):
#         l[i+z] = l[i+z] + '.' + str(z)
#     pass

# # print(l.index('7'))
# # l[l.index('7')+1] = '10'
# print(l)

# print([str(0)])

# print([int('0')])

l = []
l += [1,0]
print(l)
l += [22]
print(l)