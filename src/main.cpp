#include "serial_packer.hpp"
#include <iostream>
#include <fstream>

#define USAGE_MSG "usage: stream_packer [--unpack <file> || --src <binary>] [--target <target_file>]"

int main(int argc, char *argv[])
{
    bool unpack_set = false;
    bool source_set = false;
    bool target_set = false;
    //std::ifstream *is = &stdin;
    std::string input_filename = "";

    std::string output_filename = "";

    for(int i = 1; i < argc; i++) {
        std::string arg = std::string(argv[i]);

        if(arg == "-h" || arg == "--help") {
            std::cout << USAGE_MSG << std::endl;
            return 0;
        }
        else if (arg == "-u" || arg == "--unpack") {
            if(unpack_set) {
                std::cerr << "Cannot specify unset arg multiple times" << std::endl;
                std::cerr << USAGE_MSG << std::endl;
                return -1;
            }
            if(source_set) {
                std::cerr << "Cannot specify source arg in conjunction with unset" << std::endl;
                std::cerr << USAGE_MSG << std::endl;
                return -1;
            }
            if(i+1 >= argc) {
                std::cerr << "Not enough arguments provided" << std::endl;
                return -1;
            }
            unpack_set = true;
            input_filename = std::string(argv[++i]);
        }
        else if(arg == "-s" || arg == "--src") {
            if(unpack_set) {
                std::cerr << "Cannot specify src arg multiple times" << std::endl;
                std::cerr << USAGE_MSG << std::endl;
                return -1;
            }
            if(unpack_set) {
                std::cerr << "Cannot specify source arg in conjunction with unset" << std::endl;
                std::cerr << USAGE_MSG << std::endl;
                return -1;
            }
            if(i+1 >= argc) {
                std::cerr << "Not enough arguments provided" << std::endl;
                return -1;
            }
            source_set = true;
            input_filename = std::string(argv[++i]);
        }
        else if(arg == "-t" || arg == "--target") {
            if(target_set) {
                std::cerr << "Cannot specify target arg multiple times" << std::endl;
                std::cerr << USAGE_MSG << std::endl;
                return -1;
            }
            if(i+1 >= argc) {
                std::cerr << "Not enough arguments provided" << std::endl;
                return -1;
            }
            target_set = true;
            output_filename = std::string(argv[++i]);
        }
        else {
            std::cerr << "Unknown argument sequence" << std::endl;
            std::cerr << USAGE_MSG << std::endl;
            return -1;
        }
    }

    std::streambuf *inbuf, *outbuf;
    std::ifstream infile;
    std::ofstream outfile;

    if(unpack_set || source_set) {
        infile.open(input_filename);
        inbuf = infile.rdbuf();
    }
    else {
        inbuf = std::cin.rdbuf();
    }

    if(target_set) {
        outfile.open(output_filename);
        outbuf = outfile.rdbuf();
    }
    else if (unpack_set) {
        outbuf = std::cout.rdbuf();
            }
    else {
        outfile.open("out.pkd.bin");
        outbuf = outfile.rdbuf();
    }

    std::istream in(inbuf);
    std::ostream out(outbuf);

    if(unpack_set) {
        SerialPacker::unpack(in, out);
    }
    else {
        SerialPacker::pack(in, out);
    }

    if(infile.is_open()) infile.close();
    if(outfile.is_open()) outfile.close();


    return 0;
}
