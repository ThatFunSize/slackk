import pickle
with open('objs.pkl') as f:  # Python 3: open(..., 'rb')
    entry_number = pickle.load(f)
print(entry_number)
entry_number += 1
print(entry_number)
entry_number = 0
with open('objs.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
	pickle.dump(entry_number, f)