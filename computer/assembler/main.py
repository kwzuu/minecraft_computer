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
            encoded = listings.encode(line)
            hi = encoded // 64
            lo = encoded % 64
            print("%04o" % encoded, f"({hi}, {lo})")
