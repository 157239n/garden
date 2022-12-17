
import os, flask, gpiozero, time, threading, json # just to make sure the environment has these packages

def error(message): print(f"{message}, aborting..."); exit()

def replaceInFile(file, _from, _to):
    with open(file) as f: data = f.read().replace(str(_from), str(_to))
    with open(file, "w") as f: f.write(data)

repoDir = "/home/pi/repos/garden"

if os.getcwd() != repoDir: error(f"Current working directory is not {repoDir}")
if os.system("crontab cron.txt"): error("Something gone wrong while installing crontab")
replaceInFile(f"{repoDir}/startup", "PORT", int(input("\nChoose a remote port: ")))
replaceInFile(f"{repoDir}/startup", "SERVER", input("\nMake sure you have your ssh key files ready and you can access the server normally before continuing...\nChoose a server (eg. user@company.com): "))
pins = input("\nChoose pins to control, delimited by commas (eg. `14, 15`, to control pins 14 and 15 independently): ");
replaceInFile(f"{repoDir}/site.html", "const pins = [20, 21];", f"const pins = [{pins}];")
print("""All done. Now it will automatically run right after boot. To run now without rebooting, execute ./startup

Reminders:
- Use `nmap -p22 192.168.1.0/24` to scan for the pi on the local network""")


