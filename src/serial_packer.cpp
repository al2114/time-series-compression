#include "serial_packer.hpp"
#include <iostream>
#include <fstream>

namespace SerialPacker {

/*
 *  SerialPacker provides pack/unpack functions to compress
 *  streamed time-series data using delta-of-delta and variable
 *  width encoding. See README for details of encoding scheme.
 */

    // Take an integer value and streams out the encoded binary
    // byte by byte litte-endian
    static void encodeVarInt(int value, std::ostream &out) {
        bool neg = value < 0;
        unsigned val = neg?-value:value;
        char byte = neg; // LSB of encoding indicating sign
        byte += (val & 0x3F) << 1; // Encode lower 6 bits
        val = val >> 6;

        while(val) { // While val is non-zero
            byte += 0x80; // Set byte MSB to indicate continuation
            out.write(&byte, 1);
            byte = val & 0x7F; // Setup byte for next 7 bits
            val = val >> 7;
        }
        out.write(&byte, 1); // Last write has MSB = 0
    }

    // Encodes a reset byte to indicate that an invalid ddelta value
    // appeared (i.e. overflow). note: 0x1 represents -0 signed magnitude
    // in the encoding scheme, hence it can be used as a special marker
    static void encodeResetByte(std::ostream &out) {
        char byte = 0x1;
        out.write(&byte, 1);
    }

    // Helper function to check for overflow when computing deltas
    static bool validDelta(int delta, int curr, int prev) {
        return (delta < curr) == (prev > 0);
    }

    void pack(std::istream &in, std::ostream &out)
    {
        int timestamp, value;
        int prev_ts = 0, prev_delta=0;
        while(in >> timestamp >> value) { // Read pair value from istream
            int delta = timestamp - prev_ts;
            if(validDelta(delta, timestamp, prev_ts)) { // Check for valid delta
                int ddelta = delta - prev_delta;
                if(validDelta(ddelta, delta, prev_delta)) {
                    encodeVarInt(ddelta, out);
                }
                else { // ddelta overflow
                    encodeResetByte(out);
                    delta = timestamp;
                    encodeVarInt(timestamp, out);
                }
            }
            else { // delta overflows
                encodeResetByte(out);
                delta = timestamp;
                encodeVarInt(timestamp, out);
            }
            encodeVarInt(value, out);
            prev_ts = timestamp;
            prev_delta = delta;
        }

    }


    // Takes and decodes a full integer from the inpput stream and outputs
    // the decoded integer to &value. Raises reset_flag if reset byte marker is
    // detected. Returns 0 if input stream is at EOF else returns 1.
    static int decodeVarInt(std::istream &in, int &value, bool &reset_flag) {
        char byte;
        bool neg;
        int offset; // Offset acts as a pointer to where in the varbuf to store the bits
        unsigned val; // Stores the value, unsigned to account INT_MIN

        // Read in first byte and check EOF
        if(in.read(&byte, 1).eof())
            return 0;

        // Detect reset marker, corresponding encodeResetFlag
        if(byte == 0x1){
            reset_flag = true;
            return 1;
        }

        // Check negative bit
        neg = byte & 1;
        val = (byte >> 1) & 0x3F; // Store next 6 bits
        offset = 6;

        while( byte & 0x80 ) { // Check continuation bit
            in.read(&byte, 1);
            val += (byte & 0x7F) << offset;
            offset += 7;
        }

        value = neg?-val:val;

        return 1;
    }

    void unpack(std::istream &in, std::ostream &out)
    {
        bool decoding_timestamp = true;
        int timestamp = 0;
        int delta = 0;
        int value = 0;

        bool reset_flag = false;

        // While istream not in EOF, read into value decoded int
        while(decodeVarInt(in, value, reset_flag)) {
            if(reset_flag) {
                timestamp = 0;
                delta = 0;
                reset_flag = false;
            }
            else {
                if(decoding_timestamp) {
                    // value is ddelta
                    delta += value;
                    timestamp += delta;
                    out << timestamp;
                }
                else {
                    out << value;
                }
                if(in.peek() != EOF)
                    out << " ";
                decoding_timestamp = !decoding_timestamp;
            }
        }
    }

}

