#ifndef SERIAL_PACKER_HPP
#define SERIAL_PACKER_HPP

#include <iostream>

namespace SerialPacker {
    void pack(std::istream &in, std::ostream &out);
    void unpack(std::istream &in, std::ostream &out);
}

#endif
