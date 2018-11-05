import time
from http.server import HTTPServer
from server import Server

HOST, PORT = 'localhost', 8888

if __name__ == '__main__':
    httpd = HTTPServer((HOST, PORT), Server)
    print(time.asctime(), 'Server UP - {0}:{1}'.format(HOST,PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - {0}:{1}'.format(HOST,PORT))