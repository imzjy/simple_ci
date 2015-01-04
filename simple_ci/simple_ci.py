# -*- coding: utf-8 -*-

import urllib
import paramiko
import qjson
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello():
    return ("Simple CI Server: %s" % datetime.now())
 
@app.route("/bitbucket", methods=["POST"])
def bitbucket():
    posted_data = request.stream.read()
    assert posted_data, 'post data is empty'
    # print posted_data
    try:
        push_notice = qjson.loads(urllib.unquote_plus(posted_data).lstrip('payload='))
        branch = push_notice['commits'][0]['branch']
        print branch
        
        if branch in ('master', 'online') :
            cm = push_notice['commits'][0]
            print "%s %s %s" % (cm['raw_node'], cm['author'], cm['utctimestamp'])
            print cm['message']
            ssh_script('deploy.sh', branch)
    except ex:
        print ex
        return 'error'
    return posted_data

@app.route("/github", methods=["POST"])
def github():
    posted_data = request.stream.read()
    assert posted_data, 'post data is empty'
    # print posted_data
    try:
        push_notice = qjson.loads(urllib.unquote_plus(posted_data).lstrip('payload='))
        branch = push_notice['commits'][0]['branch']
        print branch
        
        if branch in ('master', 'online') :
            cm = push_notice['commits'][0]
            print "%s %s %s" % (cm['raw_node'], cm['author'], cm['utctimestamp'])
            print cm['message']
            local_script('deploy.sh', branch)
    except ex:
        print ex
        return 'error'
    return posted_data

 
def ssh_script(script_name, branch):
    print "deploy branch of %s" % branch
    deploy_script = "sh %s %s" % (script_name, branch)
 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('host', username='user', key_filename='private_key')
    stdin, stdout, stderr = ssh.exec_command(deploy_script)
    msgs = stdout.readlines()
    for m in msgs:
        print m,
    ssh.close()

def local_script(script_name, branch):
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4040)