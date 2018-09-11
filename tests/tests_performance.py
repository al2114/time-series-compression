import data_generator as datagen
from timeit import timeit
import random
import numpy as np
import inspect
import os


scales = {
        "small": 1000,
        "medium": 15000,
        "big": 100000
        }

timestamp_modes = {
        "random": datagen.gen_ts_random,
        "ideal": datagen.gen_ts_ideal,
        "realistic_20ms": datagen.gen_ts_realistic_20ms,
        "realistic_200ms": datagen.gen_ts_realistic_200ms,
        "realistic_1000ms": datagen.gen_ts_realistic_1000ms,
        "realistic_bad_20ms": datagen.gen_ts_realistic_bad_20ms,
        "realistic_bad_200ms": datagen.gen_ts_realistic_bad_200ms,
        "realistic_bad_1000ms": datagen.gen_ts_realistic_bad_1000ms
        }

value_modes = {
        "normal_dist": datagen.gen_val_normal_dist,
        "uniform_dist": datagen.gen_val_uniform_dist,
        "positive_dist": datagen.gen_val_positive_dist,
        "negative_dist": datagen.gen_val_negative_dist,
        "moving_signal": datagen.gen_val_moving_signal,
        "random_spike": datagen.gen_val_random_spike,
        "noisy_periodic": datagen.gen_val_noisy_periodic
        }

def testPack(filepath,infile):
    setup = """
        from packer_caller import packFromFile
        infile = "%s"
        filepath = "%s"
        """ % (infile, filepath)
    setup = inspect.cleandoc(setup)
    pack_time = timeit(
            setup = setup,
            stmt = "packFromFile(infile,filepath)",
            number = 10)/10.0
    return pack_time

def testUnpack(filepath,outfile):
    setup = """
        from packer_caller import unpackToFile
        packed_file = "%s"
        outfile = "%s"
        """ % (filepath, outfile)
    setup = inspect.cleandoc(setup)
    unpack_time = timeit(
            setup = setup,
            stmt = "unpackToFile(packed_file,outfile)",
            number = 10)/10.0
    return unpack_time


def printReport(pack_time,unpack_time,N,strlen,pack_size):
    print "\tPacking:"
    print "\t\tTotal time: %.4fs" % pack_time
    print "\t\tAverage throughput: %.2fkB/s" % ((4.0*N/pack_time)/1000.0)
    print "\t\tAverage latency: %.2fus" % (1000000.0*pack_time/float(N))

    print "\tUnpacking:"
    print "\t\tTotal time: %.4fs" % unpack_time
    print "\t\tAverage throughput: %.2fkB/s" % ((4.0*N/unpack_time)/1000.0)
    print "\t\tAverage latency: %.2fus" % (1000000.0*unpack_time/float(N))

    print "\tCompression:"
    print "\t\tOriginal size: %d Bytes" % strlen
    print "\t\tPacked size: %d Bytes" % pack_size
    print "\t\tCompression ratio: %.2f%% compressed" % (100 * (1.0 - float(pack_size)/float(strlen)))
    print ""

def test(ts_mode,val_mode, scale):
    test_name = ts_mode + "_" + val_mode + "_" + scale
    filepath = "tmp/"+test_name+".pkd.bin"
    outfile = "tmp/"+test_name+".out"
    infile = "tmp/"+test_name+".bin"

    N = scales[scale]
    ts = timestamp_modes[ts_mode](N)
    vals = value_modes[val_mode](N)
    d = datagen.serialize(ts,vals)

    print "Test case: "+test_name

    with open(infile,'w') as f:
        f.write(d)

    avg_pack_time = testPack(filepath, infile)
    avg_unpack_time = testUnpack(filepath, outfile)

    with open(infile,'r') as f:
        indata = f.read()
    with open(outfile,'r') as f:
        output = f.read()

    if output == indata:
        print "\t"*4+"... CORRECT"
        filesize = os.stat(filepath).st_size
        printReport(avg_pack_time,avg_unpack_time,N,len(d),filesize)
    else:
        print "\t"*4+"... INCORRECT"


def runTests():
    for ts_mode in timestamp_modes:
        for scale in scales:
            test(ts_mode,"uniform_dist",scale)
    for val_mode in value_modes:
        if val_mode is not "uniform_dist":
            for scale in scales:
                test("realistic_200ms",val_mode,scale)


