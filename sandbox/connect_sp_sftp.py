import paramiko


def fetch_files(username, key_file_name, key_file_password):
    host = "sftp.serviceplatformen.dk"
    port = 22

    transport = paramiko.Transport((host, port))
    key = paramiko.RSAKey.from_private_key_file(key_file_name, password=key_file_password)
    transport.connect(username=username, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)


    remote_path = './IN/'
    localpath = './sftp_download/'


    filenames = sftp.listdir(remote_path)

    for filename in filenames:
        remote_file_path = remote_path + str(filename)
        local_file_path = localpath + str(filename)
        sftp.get(remote_file_path, local_file_path)
        print "Downloaded " + local_file_path



    sftp.close()
    transport.close()
    print 'SFTP connection closed.'


