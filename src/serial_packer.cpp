#include "serial_packer.hpp"
#include <iostream>
#include <fstream>

namespace SerialPacker {

    static void encodeVarInt(int val, std::ostream &out);
    static int decodeVarInt(std::istream &in, int &value);

    void pack(std::istream &in, std::ostream &out)
    {
        int timestamp, value;
        int prev_ts = 0, prev_delta=0;
        while(in >> timestamp >> value) {
            int delta = timestamp - prev_ts;
            int ddelta = delta - prev_delta;
            encodeVarInt(ddelta, out);
            encodeVarInt(value, out);
            prev_ts = timestamp;
            prev_delta = delta;
        }

    }
    void unpack(std::istream &in, std::ostream &out)
    {
        bool decoding_timestamp = true;
        int timestamp = 0;
        int delta = 0;
        int value = 0;

        while(decodeVarInt(in, value)) {
            if(decoding_timestamp) {
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

    static void encodeVarInt(int val, std::ostream &out) {
        bool neg = val < 0;
        if (neg)
            val = -val; // Ensure val represents magnitude
        char byte = neg; // LSB of encoding indicating sign
        byte += (val & 0x3F) << 1; // Encode lower 6 bits
        val = val >> 6;

        while(val) { // If there are more bits
            byte += 0x80; // Set byte MSB to indicate continuation
            out.write(&byte, 1);
            byte = val & 0x7F; // Setup byte for next 7 bits
            val = val >> 7;
        }
        out.write(&byte, 1);
    }

    static int decodeVarInt(std::istream &in, int &value) {
        char byte;
        bool neg;
        int offset;

        if(in.read(&byte, 1).eof())
            return 0;

        neg = byte & 1;
        value = (byte >> 1) & 0x3F;
        offset = 6;

        while( byte & 0x80 ) {
            in.read(&byte, 1);
            value += (byte & 0x7F) << offset;
            offset += 7;
        }

        if(neg)
            value = -value;

        return 1;
    }
}

