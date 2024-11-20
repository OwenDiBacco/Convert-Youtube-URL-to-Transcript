# chunking the array to control the concurrency 
playlists = np.array(playlists) # creates a numpy array
number_of_arrays = len(playlists) / 5 # replace denominator with the number of index you want per array -1
array_of_playlists = np.array_split(playlists, number_of_arrays)
for playlist in array_of_playlists:
    print(playlist)