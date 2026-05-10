import paramiko

hostname = '159.138.84.175'
username = 'root'
password = 'Langagent2026'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password, timeout=10)

def execute_cmd(ssh, command):
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    print(out)
    if err:
        print("ERRORS:", err)
    return exit_status, out, err

commands = [
    "cd /root/Lang_Learning_Agent_CC_Project && git pull",
    "cd /root/Lang_Learning_Agent_CC_Project && docker build -f Dockerfile.backend -t lang-agent-project/api-backend:v1 .",
    "docker rm -f ai-backend",
    "docker run -d --name ai-backend -p 8000:8000 --restart unless-stopped --env-file /root/.env lang-agent-project/api-backend:v1",
]

for cmd in commands:
    execute_cmd(ssh, cmd)

ssh.close()
