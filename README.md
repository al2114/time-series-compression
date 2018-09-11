# serial_packer

`serial_packer` is a command-line program written in C++ that takes a stream of time-series data (as space-separated ASCII stream in the form `timestamp1(int) value1(int) timestamp2(int) value2(int) ...`) and packs/unpacks the data into/from a compressed file.

## Compiling
Run `make` to build the program, the program is built into 


## Usage
```
Usage: serial_packer [ <src> || -u <file> ] [ -o <target> ]
``` 

`serial_packer` offers two modes: pack mode (default) and unpack mode (by specifying `-u`/`--unpack` flag)

In the pack mode, if a `src` file is specified, the file will be packed from the data provided by the file. Otherwise, `serial_packer` operates on data streaming from `stdin` and terminating on `EOF`.

In unpack mode, the `-u` flag must be followed by the path to the packed file that you wish to unpack.

The `-o`/`--output` flag is an optional flag. In pack mode, it specifies the pathfile name for the packed output file, and defaults to `out.pkd.bin` if unspecified. In unpacked mode, this specifies the pathfile to write the unpacked data to, and will default to `stdout` if unspecified.
 
## Design
 
The `serial_packer` is built and designed based on the following requirements:

* Operates on data stream of integer time-value pairs
* Try to reduce the size of the data for storage
* Able to playback data quickly

These requirements imply that the packing/compression should be executed serially and overhead should be kept minimal.

#### Observations, Assumptions and Approach

