.PHONY:all clean

PATH_ROOT := ..
PATH_DOC := $(PATH_ROOT)/doc
README := $(PATH_ROOT)/README.md

SOURCES := $(addprefix $(PATH_DOC)/,sequence.uml class.uml database.uml)
DESTS := $(SOURCES:%.uml=%.png)

all:readme uml

clean:
	rm -f *.png

.PHONY:readme uml

README_RST := $(README:%.md=%.rst)

readme:$(README_RST)

$(README_RST):$(README)
	@pandoc --from=markdown --to=rst -o $(@) $(<)

uml:$(DESTS)

%.png:%.uml
	@plantuml -tpng $(<)
