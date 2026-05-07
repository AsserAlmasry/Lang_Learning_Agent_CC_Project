import paramiko

hostname = '159.138.84.175'
username = 'root'
password = 'Langagent2026'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command("sleep 5 && docker ps && docker logs ai-backend --tail 10 && docker logs ai-frontend --tail 10")
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')

print("OUT:")
print(out)
print("ERR:")
print(err)

ssh.close()
