#include "serial_packer.hpp"
#include <iostream>
#include <fstream>

using namespace std;

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
