import ftplib
import os

def read_credentials(creds, serverNumber):
    with open(creds, 'r') as file:
        global server
        totalLines = file.readlines()
        lines = totalLines[serverNumber].strip()
        server, username, password = lines.split(',')
        if ':' in server:
            ip, port = server.split(':')
            port = int(port)
        else:
            ip = server
            port = 21
        server = f"{ip}:{port}"
    print(f"Server {serverNumber + 1}: {server}")
    if serverNumber + 1 != len(totalLines):
        serverNumber += 1
        return ip, port, username, password, serverNumber
    else:
        return ip, port, username, password, False

def downloadFile(ftp, remotePath, localPath):
    try:
        with open(localPath, 'wb') as local_file:
            ftp.retrbinary(f"RETR {remotePath}", local_file.write)
        print(f"Downloaded: {server}:{localPath}")
    except ftplib.error_perm as e:
        print(f"Error downloading {remotePath}: {e}")

def downloadDirectory(ftp, remoteDirectory, localDirectory):
    if not os.path.exists(localDirectory):
        os.makedirs(localDirectory)
    try:
        ftp.cwd(remoteDirectory)
    except ftplib.error_perm as e:
        print(f"Error changing to directory {remoteDirectory}: {e}")
        return

    files = ftp.nlst()

    for file in files:
        localFilePath = os.path.join(localDirectory, file)
        remoteFilePath = os.path.join(remoteDirectory, file)

        if is_ftp_directory(ftp, file):
            downloadDirectory(ftp, remoteFilePath, localFilePath)
        else:
            downloadFile(ftp, remoteFilePath, localFilePath)

    ftp.cwd('..')

def is_ftp_directory(ftp, name):
    try:
        ftp.cwd(name)
        ftp.cwd('..')
        return True
    except ftplib.error_perm:
        return False

def downloadAll(creds, serverNumber):
    try:
        ip, port, username, password, moreServers = read_credentials(creds, serverNumber)

        ftp = ftplib.FTP()
        ftp.connect(ip, port)
        ftp.login(user=username, passwd=password)

        cwd = os.getcwd()

        server_directory = os.path.join(cwd, f"{ip.replace('.', '_')}_{port}")
        if not os.path.exists(server_directory):
            os.makedirs(server_directory)

        downloadDirectory(ftp, '/', server_directory)

        ftp.quit()
        print("All files downloaded successfully.")
        if moreServers != False:
            downloadAll(creds, serverNumber + 1)

    except ftplib.all_errors as e:
        print(f"FTP error: {e}")


creds = input("File name containing credentials: ")

downloadAll(creds, 0)
