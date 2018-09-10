GXX = g++
CPPFLAGS += -std=c++11
CPPFLAGS += -O3
CPPFLAGS += -Iinclude

ODIR = obj

bin/serial_packer: obj/main.o obj/serial_packer.o
	mkdir -p bin
	$(GXX) $(CPPFLAGS) $^ -o $@

obj/%.o: src/%.cpp
	mkdir -p obj
	$(GXX) -c $(CPPFLAGS) $^ -o $@

clean:
	rm bin/serial_packer
	rm tests/*.pyc
	rm obj/*.o
	rm tmp/*

test: bin/serial_packer
	python tests/main.py
