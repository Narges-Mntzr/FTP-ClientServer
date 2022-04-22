from pyngrok import ngrok
ngrok.set_auth_token("286v8HrxqAl9O0Cg9d2aqyMaFG0_6ggrottX6UzwQxwCPyZfV")
ssh_tunnel = str(ngrok.connect(22,'tcp'))
ssh_tunnel2 = ngrok.connect(23,'tcp')
str1 = ssh_tunnel.split('"')[1]
x = str1.split(':')
host = x[1][2:]
portnum = int(x[2])
print(host)
print(portnum)