The packing scheme used follows an observation/assumption that time in time-series data is, generally speaking, monotonically increasing and equally spaced. This being the case, we can therefore use a delta-of-delta approach to store the time data to reduce the integer size, and then use variable-length integer encoding (see [Wikipedia: Variable-length quantity](https://en.wikipedia.org/wiki/Variable-length_quantity)) which offers a more compact storage scheme when dealing with smaller integers than standard 32-bit encoding.

#### Delta-of-delta & variable-length encoding implementation

The encoding scheme assumes that the input follows the specification where the first and every odd item in the stream represents the timestamp, and is a valid int (based on the system). Timestamps and deltas of the previous item are kept track of to calculate the delta-of-delta for every timestamp value and encoded variable-length. This means that the first stored timestamp indicates the first value, the second item stores the delta to this value, and all subsequent items hold the offsets to this delta.

The variable-length encoding implementation breaks the integer into chunks of 7-bits from the LSB up. This is then stored in a byte where the MSB indicates whether the next byte is part of the same integer value (i.e. a continuation bit). The integer value is iteratively packed into these 7-bit bytes until subsequent bits equal 0, for which the MSB will then be set to 0 for the most significant byte. Packed bytes are stored little-endian for algorithmic simplicity when encoding and decoding.

In order to handle negative numbers, we encode the LSB of the first byte with a `1` to indicate negative or `0` if positive. Therefore the first byte only stores the first 6 bits of the value and all subsequent bytes storing 7 bits.

#### Overflow handling

It is noteworthy when dealing with delta-of-deltas, we may encounter an overflow (e.g. calculating the delta of `INT_MAX - INT_MIN = 2*INT_MAX+1`), as such, we have a marker bit of `0x1` to indicate a reset is required (i.e. we reset the tracked timestamps and deltas, and the timestamp value that causes the overflow is encoded directly instead of as a delta-of-delta as the first in a chain of deltas).

`0x1` is used for this special case as we observe in the encoding scheme, the continuation bit `0` indicates the completion of a number of magnitude `0` and the LSB indicates negative (i.e. `-0`) which would never appear, hence can act as our special case marker.

#### Discussion

It is noted that variable-length encoding scheme will not always save on space as extra bits are used for the continuation and negative bits. However, this occurs only in the worst case of stored integers (delta-of-delta times or values) exceeding 27-bits, where 5-bytes are required to store a 32-bit integer implying a worst case overhead of 25%. However in the best case where values are less than 7-bits, the data can be stored in a quarter of the original size indicating 75% savings. As most time-series data is monotonically increasing a steady rate, this value should be close to zero.

The delta strategy may also be taken advantage of to packing the data value if we knew that the time-series data has some time associativity between consecutive data (e.g. sensor data). However, this is not always the case (e.g. random data) and so delta was not implemented for the data values.



 
## Testing

An integrated test-suite is provided written in Python. To run the tests, run `make test`.

#### Functional test

The functional tests assert the correctness of the program by testing various time-value pair inputs. The tests inlcude:

* `test_basic` – checks the program's fundamental functionality
* `test_negatives` – checks negative values works
* `test_zeros` – checks zero works
* `test_neg_one` – checks -1 (or 0xFFFFFFFF) works
* `test_max_int` – checks 2^31-1 works
* `test_min_int` – checks -2^31 works
* `test_consecutive_limits` – checks varying consecutive values between extreme limits work
* `test_empty` – checks empty stream can be handled
* `test_unordered_time` – checks out of order time stamps do not change behaviour
* `test_negative_time` – check that negative time can be handled
* `test_large` – tests 200,000 random time-value pairs work
* `test_stream_in_out`, `test_file_input`, `test_file_output`, `test_file_in_out` checks all combinations of IO interaction with the interface

These test cases can be found in `tests/test_correctness.py`

#### Performance test

Performance testing follows the requirements according to the following metrics:

* **Correctness** – does it work
* **Average packing throughput** – calculated as `BYTES_OF_DATA/TOTAL_PACK_TIME` in kB/s
* **Average packing latency** – calculated as `TOTAL_TIME/NUMBER_OF_DATAPAIRS" in microseconds per pair
* **Average unpacking throughput** – calculated as `BYTES_OF_DATA/TOTAL_UNPACK_TIME` in kB/s
* **Average unpacking latency** – calculated as `TOTAL_TIME/NUMBER_OF_DATAPAIRS" in microseconds per unpacked pair
* **Compression ratio** – calculated as `100 * (1 - PACKED_SIZE/ORIGINAL_SIZE)`

Each test case tries to model sensible data that the system may encounter, and performs each case in `small`, `medium` and `big` sizes defined in `test/tests_performance.py`. These sizes are `1000`, `15000` and `100000` time-value datapairs respectively. Python's `testit` module is used to perform timing analyses in order to calculate the above metric.

Each test is performed 10 times to take an average of measured times. It is noteworthy that the larger tests are more representative of the algorithmic throughput as there is some constant overhead to setup the program contributing to the timing.


##### Timestamp test cases
* `random` – Generates uniform random timestamps between `[INT_MIN, INT_MAX]`
* `ideal` – Generates linear range of increasing values from 0 to `INT_MAX`
* `realistic_xms` – Generates linear range of values increases by `x` with a standard deviation of `x/10` and an offset of 100000. This simulates imperfectly timed series readings, but generally in-order.
* `realistic_bad_xms` – Generates linear range of values increases by `x` with a standard deviation of `x/2` and an offset of 100000. This simulates imperfect timed series readings such as bad network packets, and may be out-of-order.

These timestamp cases are tested with a `uniform` random distribution of value  as a performance benchmark.

##### Value test cases
* `normal_dist` – Genereates zero mean normally distributed values with a standard deviation of 250,000
* `uniform_dist` – Generates uniformly randomly distributed integers between [INT_MIN, INT_MAX]
* `positive_dist` – Generates squared normal positive distribution (by squaring normally distributed values having 10000 standard dev.)
* `negative_dist` – Negative of the squared normal distribution
* `moving_signal` – A moving signal that changes based on a changing delta (initially 10 per timestep, varying per unit by a standard deviation of 2), simulating a natural signal
* `random_spike` – Normally distributed data except with a 5% chance that it may spike significantly higher than the distribution. Simulates network/communication data, where there are short random occurences of a high value (e.g. lag, traffic etc.).
* `noisy_periodic` – A 10000 amplitude 100 period sine wave with 1000 std noise, simulating sensor data

These values are tested with `realistic_20ms` as a performance benchmark.

##### Performance results

Using `realistic_20ms` timestamp and `moving_signal` as a benchmark on `big` set tested on a 2.8GHz Intel Core i7 we observe the following results:

* Packing throughput: 2348.86kB/s
* Unpacking throughput: 2809.63kB/s
* Compression ratio: 71.24%


## Future work

The current iteration of the packing scheme explores the use of delta-of-deltas packing of timestamp and variable-length encoding in 7-bit groups. This approach demonstrates how predeterminitive knowledge of the data can aid in coming up with a more efficient packing strategy.

However, it is impossible to preemptively determine a lot of qualities regarding the data. However, further optimisations may be made by performing an data analysis step in order to determine packing strategy.

In this apparoach, we may choose to utilise or not to utilise delta schemes or perform variable-length encoding in a different size of bitgroups (to optimise between overhead and packing resolution) depending on the size and distribution of the time-series data.

This would be perfectly valid as the requirements only concerns fast unpacking, and so this step would come at a cost of extra time taken to pack and extra complexity.

In terms of unpacking throughput, it is not hard to imagine the task can be parallelised to be processed on multiple cores, however may require some tweaking in implementation to accomodate for dependencies.
