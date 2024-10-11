import os
import socket
from datetime import datetime
import cgi

class SocketServer:
    def __init__(self):
        self.bufsize = 1024  # 버퍼 크기 설정
        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()  # 응답 파일 읽기
        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def save_request(self, request_data):
        """요청 데이터를 파일로 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_path = os.path.join(self.DIR_PATH, f"{timestamp}.bin")
        with open(file_path, 'wb') as f:
            f.write(request_data)
        print(f"Request saved to {file_path}")

    def save_image(self, image_data, filename):
        """이미지 파일로 저장"""
        image_path = os.path.join(self.DIR_PATH, filename)
        with open(image_path, 'wb') as img_file:
            img_file.write(image_data)
        print(f"Image saved to {image_path}")

    def handle_multipart_data(self, data):
        """멀티파트 데이터 처리"""
        boundary = data.split(b'\r\n')[0]  # 멀티파트 경계 추출
        parts = data.split(boundary)
        for part in parts:
            if b'Content-Disposition' in part:
                disposition = part.split(b'Content-Disposition:')[1].split(b'\r\n')[0]
                if b'filename' in disposition:
                    filename = disposition.split(b'filename="')[1].split(b'"')[0].decode('utf-8')
                    image_data = part.split(b'\r\n\r\n')[1].split(b'\r\n--')[0]
                    self.save_image(image_data, filename)

    def run(self, ip, port):
        """서버 실행"""
        # 소켓 생성
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")
        try:
            while True:
                # 클라이언트의 요청 대기
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)  # 타임아웃 설정 (5초)
                print("Request message...\r\n")
                request_data = b""
                while True:
                    try:
                        data = clnt_sock.recv(self.bufsize)
                        if not data:
                            break
                        request_data += data
                    except socket.timeout:
                        break
                
                # 요청 저장
                self.save_request(request_data)

                # 멀티파트 데이터 처리 (이미지 저장)
                self.handle_multipart_data(request_data)

                # 응답 전송
                clnt_sock.sendall(self.RESPONSE)
                # 클라이언트 소켓 닫기
                clnt_sock.close()

        except KeyboardInterrupt:
            print("\r\nStop the server...")
            # 서버 소켓 닫기
            self.sock.close()

if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)

