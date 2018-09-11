import data_generator as datagen
from timeit import timeit
import random
import numpy as np
import inspect
import os


scales = {
        "small": 5000,
        "medium": 50000,
        "big": 500000
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

    pack_throughput = ((4.0*N/pack_time)/1024.0)
    pack_latency = (1000000.0*pack_time/float(N))
    unpack_throughput = ((4.0*N/unpack_time)/1024.0)
    unpack_latency = (1000000.0*pack_time/float(N))
    compress_ratio = (100 * (1.0 - float(pack_size)/float(strlen)))

    print "\tPacking:"
    print "\t\tTotal time: %.4fs" % pack_time
    print "\t\tAverage throughput: %.2fkB/s" % pack_throughput
    print "\t\tAverage latency: %.2fus" % pack_latency

    print "\tUnpacking:"
    print "\t\tTotal time: %.4fs" % unpack_time
    print "\t\tAverage throughput: %.2fkB/s" % unpack_throughput
    print "\t\tAverage latency: %.2fus" % unpack_latency
    print "\tCompression:"
    print "\t\tOriginal size: %d Bytes" % strlen
    print "\t\tPacked size: %d Bytes" % pack_size
    print "\t\tCompression ratio: %.2f%% compressed" % compress_ratio
    print ""

    return (True, pack_throughput, unpack_throughput, compress_ratio)


def test(ts_mode,val_mode, scale, results):
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
        performance = printReport(avg_pack_time,avg_unpack_time,N,len(d),filesize)
    else:
        print "\t"*4+"... INCORRECT"
        performance = (False, 0,0,0)

    results[test_name] = performance


def runTests():
    results = {}
    for scale in scales:
        for ts_mode in timestamp_modes:
            test(ts_mode,"uniform_dist",scale,results)
        for val_mode in value_modes:
            if val_mode is not "uniform_dist":
                test("realistic_200ms",val_mode,scale,results)
    count = 0
    num_success = 0
    best_compress = 0
    best_compress_test = ""
    worst_compress = 100.0
    worst_compress_test = ""
    avg_pack_throughput = 0
    avg_unpack_throughput = 0
    avg_compress = 0
    for t in results:
        count = count + 1
        res = results[t]
        if res[0]:
            num_success = num_success+1
        avg_pack_throughput = avg_pack_throughput + res[1]
        avg_unpack_throughput = avg_unpack_throughput + res[2]
        avg_compress = avg_compress + res[3]
        if res[3] > best_compress:
            best_compress_test = t
            best_compress = res[3]
        if res[3] < worst_compress:
            worst_compress_test = t
            worst_compress = res[3]
    avg_pack_throughput = avg_pack_throughput/count
    avg_unpack_throughput = avg_unpack_throughput/count
    avg_compress = avg_compress/count

    print "Completed %d out of %d performance tests\n" % (num_success, count)
    print "Average packing throughput: %.2f kB/s" % avg_pack_throughput
    print "Average unpacking throughput: %.2f kB/s" % avg_unpack_throughput
    print "Average compress rate: %.2f%%" % avg_compress
    print "Best compression test: %s (%.2f%%)" % (best_compress_test, best_compress)
    print "Worst compression test: %s (%.2f%%)" % (worst_compress_test, worst_compress)



