import os
import psutil

"""Funksjoner for testing av applikasjon"""

def memory_info():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss/10**6

def print_memory_info():
    print()
    print("************************")
    print("Minnebruk: {} MB".format(memory_info()))
    print("************************")
    print()



if __name__ == "__main__":
    import xlrd
    import os.path

    wb = xlrd.open_workbook("test.xls")
    print(wb.sheet_names())
    sh = wb.sheet_by_index(7)
    with open("kilometrering.txt", "w") as my_file:
        rows = range(117,201)
        cols = [0, 3, 4]
        my_file.write("kilometer = { ")
        for row in rows:

            my_file.write("\n\t\t\t")
            for col in cols:
                cell = sh.cell(row, col).value
                if col == 0:
                    my_file.write("\"{}\": ".format(cell))
                elif col == 3:
                    my_file.write("[{}, ".format(cell))
                elif col == 4:
                    my_file.write("{}], ".format(cell))

        my_file.write(" }")