#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import codecs
import subprocess
import paramiko
import qjson
from datetime import datetime
from flask import Flask, request

# globals
app = Flask(__name__)
CURPATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURPATH, 'config.json')

def now():
    return datetime.utcnow()

def parse_config():
    '''
    return json playload object
    '''
    with codecs.open(CONFIG_PATH, 'r', 'utf-8') as f:
        return qjson.loads(f.read())


@app.route("/")
def hello():
    return ("Simple CI Server: %s" % now())
 
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
            run_ssh_script('deploy.sh', branch)
    except ex:
        print ex
        return 'error'
    return posted_data

@app.route("/github", methods=["POST"])
def github():
    posted_data = request.stream.read()
    # assert posted_data, 'post data is empty'
    # print posted_data
    try:
        push_notice = qjson.loads(posted_data)
        config  = parse_config()

        if hasattr(push_notice, 'zen'):
            print push_notice.zen
            return 'ping...ok!'

        if hasattr(push_notice, 'ref'):
            print push_notice.ref

            branch = push_notice.ref.split('/')[-1]
            print branch
            
            if branch in config.branchs :
                run_local_script(config.path, branch)
    except:
        raise
    return 'ok'

 
def run_ssh_script(script_name, branch):
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

def run_local_script(script_path, branch):
    print 'run local script'
    subprocess.call(script_path + ' ' + branch, shell=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4040, debug=True)