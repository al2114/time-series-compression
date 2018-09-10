#include "serial_packer.hpp"
#include <iostream>
#include <fstream>

namespace SerialPacker {

    static void encodeVarInt(int value, std::ostream &out) {
        bool neg = value < 0;
        unsigned val = neg?-value:value;
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

    static void encodeResetByte(std::ostream &out) {
        char byte = 0x1;
        out.write(&byte, 1);
    }

    void pack(std::istream &in, std::ostream &out)
    {
        int timestamp, value;
        int prev_ts = 0, prev_delta=0;
        while(in >> timestamp >> value) {
            int delta = timestamp - prev_ts;
            if((delta < timestamp) == (prev_ts > 0)) { // Check for valid delta
                int ddelta = delta - prev_delta;
                if((ddelta < delta) == (prev_delta > 0)) {
                    encodeVarInt(ddelta, out);
                }
                else {
                    //ddleta overflow
                    encodeResetByte(out);
                    delta = 0;
                    encodeVarInt(timestamp, out);
                }
            }
            else {
                // delta overflow
                encodeResetByte(out);
                delta = 0;
                encodeVarInt(timestamp, out);
            }
            encodeVarInt(value, out);
            prev_ts = timestamp;
            prev_delta = delta;
        }

    }

    static int decodeVarInt(std::istream &in, int &value, bool &reset_flag) {
        char byte;
        bool neg;
        int offset;
        unsigned val;

        if(in.read(&byte, 1).eof())
            return 0;
        if(byte == 0x1){
            reset_flag = true;
            return 1;
        }

        neg = byte & 1;
        val = (byte >> 1) & 0x3F;
        offset = 6;

        while( byte & 0x80 ) {
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

        while(decodeVarInt(in, value,reset_flag)) {
            if(reset_flag) {
                timestamp = 0;
                delta = 0;
                reset_flag = false;
            }
            else {
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
    }

}

