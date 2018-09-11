#!/usr/bin/python
import tests_correctness
import tests_performance
import sys

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
    tests_correctness.runTests()

    printTitle("Testing performance on different data models")
    tests_performance.runTests()


