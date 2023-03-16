import joblib

file = joblib.load('address_sliced.jbl')
# file = {1: [3], 2: [5, 3], 4: [3]}
count = 0

print('Length after:', len(file))

# temp = {val : key for key, val in file.items()}
# res = {val : key for key, val in temp.items()}

temp = []
res = dict()
for key, val in file.items():
    if val not in temp:
        temp.append(val)
        res[key] = val

print('Length after:', len(res))

joblib.dump(res,'address_sliced_no_duplicates.jbl')