import sys
from time import sleep

from ConsoleAPI import API
import socket

import urllib2
import zipfile
import os.path

import subprocess

def unzip( filename):
    zfile = zipfile.ZipFile(filename)
    names = []
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        print "Decompressing " + filename + " on " + dirname
        if not os.path.exists(dirname) and dirname:
            os.mkdir(dirname)
            fd = open(name,"w")
            fd.write(zfile.read(name))
            fd.close()
            names.append(name)
    return names

def internet_off():
    ips = [ '87.248.112.181', '173.194.35.176', '176.32.98.166']

    ret = False
    for rep in ips:
        try:
            print rep
            response=urllib2.urlopen('http://' + rep, timeout=5)
            return False
        except urllib2.URLError as err:
            ret = True
    return ret

class VMAVTest:

    host = "rcs-castore"
    user = "avmonitor"
    passwd = "avmonitorp1234"
    connection = None

    def create_new_factory(self, operation, target, factory, config):
        c = self.connection
        operation = c.operation(operation)
        #TODO: delete target if exists
        print "targets: " + c.targets(target)

        target = c.target_create(operation, target, 'made by vmavtest')
        factory = c.factory_create(operation, target, 'desktop', factory, 'made by vmavtest')
        c.factory_add_config(factory, config)
        print "factory: ", factory
        return factory

    def build_agent(self):
        param = { 'platform': 'windows',
              'binary': { 'demo' : False, 'admin' : False},
              'melt' : {'scout' : True, 'admin' : False, 'bit64' : True, 'codec' : True },
              'sign' : {}
              }

        #{"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true}
        try:
            filename = 'build.out'
            r = conn.build(factory, param, filename)
            contentnames = unzip(filename)
            return [n for n in contentnames if n.endswith('.exe')]
        except Exception, e:
            print e
        
    def execute_build(self, exenames):
        for n in exenames:
            os.system(n)

    def mouse_move(self, timeout=60):
        subp = subprocess.Popen(['mouse_emu.exe'])
        p = psutil.Process(subp.pid)
        try:
            p.wait(timeout)
        except psutil.TimeoutExpired:
            p.kill()
            raise

    def check_instance(self, factory):
        return self.connection.enum_instances(factory)

    def execute_test(self):
        if not internet_off():
            print "ERROR: I don't want to reach Internet"
        #exit(0)

        print "Network unreachable"
        hostname = socket.gethostname()
        operation = 'AVMonitor'
        target = hostname
        factory = hostname
        config = "config.json"

        self.connection = API(host, user, passwd)
        self.connection.login()
        try:
        
            factory = create_new_factory(operation, target, factory, config)
            exe = build_agent( factory )
            execute_build(exe)
            sleep(60 * 5)
            mouse_move()
            sleep(60 * 2)
            result = checkInstance( factory )
        except Exception, e:
            l("Error: " + e)
        finally:
            self.connection.logout()

def test_api():
    print 'test'
    conn = API(host, user, passwd)
    print conn.login()

    if(False):
        operation, target, factory = '511dfd70aef1de05f8001090', '511e44d4aef1de05f800137a', '511e44d5aef1de05f8001380'

    else:
        operation = conn.operation('AVMonitor')
        target = conn.target_create(operation,'Turca','la mia targa')
        factory = conn.factory_create(operation, target, 'desktop', 'fattoria', 'degli animali')
        print "factory: ", factory
        #sleep(10)

        config = open('assets/basic_config_castore.json').read()
        conn.factory_add_config(factory, config)

    param = { 'platform': 'windows',
          'binary': { 'demo' : False, 'admin' : False},
          'melt' : {'scout' : True, 'admin' : False, 'bit64' : True, 'codec' : True },
          'sign' : {}
          }

    #{"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true}
    try:
        r = conn.build(factory, param, 'build.out')
    except Exception, e:
        print e
    
    r = unzip('build.out')
    print r

    r = check_instance( factory )
    print r

    #sleep(5)
    conn.target_delete(target)
    print operation, target, factory
    print conn.logout()

def main():
    if(sys.argv.__contains__('test')):
        test_api()
        exit(0)
    
    vmavtest = VMAVTest()
    vmavtest.execute_test()


if __name__ == "__main__":
    main()