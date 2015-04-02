from fabric.api import *
env.hosts = [
#  "slice352.pcvm3-1.geni.case.edu",
#    "slice352.pcvm3-1.instageni.metrodatacenter.com",
#    "slice352.pcvm2-2.instageni.rnoc.gatech.edu",
#    "slice352.pcvm3-2.instageni.illinois.edu",
#    "slice352.pcvm5-7.lan.sdn.uky.edu",
#    "slice352.pcvm3-1.instageni.lsu.edu",
#    "slice352.pcvm2-2.instageni.maxgigapop.net", I killed this one
    "slice352.pcvm1-1.instageni.iu.edu",
    "slice352.pcvm3-4.instageni.rnet.missouri.edu",
    "slice352.pcvm3-7.instageni.nps.edu",
#    "slice352.pcvm2-1.instageni.nysernet.org", dead on delivery, do not use
    "slice352.pcvm3-11.genirack.nyu.edu", #10.12.1.34
#    "slice352.pcvm5-1.instageni.northwestern.edu",
#    "slice352.pcvm5-2.instageni.cs.princeton.edu",
#    "slice352.pcvm3-3.instageni.rutgers.edu",
#    "slice352.pcvm1-6.instageni.sox.net",
#    "slice352.pcvm3-1.instageni.stanford.edu",
#    "slice352.pcvm2-1.instageni.idre.ucla.edu",
#    "slice352.pcvm4-1.utahddc.geniracks.net",
#    "slice352.pcvm1-1.instageni.wisc.edu",
  ]

env.key_filename="./id_rsa"
env.use_ssh_config = True
env.ssh_config_path = './ssh-config'

def pingtest():
    run('ping -c 3 www.yahoo.com')

def uptime():
    run('uptime')

@parallel
def deploy():
	run('mkdir -p client')
	run('mkdir -p server')
	run('mkdir -p file')
	put('./../client/*','./client/')
	put('./../server/*', 'server/')

@parallel
def clean():
	run('rm -r *')

def ls():
	run('ls -R -l')

def ifconfig():
	run('ifconfig')

@hosts("slice352.pcvm3-11.genirack.nyu.edu")
def runServer():
	run('python3 server/main.py')

@hosts("slice352.pcvm1-1.instageni.iu.edu")
def runClient1():
	run('python3 client/main.py -I 10.12.1.34')

@hosts("slice352.pcvm3-4.instageni.rnet.missouri.edu")
def runClient2():
	run('python3 client/main.py -I 10.12.1.34')

@hosts("slice352.pcvm3-7.instageni.nps.edu")
def runClient4():
        run('python3 client/main.py -I 10.12.1.34')

@hosts("slice352.pcvm3-11.genirack.nyu.edu")
def runClient3():
        run('python3 client/main.py -I 10.12.1.34')

@hosts(["slice352.pcvm1-1.instageni.iu.edu","slice352.pcvm3-4.instageni.rnet.missouri.edu","slice352.pcvm3-11.genirack.nyu.edu"])
@parallel
def prepDemo():
	put('testFile.html','file/')
	put('testFile2.html','file/')
