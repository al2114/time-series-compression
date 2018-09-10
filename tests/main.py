#!/usr/bin/python
import tests_correctness

test_sizes = {
    "small": 256,
    "medium": 4096,
    "big": 32768
    }

if __name__ == "__main__":

    print "* * * * * * * * * * * * *"
    print "Testing for correctness"
    print "* * * * * * * * * * * * *"

    for test in tests_correctness.tests:
        print "Test case: " + test.__name__,
        test()
        print "... PASSED"


