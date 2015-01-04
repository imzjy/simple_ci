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

def get_config(hoster_name):
    '''
    return json playload object
    '''
    with codecs.open(CONFIG_PATH, 'r', 'utf-8') as f:
        return getattr(qjson.loads(f.read()), hoster_name)


@app.route("/")
def hello():
    return ("Simple CI Server: %s" % now())
 
@app.route("/bitbucket", methods=["POST"])
def bitbucket():
    posted_data = request.stream.read()
    posted_data = urllib.unquote_plus(posted_data)
    print posted_data
    try:
        config  = get_config('bitbucket')
        push_notice = qjson.loads(posted_data.lstrip('payload='))

        repo = push_notice.repository.absolute_url.strip('/') 
        branch = push_notice.commits[0].branch
        print repo, ' ', branch

        for recipe in config:
            if repo != recipe.repo:
                break
            if branch not in recipe.branchs:
                break

            if recipe.script == 'ssh':
                run_ssh_script(recipe.ssh, branch)
            if recipe.script == 'local':
                run_local_script(recipe.cmd, branch)
    except:
        raise
    return 'ok'

@app.route("/github", methods=["POST"])
def github():
    posted_data = request.stream.read()
    # assert posted_data, 'post data is empty'
    # print posted_data
    try:
        config  = get_config('github')
        push_notice = qjson.loads(posted_data)

        if hasattr(push_notice, 'zen'):
            print push_notice.zen
            return 'ping...ok!'

        if hasattr(push_notice, 'ref'):
            print push_notice.ref

            repo = push_notice.repository.full_name
            branch = push_notice.ref.split('/')[-1]
            print repo, ' ', branch

            for recipe in config:
                if repo != recipe.repo:
                    break
                if branch not in recipe.branchs:
                    break

                if recipe.script == 'ssh':
                    run_ssh_script(recipe.ssh, branch)
                if recipe.script == 'local':
                    run_local_script(recipe.cmd, branch)
    except:
        raise
    return 'ok'

 
def run_ssh_script(ssh_config, branch):
    print "deploy branch of %s" % branch
    deploy_script = "sh %s %s" % (ssh_config.cmd, branch)
 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_config.host, ssh_config.user, ssh.ssh_key_file)
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