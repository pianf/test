

s = input('Write word here:')

space = "' '"


if s.endswith(space):
    s = s.rstrip()
    # word = s[:-len(space)]
# #take the word 'name' out of the list
# for i in range(len(s) - 1):
#     s[i] = s[i + 1] #0 becomes 1, 1 becomes 2, 2 becomes 3
# s = s[:len(s) - 1]

print(s)