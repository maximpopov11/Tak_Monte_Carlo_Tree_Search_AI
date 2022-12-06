import os

black = 0
white = 0
for i in range(49):
    with open(f'Game {i}.txt', 'rb') as f:
        try:  # catch OSError in case of a one line file 
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
        if "Winner: Black" in last_line:
            black+=1
        else:
            white+=1
print(f"black: {black} | white: {white}")
