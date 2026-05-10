import paramiko

hostname = '159.138.84.175'
username = 'root'
password = 'Langagent2026'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command("docker inspect ai-backend | grep -i OOM")
out = stdout.read().decode('utf-8', errors='replace')
print("OOM Check:", out)

stdin, stdout, stderr = ssh.exec_command("docker logs ai-backend | tail -n 20")
out = stdout.read().decode('utf-8', errors='replace')
print("Logs:", out)

ssh.close()
