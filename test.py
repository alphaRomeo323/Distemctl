import subprocess

var = (subprocess.run('ls', shell=True).stdout)

print(var)