import subprocess

def main():
    process1 = subprocess.Popen("python  -u main2.py", shell=False, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)


    #print process1.communicate()[0]

    while True:
        line = process1.stdout.readline()
        if not line:
            break
        print (line)

if __name__ == '__main__':
    main()