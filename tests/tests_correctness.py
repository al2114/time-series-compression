import data_generator as data
from packer_caller import pack, packFromFile, unpack, unpackToFile

#
#  Basic functional correctness tests
#

def test_basic():
    test_name = "test_basic"

    ts = [10, 20, 30]
    vals = [123, 456, 789]
    d = data.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_negatives():
    test_name = "test_negatives"

    ts = [10, 20, 30]
    vals = [-123, -456, -789]
    d = data.serialize(ts,vals)

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
    d = data.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_neg_one():
    test_name = "test_neg_one"

    ts = [10, 20, 30]
    vals = [-1]*3
    d = data.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"


def test_max_int():
    test_name = "test_max_int"

    ts = [10, 20, 30]
    vals = [data.MAX_INT]*3
    d = data.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_min_int():
    test_name = "test_min_int"

    ts = [10, 20, 30]
    vals = [data.MIN_INT]*3
    d = data.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_consecutive_limits():
    test_name = "test_consecutive_limits"

    ts = [data.MAX_INT, data.MIN_INT, data.MAX_INT, data.MIN_INT]
    vals = [data.MAX_INT, data.MIN_INT, data.MAX_INT, data.MIN_INT]
    d = data.serialize(ts,vals)

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
#  Testing
#

def test_unordered_time():
    test_name = "test_unordered_time"

    ts = [20, 10, 30, 90, 25, 40]
    vals = [123, 456, 789, 987, 654, 321]
    d = data.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"


def test_negative_time():
    test_name = "test_negative_time"

    ts = [-10, -20, -30]
    vals = [123, 456, 789]
    d = data.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

def test_large():
    test_name = "test_large"

    ts = data.gen_interval(100000, 300, 1000000)
    vals = data.gen_random_ints(100000)
    d = data.serialize(ts,vals)

    filepath = "tmp/"+test_name+"pkd.bin"

    pack(d, filepath)
    output = unpack(filepath)

    assert output == d, test_name + " failed"

#
#  Testing different IO combinations
#

#def test_stream_in_out():
#def test_file_input():
#def test_file_output():
#def test_file_in_out():


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
        test_large
#        test_stream_in_out,
#        test_file_input,
#        test_file_output,
#        test_file_in_out
        ]
