import telnetlib

def test_ip(ip,port):
    try:
        telnetlib.Telnet(ip,port,timeout=2)
        print("代理ip有效！")
    except:
        print("代理ip无效！")

test_ip("103.118.46.61","8080")
