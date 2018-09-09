#include "serial_packer.hpp"
#include <iostream>
#include <fstream>

namespace SerialPacker {
    static void packInt(int val, std::ostream &out) {
        bool neg = val < 0;
        if (neg)
            val = -val; // Ensure val represents magnitude
        char byte = neg; // LSB of encoding indicating sign
        byte += (val & 0x3F) << 1; // Encode lower 6 bits
        val = val >> 6;

        while(val) { // If there are more bits
            byte += 0x80; // Set byte MSB to indicate continuation
            out << byte; // Output encoded byte to stream
            byte = val & 0x7F; // Setup byte for next 7 bits
            val = val >> 7;
        }
        out << byte;

    }

    void pack(std::istream &in, std::ostream &out)
    {
        int timestamp, value;
        int prev = 0;
        while(in >> timestamp >> value) {
            int ts_delta = timestamp - prev;
            packInt(ts_delta, out);
            packInt(value, out);
            prev = timestamp;
        }

    }

    void unpack(std::istream &in, std::ostream &out)
    {
        char byte;
        int timestamp = 0;
        bool decoding_timestamp = true;


        bool is_start = true;
        bool neg = false;
        int value = 0;
        int offset = 0;

        while(in >> byte) {
            if(is_start) {
                is_start = false;
                neg = byte & 1;
                value = (byte>>1) & 0x3F;
                offset += 6;
            }
            else {
                value += (byte & 0x7F) << offset;
                offset += 7;
            }

            if((byte & 0x80) == 0) {
                if(neg)
                    value = -value;
                if(decoding_timestamp) {
                    timestamp += value;
                    out << timestamp;
                }
                else {
                    out << value;
                }
                value = 0;
                offset = 0;
                is_start = true;
                decoding_timestamp = !decoding_timestamp;
            }
        }
    }
}

