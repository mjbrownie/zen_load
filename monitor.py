#!/usr/bin/python
import subprocess
import datetime
import sys

#TODO add an override option
#NOTE Please check this command thoroughly to ensure you are comfortable with it
# Command is in three sections
# 1. check of load avg in /proc/loadavg
# 2. check of memory in /proc/meminfo
# 3. check of df mount on / 
# result on a linux box should be
#
# 0.54 0.70 0.56 357260 73%
DEFAULT_COMAND = r"echo \`cut -d' ' -f1-3 /proc/loadavg\` \`grep MemFree /proc/meminfo|awk '{print \$2}'\` \`df | grep /$|awk '{print \$5}'\`"
DEFAULT_PARSE = ""

DISABLE_THROWS = False
EXTRA_ZEN = True
EXTRA_EXTRA_ZEN = True

def main():
    try:
        with open('.zen_load/servers.txt' ,'r') as fp:
            servers = [s.rstrip().split(':') for s in fp.readlines()]
    except:
        print "No servers defined: " + datetime.datetime.now().strftime('%d/%m %H:%M')
        sys.exit()

    buttons = []

    for s in servers:
        command = 'ssh %s "%s"' % (s[1],DEFAULT_COMAND)
        p = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE)
        out,err = p.communicate()

        vals = out.split(" ")

        try:
            l1, l2, l3, mem, disk = vals


            colors = dict(
                    l1 = str(load_check(l1)),
                    l2 = str(load_check(l2)),
                    l3 = str(load_check(l3)),
                    mem = str(mem_check(mem)),
                    disk = str(disk).rstrip(),
                    name = s[0],
                    login = s[1],
                    )

            display = "%(name)s: %(l1)s %(l2)s %(l3)s %(mem)s %(disk)s" % colors
            #TODO allow for more shells
            if EXTRA_ZEN:
                if not 'green' in display and not 'red' in display \
                        and not 'yellow' in display:
                    #display = "%(name)s :-) " % colors
                    display = "%(name)s" % colors
                elif EXTRA_EXTRA_ZEN and 'green' in display \
                        and not 'red' in display:
                    c = 'yellow' in display and 'yellow' or 'green'
                    #display = "%s ^fg(%s):-(^fg() " % (s[0],c)
                    display = "%s ^fg(%s):|^fg() " % (s[0],c)

            shell = 'urxvt -title "%(name)s" -e ssh %(login)s' % colors

            button = "^ca(1,%s) %s ^ca()" % (shell,display)

            buttons.append(
                    button
                    )

        except Exception:
            shell = 'urxvt -title "%s" -e ssh %s' % tuple(s)
            buttons.append("^ca(1,%s) no %s! ^ca()" % (shell, s[0]))


    print " | ".join(buttons)+ " | " + datetime.datetime.now().strftime('%d/%m %H:%M')


def load_check(i):
    i = float(i)
    if i < 1:
        return i
    if i < 2:
        return "^fg(green)%s^fg()" % i
    if i < 6:
        return "^fg(orange)%s^fg()" % i
    return "^fg(red)%s^fg()" % i

def mem_check(i):
    i = int(i)
    if i < 80000:
        return "^fg(red)%s^fg()" % i
    if i < 130000:
        return "^fg(green)%s^fg()" % i
    return i

if __name__ == "__main__":
    main()
