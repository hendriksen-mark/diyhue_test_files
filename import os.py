import os

configDir = '/opt/hue-emulator/config1'

try:
    os.popen('rm -r ' + configDir + '/*.yaml')
    #os.remove(configDir + "/*.yaml")
except Exception as e:
    print("Something went wrong when deleting the config")
    print(str(type(e).__name__) + " " + str(e))

#os.popen('cp -r ' + configDir + '/backup/*.yaml ' + configDir + '/')
#os.popen('tar -czvf ' + configDir + '/config.tar.gz ' + configDir + '/*.yaml')
#os.popen('zip ' + configDir + '/config ' + configDir + '/*.yaml )