#include <vector>
#include <iostream>
#include <fstream>

using namespace std;

void packInt(int val, ostream &out) {
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

void pack(istream &in, ostream &out)
{
    int timestamp, value;
    int prev = 0;
    while(cin >> timestamp >> value) {
        int ts_delta = timestamp - prev;
        packInt(ts_delta, out);
        packInt(value, out);
        prev = timestamp;
    }

}

void unpack(istream &in, ostream &out)
{
    char byte;
    int timestamp = 0;
    bool decoding_timestamp = true;


    bool is_start = true;
    bool neg = false;
    int value = 0;
    int offset = 0;

    while(cin >> byte) {
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


#define USAGE_MSG "usage: stream_packer [--unpack <file> || --src <binary>] [--target <target_file>]"

int main(int argc, char *argv[])
{
    bool unpack_set = false;
    bool source_set = false;
    bool target_set = false;
    //ifstream *is = &stdin;
    string input_filename = "";

    string output_filename = "";

    for(int i = 1; i < argc; i++) {
        string arg = string(argv[i]);

        if(arg == "-h" || arg == "--help") {
            cout << USAGE_MSG << endl;
            return 0;
        }
        else if (arg == "-u" || arg == "--unpack") {
            if(unpack_set) {
                cerr << "Cannot specify unset arg multiple times" << endl;
                cerr << USAGE_MSG << endl;
                return -1;
            }
            if(source_set) {
                cerr << "Cannot specify source arg in conjunction with unset" << endl;
                cerr << USAGE_MSG << endl;
                return -1;
            }
            if(i+1 >= argc) {
                cerr << "Not enough arguments provided" << endl;
                return -1;
            }
            unpack_set = true;
            input_filename = string(argv[++i]);
        }
        else if(arg == "-s" || arg == "--src") {
            if(unpack_set) {
                cerr << "Cannot specify src arg multiple times" << endl;
                cerr << USAGE_MSG << endl;
                return -1;
            }
            if(unpack_set) {
                cerr << "Cannot specify source arg in conjunction with unset" << endl;
                cerr << USAGE_MSG << endl;
                return -1;
            }
            if(i+1 >= argc) {
                cerr << "Not enough arguments provided" << endl;
                return -1;
            }
            source_set = true;
            input_filename = string(argv[++i]);
        }
        else if(arg == "-t" || arg == "--target") {
            if(target_set) {
                cerr << "Cannot specify target arg multiple times" << endl;
                cerr << USAGE_MSG << endl;
                return -1;
            }
            if(i+1 >= argc) {
                cerr << "Not enough arguments provided" << endl;
                return -1;
            }
            target_set = true;
            output_filename = string(argv[++i]);
        }
        else {
            cerr << "Unknown argument sequence" << endl;
            cerr << USAGE_MSG << endl;
            return -1;
        }
    }

    streambuf *inbuf, *outbuf;
    ifstream infile;
    ofstream outfile;

    if(unpack_set || source_set) {
        infile.open(input_filename);
        inbuf = infile.rdbuf();
    }
    else {
        inbuf = cin.rdbuf();
    }

    if(target_set) {
        outfile.open(output_filename);
        outbuf = outfile.rdbuf();
    }
    else if (unpack_set) {
        outbuf = cout.rdbuf();
            }
    else {
        outfile.open("out.pkd.bin");
        outbuf = outfile.rdbuf();
    }

    istream in(inbuf);
    ostream out(outbuf);

    if(unpack_set) {
       unpack(in, out);
    }
    else {
       pack(in, out);
    }

    return 0;
}
