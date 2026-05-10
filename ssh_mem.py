import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('159.138.84.175', username='root', password='Langagent2026')
stdin, stdout, stderr = ssh.exec_command('docker inspect ai-backend --format "{{.HostConfig.Memory}}"')
print("Mem:", stdout.read().decode())
