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
    "cd /root/Lang_Learning_Agent_CC_Project && docker build --build-arg NEXT_PUBLIC_API_URL=https://lang-agent-asser.duckdns.org --build-arg NEXT_PUBLIC_API_KEY=qKqr7nG3oPh2Aq8q1uSTSC5Nh72-I1fLNSVo7t9l28c -f Dockerfile.frontend -t lang-agent-project/frontend-ui:v1 .",
    "docker rm -f ai-backend ai-frontend",
    "docker run -d --name ai-backend -p 8000:8000 --restart unless-stopped --env-file /root/.env lang-agent-project/api-backend:v1",
    "docker run -d --name ai-frontend -p 3000:3000 --restart unless-stopped lang-agent-project/frontend-ui:v1"
]

for cmd in commands:
    execute_cmd(ssh, cmd)

ssh.close()
