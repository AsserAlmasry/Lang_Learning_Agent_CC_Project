import paramiko
import time

hostname = '159.138.84.175'
username = 'root'
password = 'Langagent2026'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/conf.d/lang_agent.conf")
conf = stdout.read().decode('utf-8')

if "rewrite ^/api/(.*)$ /$1 break;" in conf:
    print("Found rewrite rule. Removing it...")
    new_conf = conf.replace("rewrite ^/api/(.*)$ /$1 break;", "")
    
    # Write back to server
    sftp = ssh.open_sftp()
    with sftp.file('/etc/nginx/conf.d/lang_agent.conf', 'w') as f:
        f.write(new_conf)
    sftp.close()
    
    # Reload nginx
    stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
    print("NGINX Reloaded:", stdout.read().decode('utf-8'))
    print("ERR:", stderr.read().decode('utf-8'))
else:
    print("Rewrite rule not found.")

ssh.close()
