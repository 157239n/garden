
import os, flask, gpiozero, time, threading, json # just to make sure the environment has these packages

def error(message):
	print(f"{message}, aborting...")
	exit()

def replaceInFile(file, _from, _to):
	f = open(file)
	data = f.read().replace(_from, _to)
	f.close()

	f = open(file, "w")
	f.write(data)
	f.close()

repoDir = "/home/pi/repos/garden"

if os.getcwd() != repoDir: error(f"Current working directory is not {repoDir}")
if os.system("crontab cron.txt"): error("Something gone wrong while installing crontab")
replaceInFile(f"{repoDir}/startup", "PORT", int(input("\nChoose a remote port: ")))
replaceInFile(f"{repoDir}/startup", "SERVER", int(input("\nMake sure you have your ssh key files ready and you can access the server normally before continuing...\nChoose a server (eg. user@company.com): ")))
print("""All done. Now it will automatically run right after boot. To run now without rebooting, execute ./startup

Reminders:
- Controlling pins are 14, 15, 20 and 21. Use whatever is convenient for you
- Use `nmap -p22 192.168.1.0/24` to scan for the pi on the local network""")


