#include "serial_packer.hpp"
#include <iostream>
#include <fstream>

#define USAGE_MSG "usage: stream_packer [<src_file> || --unpack <file>] [--target <target_file>]"
#define RET_ERROR(x) std::cerr << x << std::endl; \
    std::cerr << USAGE_MSG << std::endl; \
    return -1;


int main(int argc, char *argv[])
{
    bool unpack_set = false;
    bool source_set = false;
    bool target_set = false;

    std::string input_filename = "";
    std::string output_filename = "";

    for(int i = 1; i < argc; i++) {
        std::string arg = std::string(argv[i]);

        if(arg == "-h" || arg == "--help") {
            std::cerr << USAGE_MSG << std::endl;
            return 0;
        }
        else if (arg == "-u" || arg == "--unpack") {
            if(unpack_set) {
                RET_ERROR("Cannot specify unset arg multiple times");
            }
            if(source_set) {
                RET_ERROR("Invalid argument sequence");
            }
            if(i+1 >= argc) {
                RET_ERROR("Missing arguments");
            }
            unpack_set = true;
            input_filename = std::string(argv[++i]);
        }
        else if(arg == "-o" || arg == "--output") {
            if(target_set) {
                RET_ERROR("Cannot specify output arg multiple times");
            }
            if(i+1 >= argc) {
                RET_ERROR("Missing arguments");
            }
            target_set = true;
            output_filename = std::string(argv[++i]);
        }
        else {
            if(source_set || unpack_set) {
                RET_ERROR("Invalid argument sequence");
            }
            source_set = true;
            input_filename = std::string(argv[i]);
        }
    }

    std::streambuf *inbuf, *outbuf;
    std::ifstream infile;
    std::ofstream outfile;

    if(unpack_set || source_set) {
        try {
            infile.open(input_filename);
            inbuf = infile.rdbuf();
        }
        catch(const std::ifstream::failure &e) {
            RET_ERROR("Error opening input file: " + std::string(e.what()));
        }
    }
    else {
        inbuf = std::cin.rdbuf();
    }

    if(target_set) {
        try {
            outfile.open(output_filename);
            outbuf = outfile.rdbuf();
        }
        catch(const std::ofstream::failure &e) {
            RET_ERROR("Error opening output file: " + std::string(e.what()));
        }
    }
    else if (unpack_set) {
        outbuf = std::cout.rdbuf();
    }
    else {
        try {
            outfile.open("out.pkd.bin");
            outbuf = outfile.rdbuf();
        }
        catch(const std::ofstream::failure &e) {
            RET_ERROR("Error opening output file: " + std::string(e.what()));
        }
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
