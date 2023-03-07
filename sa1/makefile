all: make_formatter.o run_formatter

make_formatter.o: make_formatter.c make_formatter.h
	gcc -c $<

run_formatter: run_formatter.c make_formatter.o
	gcc -o $@ $^

clean:
	rm -rf *.o run_formatter

