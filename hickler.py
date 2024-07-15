import hickle as hkl
entry_number = hkl.load('entrys')
entry_number = 0
hkl.dump(entry_number, 'entrys')

print(entry_number)