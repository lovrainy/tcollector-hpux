import time
def input_log():
    i = 0
    while True:
        i += 1
        date = '2019-11-%d'%i
        with open('/home/weblogic/tcollector/tc_web_app.log', 'a') as f:
            f.write(date+'this is a test input\n')
        time.sleep(0.1)


if __name__ == "__main__":
    input_log()

