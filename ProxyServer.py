import socket
import time
import os
from os import path, makedirs
import shutil

# Global dictionary to store cached pages
cache = {}

# Function to get the current time
def get_time():
  return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

# Function to parse a url
def parse_url(url):
  url = url.lower().removeprefix('http://')
  url = ''.join(filter(lambda char: char not in ['<', '>', ':', '"', '|', '?', '*'] , url))
  sections = url.split('/')
  filedir = path.join('cache', *sections[:-1])
  filename = sections[-1]
  if filename == '':
    filename = 'index.html'
  filepath = path.join(filedir, filename)
  return filepath, filedir, filename

# Function to check if a page is in the cache
def is_cached(url):
  """ return cache.get(url) != None """
  filepath, _ , _ = parse_url(url)
  if(path.exists(filepath) and path.isfile(filepath)):
    return True
  else:
    return False

# Function to get the page from the cache
def get_cached_page(url):
  if is_cached(url):
    filepath, _ , _ = parse_url(url)
    data = open(filepath, 'rb').read()
    return data
  else:
    return None

# Function to store a page in the cache
def cache_page(url, data):
  filepath, filedir, _ = parse_url(url)
  if(not path.exists(filedir) or not path.isdir(filedir)):
    os.makedirs(filedir)
  file = open(filepath, 'wb')
  file.write(data)
  file.close()

# Function to clear the whole cache 
def clear_cache():
  if(path.exists('cache') and path.isdir('cache')):
    shutil.rmtree('cache')

# Function to check if a domain is blocked
def is_blocked(url):
  if( not path.exists('blocked_sites.txt') or not path.isfile('blocked_sites.txt') ):
    print(f'!! Did not found "blocked_sites.txt" file')
    return False
  websites = open("blocked_sites.txt", 'r').readlines()
  for website in websites:
    if (url == website.strip()):
      return True
  return False

# Function to block client request
def get_blocked_page():
  response = b'HTTP/1.1 401 Unauthorized\r\nContent-Type:text/html\r\n\r\n'
  blocked_page = os.path.join('cache', 'blocked', 'blocked_page.html')
  if( path.exists(blocked_page) and path.isfile(blocked_page) ):
    response += open(blocked_page, 'rb').read()
  else:
    response += b"""<html>
                      <h1 style='color:red'>401 Unauthorized</h1>
                      <h3>This page was blocked by the proxy server.</h3>
                    </html>"""
  return response

# Function to parse the request from a clinet
def parse_request(request):
  if request == b"":
    return None, None, None
  headers, _ = request.split(b"\r\n\r\n", 1)
  header_lines = headers.split(b"\r\n")
  request_line = header_lines[0]
  method, url, _ = request_line.split(b" ", 2)
  for header in header_lines[1:]:
    name, value = header.split(b": ", 1)
    if(name.lower() == b"host"):
      server = value
  return method.decode(), url.decode(), server.decode()

# Function to send a GET request to a server
def send_get_request(server, url):
  request = f"GET {url} HTTP/1.1\r\nHost: {server}\r\nConnection: close\r\n\r\n"
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    s.connect((server, 80))
    s.sendall(request.encode())
    print(f'>> Sent GET request to get page')
    response = b""
    while True:
      data = s.recv(4096)
      if not data:
        break
      response += data
    s.close()
    return response
  except Exception as e:
    print(f'!! Failed to connect with this server {server}')
    #print(e)
    return None

# Function to send a POST request to a server
def send_post_request(server, request):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    s.connect((server, 80))
    s.sendall(request)
    print(f'>> Sent POST request to this page')
    response = b""
    """ while True:
      data = s.recv(4096)
      if not data:
        break
      response += data """
    s.close()
    return response
  except Exception as e:
    print(f'!! Failed to connect with this server {server}')
    #print(e)
    return None

