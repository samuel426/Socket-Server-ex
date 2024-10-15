import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.bufsize = 1024  # 버퍼 크기 설정
        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()  # 응답 파일 읽기
        self.DIR_PATH = './request'
        self.IMAGE_DIR = './image'
        self.createDir(self.DIR_PATH)
        self.createDir(self.IMAGE_DIR)  # 이미지 폴더 생성

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"Directory {path} created.")
        except OSError:
            print(f"Error: Failed to create the directory {path}.")

    def save_request(self, request_data):
        """요청 데이터를 파일로 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_path = os.path.join(self.DIR_PATH, f"{timestamp}.bin")
        with open(file_path, 'wb') as f:
            f.write(request_data)
        print(f"Request saved to {file_path}")

    def save_image(self, image_data, filename):
        """이미지 파일을 'image' 폴더에 저장"""
        image_path = os.path.join(self.IMAGE_DIR, filename)
        with open(image_path, 'wb') as img_file:
            img_file.write(image_data)
        print(f"Image saved to {image_path}")

    def handle_multipart_data(self, data):
        """멀티파트 데이터 처리 (디버깅 추가)"""
        # HTTP 요청의 헤더와 본문을 분리
        headers, body = data.split(b'\r\n\r\n', 1)
        
        # 헤더에서 Content-Type과 boundary 추출
        for header_line in headers.split(b'\r\n'):
            if b'Content-Type: multipart/form-data' in header_line:
                boundary = header_line.split(b'boundary=')[1]
                boundary = b'--' + boundary  # boundary 앞에 '--' 추가
                print(f"Boundary: {boundary}")

        # 멀티파트 데이터를 경계로 분리
        parts = body.split(boundary)
        print(f"Total parts: {len(parts)}")

        for i, part in enumerate(parts):
            print(f"\n--- Processing part {i} ---")
            if b'Content-Disposition' in part:
                headers = part.split(b'\r\n')[1].decode('utf-8')
                print(f"Headers: {headers}")
                
                # 파일명 추출
                if 'filename=' in headers:
                    filename = headers.split('filename=')[1].split('"')[1]
                    print(f"Filename: {filename}")
                    
                    # 파일 데이터 추출
                    file_data = part.split(b'\r\n\r\n')[1].rstrip(b'\r\n--')
                    print(f"File data size: {len(file_data)} bytes")
                    
                    # 이미지 파일 저장
                    self.save_image(file_data, filename)
                else:
                    print("No file found in this part.")
            else:
                print("No Content-Disposition in this part.")

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

