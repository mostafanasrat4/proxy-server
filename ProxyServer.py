#The code defines a global dictionary called cache that stores cached web pages.

#The is_cached function checks if a given URL is in the cache.

#The get_cached_page function retrieves a cached page from the cache dictionary.

#The cache_page function stores a page in the cache dictionary with a timestamp and t
#he page data and content type.

#The send_get_request function sends a GET request to a given server for a specific URL.

#The parse_response function takes in the response from a server and returns the status code, 
#headers, and body of the response.

#The handle_client function handles a client request by first checking if it is a GET request, 
#and then checking if the requested URL is in the cache. If it is, it sends the cached page to the 
#client. If not, it sends a GET request to the server, retrieves the response, and stores the 
# response in the cache before sending it to the client.

#This code creates a very simple web proxy server that listens for client requests and either 
#serves a cached page or retrieves a page from the server and caches it before sending it to the 
# client. It is able to handle any type of object, including HTML pages and images.
import socket
import threading
import time
import re
import os
from os import path, makedirs
import shutil

# Global dictionary to store cached pages
cache = {}

# Function to get the current time
def get_time():
  return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

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
  """ page = cache.get(url)
  if page:
    return page["data"], page["type"]
  else:
    return None, None """
  if is_cached(url):
    filepath, _ , _ = parse_url(url)
    data = open(filepath, 'rb').read()
    return data
  else:
    return None

# Function to store a page in the cache
def cache_page(url, data, content_type):
  """ cache[url] = {
    "timestamp": get_time(),
    "data": data,
    "type": content_type
  } """
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

# Function to send a GET request to a server
def send_get_request(server, url):
  request = f"GET {url} HTTP/1.1\r\nHost: {server}\r\nConnection: close\r\n\r\n"
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((server, 80))
  s.sendall(request.encode())
  response = b""
  while True:
    data = s.recv(4096)
    if not data:
      break
    response += data
  s.close()
  return response

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

# Function to handle a client request
def handle_client_request(conn, addr):
  request = conn.recv(4096)
  # Parse the request
  method, url, server = parse_request(request)
  print(f'>> Recieved request to {url}')
  # Check if it's a GET request
  if method != "GET":
    print(f'!! This is an HTTP {method} method. Only accept GET requests')
    print(request)
    conn.close()
    return
  # Check if the page is in the cache
  if is_cached(url):
    data, content_type = get_cached_page(url)
    # Send the page from the cache
    response = (f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(data)}\r\n\r\n").encode()
    response += data
    conn.sendall(response)
    conn.close()
    print('>> Served from cache')
  else:
    print('>> Not found in cache')
    response = send_get_request(server, url)
    print(f'>> Sent GET request to get page')
    #print(f'response: \n{response}')
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

# Function to initiate the proxy server
def init_proxy_server():
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = socket.gethostname()
  # bind the socket to localhost, and port 8080
  server_socket.bind((host, 8080))
  server_socket.listen(100)
  print("server ready to listen")

  # wait for a connection
  while 1:
      client_socket, client_address = server_socket.accept()
      print("\n------------------------------------------------------------")
      print(f"New connection from {client_address}")
      handle_client_request(client_socket,client_address)

# Function to parse a request url
def parse_url(url):
  url = url.lower().removeprefix('http://')
  sections = url.split('/')
  filedir = path.join('cache', *sections[:-1])
  filename = sections[-1]
  if filename == '':
    filename = 'index.html'
  filepath = path.join(filedir, filename)
  return filepath, filedir, filename


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




if __name__ == "__main__":
  init_proxy_server()