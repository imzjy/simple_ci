# -*- coding: utf-8 -*-

import urllib, json
import paramiko
from datetime import datetime
from flask import Flask, request
 
app = Flask(__name__)
 
@app.route("/")
def hello():
    return ("Simple CI Server: %s" % datetime.now())
 
@app.route("/ci", methods=["GET", "POST"])
def ci():
    if request.method == 'POST':
        posted_data = request.stream.read()
        assert posted_data, 'post data is empty'
        # print posted_data
        try:
            web_notice = json.loads(urllib.unquote_plus(posted_data).lstrip('payload='))
            branch = web_notice['commits'][0]['branch']
            print branch
            
            if branch in ('master', 'online') :
                cm = web_notice['commits'][0]
                print "%s %s %s" % (cm['raw_node'], cm['author'], cm['utctimestamp'])
                print cm['message']
                deploy(branch)
        except ex:
            print ex
            return 'error'
        return posted_data
    return ("Simple CI Server: %s" % datetime.now())
 
 
def deploy(branch):
    print "deploy branch of %s" % branch
    deploy_script = "sh deploy.sh %s" % branch
 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('host', username='user', key_filename='private_key')
    stdin, stdout, stderr = ssh.exec_command(deploy_script)
    msgs = stdout.readlines()
    for m in msgs:
        print m,
    ssh.close()
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4040)