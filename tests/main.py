#!/usr/bin/python
import tests_correctness

test_sizes = {
    "small": 256,
    "medium": 4096,
    "big": 32768
    }


def printTitle(title):
    print ""
    print "-" * len(title)
    print title
    print "-" * len(title)

if __name__ == "__main__":

    printTitle("Testing functional correctness")

    for test in tests_correctness.tests:
        print "Test case: " + test.__name__,
        test()
        print "... PASSED"

    n = len(tests_correctness.tests)
    print "\nSuccessfully passed " + str(n) + " out of " + str(n) + " tests";

    printTitle("Correctness and performance tests on different models")


