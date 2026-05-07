import paramiko

hostname = '159.138.84.175'
username = 'root'
password = 'Langagent2026'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command("cat /root/.env")
print(stdout.read().decode('utf-8'))

ssh.close()
