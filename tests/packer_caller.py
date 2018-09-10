import subprocess

PACKER_CMD = "./bin/serial_packer"
OUT_DIR = "out/"

def pack(data, outfile):
    p = subprocess.Popen([PACKER_CMD,"-o",outfile], stdin=subprocess.PIPE)
    p.communicate(data)

def packFromFile(src, outfile):
    subprocess.call([PACKER_CMD,src,"-o",outfile])

def unpack(packed_file):
    return subprocess.check_output([PACKER_CMD,"-u",packed_file])

def unpackToFile(packed_file, outfile):
    subprocess.call([PACKER_CMD,"-u",packed_file,"-o",outfile])