# Function to parse a response from a server
def parse_response(response):
  headers, body = response.split(b"\r\n\r\n", 1)
  header_lines = headers.split(b"\r\n")
  status_line = header_lines[0]
  status_code = int(status_line.split(b" ")[1])
  status_word = status_line[13:].decode()
  headers = {}
  for header in header_lines[1:]:
    name, value = header.split(b": ", 1)
    headers[name.decode().lower()] = value.decode()
  return status_code, status_word, headers, body

# Function to handle recieved GET request
def handle_get_request(server, url):
  # Check if the server is blocked
  if is_blocked(server):
    print('>> This url was blocked')
    response = get_blocked_page()
    return response
  # Check if this page is cached
  if is_cached(url):
    data = get_cached_page(url)
    response = (f"HTTP/1.1 200 OK\r\nHost: {server}\r\nContent-Length: {len(data)}\r\n\r\n").encode()
    response += data
    print('>> Served from cache')
    return response
  # If not cached, send GET request and cache
  else:
    print('>> Not found in cache')
    response = send_get_request(server, url)
    if response:
      status_code, status_word, _ , body = parse_response(response)
      if(status_code==200):
          cache_page(url, body)
          print('>> Page cached successfully')
      else:
        print(f'!! ERROR {status_code} {status_word}')
    return response

# Function to handle a single client request
def handle_client_request(request):
  method, url, server = parse_request(request)
  print(f'>> Recieved a {method} request to {url}')
  response = None
  if method == 'GET':
    response = handle_get_request(server, url)
  elif method == 'POST':
    response = send_post_request(server, request)
  else:
    print(f'!! This is an HTTP {method} request. Can handle only GET and POST requests')
  return response

# Function to initiate the proxy server
def init_proxy_server():
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = socket.gethostname()
  # bind the socket to localhost, and port 8080
  server_socket.bind(('', 8080))
  server_socket.listen(100)
  print(">> Server ready to listen")

  # wait for a connection
  while 1:
      client_socket, client_address = server_socket.accept()
      print("\n------------------------------------------------------------")
      print(f"New connection from {client_address}")
      request = client_socket.recv(4096)
      response = handle_client_request(request)
      if response != b'' and response != None:
        client_socket.sendall(response)
      client_socket.close()



def test():
  url = "http://p3.ssl.qhimg.com/t01649b59bec74b0e1f"
  data = b'data'
  filepath, filedir, filename = parse_url(url)

  if(is_cached(url)):
    print('cached')
    d = open(filepath, 'rb').read()
    print(d)
    #get_cached_page(url)
  else:
    print(f'>> Sent GET request to get page')
    #response = send_get_request(server, url)
    #status_code, status_word, headers, body = parse_response(response)
    #if(status_code==200):
        #cache_page(url, body, headers["content-type"])
    if(not path.exists(filedir) or not path.isdir(filedir)):
      makedirs(filedir)
    open(filepath, 'wb').write(data)
    print('>> Page cached successfully')


# Function to handle a client request
def handle_client_request1(conn, addr):
  
  # Parse the request
  method, url, server = parse_request(request)
  print(f'>> Recieved request to {url}')
  # Check if it's a GET request
  if method != "GET":
    print(f'!! This is an HTTP {method} method. Only accept GET requests')
    conn.close()
    return
  # Check if the page is in the cache
  if is_cached(url):
    data = get_cached_page(url)
    # Send the page from the cache
    response = (f"HTTP/1.1 200 OK\r\nContent-Length: {len(data)}\r\n\r\n").encode()
    response += data
    conn.sendall(response)
    conn.close()
    print('>> Served from cache')
  else:
    print('>> Not found in cache')
    response = send_get_request(server, url)
    print(f'>> Sent GET request to get page')
    if response:
      status_code, status_word, headers, body = parse_response(response)
      if(status_code==200):
          cache_page(url, body, headers["content-type"])
          print('>> Page cached successfully')
          conn.sendall(response)
          conn.close()
      else:
        print(f'!! ERROR {status_code} {status_word}')
        conn.sendall(response)
        conn.close()


if __name__ == "__main__":
  init_proxy_server()