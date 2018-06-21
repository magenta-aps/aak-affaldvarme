DIA_FILES := $(wildcard *.dia)
SVG_FILES := $(patsubst %.dia,%.svg,$(DIA_FILES))


%.svg: %.dia
	dia --export=$@ --filter=svg $<

all: $(SVG_FILES)
	@echo exported diagrams
