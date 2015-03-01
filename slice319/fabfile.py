from fabric.api import *

#IMPORTANT: We only get about 12GB of storage across all the nodes.
#Keep test files from being too huge, and clean up afterwards.

#This list is all the available hosts. You can ssh to these using the 
#rsa key and ssh_config files in this folder. Uncomment any names you 
#want to use.
env.hosts = ["slice319.pcvm3-1.geni.case.edu",
#    "slice319.pcvm1-1.geni.it.cornell.edu",  This slice misbehaving
    "slice319.pcvm3-1.instageni.metrodatacenter.com",
    "slice319.pcvm2-2.instageni.rnoc.gatech.edu",
    "slice319.pcvm3-2.instageni.illinois.edu",
#    "slice319.pcvm5-7.lan.sdn.uky.edu",
#    "slice319.pcvm3-1.instageni.lsu.edu",
#    "slice319.pcvm2-2.instageni.maxgigapop.net",
#    "slice319.pcvm1-1.instageni.iu.edu",
#    "slice319.pcvm3-4.instageni.rnet.missouri.edu",
#    "slice319.pcvm3-7.instageni.nps.edu",
#    "slice319.pcvm2-1.instageni.nysernet.org",
#    "slice319.pcvm3-11.genirack.nyu.edu",
#    "slice319.pcvm5-1.instageni.northwestern.edu",
#    "slice319.pcvm5-2.instageni.cs.princeton.edu",
#    "slice319.pcvm3-3.instageni.rutgers.edu",
#    "slice319.pcvm1-6.instageni.sox.net",
#    "slice319.pcvm3-1.instageni.stanford.edu",
#    "slice319.pcvm2-1.instageni.idre.ucla.edu",
#    "slice319.pcvm4-1.utahddc.geniracks.net",
#    "slice319.pcvm1-1.instageni.wisc.edu",
  ]

#Dont touch these
env.key_filename="./id_rsa"
env.use_ssh_config = True
env.ssh_config_path = './ssh-config'


#Functions defined here will run on all the nodes
#by calling fab <func_name> from the command line

#You can mount fabric on your machine, or ssh to
#u-kubuntu.csc.uvic.ca to test stuff

def pingtest():
	run('ping -c 3 www.yahoo.com')

def uptime():
	run('uptime')

def ifconfig():
	run('ifconfig')

#Mounts files to the nodes
@parallel
def update():
	run ('mkdir -p client')
	run ('mkdir -p server')

	with lcd('../'):
		put('client/*','client/')
		put('server/*','server/')

#Cleans the nodes (kills everything everywhere)
@parallel
def clean():
	run('rm -r *')

#The @hosts decorator makes it only run on certain machines
@hosts('slice319.pcvm3-1.geni.case.edu')
def runserver():
	run ('python server/main.py')


def runclients():
	run('python client/main.py')
