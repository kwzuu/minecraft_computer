from sys import argv

from computer.assembler import listings


def main():
    if len(argv) != 2:
        print(argv)
        print("please provide a file!")
        exit()

    with open(argv[1]) as f:
        lines = f.readlines()
        for line in lines:
            print("%04o" % listings.encode(line))
