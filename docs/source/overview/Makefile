DIA_FILES := $(wildcard *.dia)
SVG_FILES := $(patsubst %.dia,%.svg,$(DIA_FILES))


%.svg: %.dia
	@dia --export=$@ --filter=svg $<

.PHONY: clean

clean:
	@echo Removing all generated svg files
	@rm -f $(SVG_FILES)

all: $(SVG_FILES)
	@echo Generated svg files feom dia files

html: all
