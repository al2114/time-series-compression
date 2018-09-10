import data_generator as datagen
from packer_caller import pack, packFromFile, unpack, unpackToFile

#
#  Basic functional correctness tests
#

def test_basic():
    test_name = "test_basic"

    ts = [10, 20, 30]
    vals = [123, 456, 789]
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_negatives():
    test_name = "test_negatives"

    ts = [10, 20, 30]
    vals = [-123, -456, -789]
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

#
#  Input limit tests
#
def test_zeros():
    test_name = "test_zeros"

    ts = [10, 20, 30]
    vals = [0]*3
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_neg_one():
    test_name = "test_neg_one"

    ts = [10, 20, 30]
    vals = [-1]*3
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"


def test_max_int():
    test_name = "test_max_int"

    ts = [10, 20, 30]
    vals = [datagen.MAX_INT]*3
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_min_int():
    test_name = "test_min_int"

    ts = [10, 20, 30]
    vals = [datagen.MIN_INT]*3
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_consecutive_limits():
    test_name = "test_consecutive_limits"

    ts = [datagen.MAX_INT, datagen.MIN_INT, datagen.MAX_INT, datagen.MIN_INT]
    vals = [datagen.MAX_INT, datagen.MIN_INT, datagen.MAX_INT, datagen.MIN_INT]
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_empty():
    test_name = "test_empty"

    filepath = "tmp/"+test_name+"pkd.bin"
    pack("", filepath)
    output = unpack(filepath)

    assert output == "", test_name + " failed"

#
#  Valid unusual stream behaviour test
#

def test_unordered_time():
    test_name = "test_unordered_time"

    ts = [20, 10, 30, 90, 25, 40]
    vals = [123, 456, 789, 987, 654, 321]
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"


def test_negative_time():
    test_name = "test_negative_time"

    ts = [-10, -20, -30]
    vals = [123, 456, 789]
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

#
#  Scale test
#

def test_large():
    test_name = "test_large"

    ts = datagen.gen_interval(200000, 300, 1000000)
    vals = datagen.gen_random_ints(200000)
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"
#
#  Different interface IO combinations tests
#

def test_stream_in_out():
    test_name = "test_stream_in_out"

    ts = datagen.gen_random_ints(100)
    vals = datagen.gen_random_ints(100)
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"


def test_file_input():
    test_name = "test_file_input"

    ts = datagen.gen_random_ints(100)
    vals = datagen.gen_random_ints(100)
    d = datagen.serialize(ts,vals)


    infile = "tmp/"+test_name+".bin"
    filepath = "tmp/"+test_name+"pkd.bin"

    with open(infile,'w') as f:
        f.write(d)

    packFromFile(infile, filepath)
    output = unpack(filepath)

    with open(infile,'r') as f:
        dfile = f.read()

    assert output == dfile, test_name + " failed"

def test_file_output():
    test_name = "test_file_output"

    ts = datagen.gen_random_ints(100)
    vals = datagen.gen_random_ints(100)
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"
    outfile= "tmp/"+test_name+".out"

    pack(d, filepath)
    unpackToFile(filepath, outfile)

    with open(outfile) as f:
        output = f.read()

    assert output == d, test_name + " failed"




def test_file_in_out():
    test_name = "test_file_output"

    ts = datagen.gen_random_ints(100)
    vals = datagen.gen_random_ints(100)
    d = datagen.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"
    infile = "tmp/"+test_name+".bin"
    outfile= "tmp/"+test_name+".out"

    with open(infile,'w') as f:
        f.write(d)

    packFromFile(infile, filepath)
    unpackToFile(filepath, outfile)

    with open(infile,'r') as f:
        dfile = f.read()
    with open(outfile) as f:
        output = f.read()

    assert output == dfile, test_name + " failed"






tests = [
        test_basic,
        test_negatives,
        test_zeros,
        test_max_int,
        test_min_int,
        test_consecutive_limits,
        test_empty,
        test_unordered_time,
        test_negative_time,
        test_large,
        test_stream_in_out,
        test_file_input,
        test_file_output,
        test_file_in_out
        ]
