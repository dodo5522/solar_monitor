.PHONY:all clean

PATH_ROOT := ..
PATH_DOC := $(PATH_ROOT)/doc
README := $(PATH_ROOT)/README.md
SEQUENCE := $(PATH_DOC)/sequence.uml
CLASS := $(PATH_DOC)/class.uml
DATABASE := $(PATH_DOC)/database.uml

all:readme uml

clean:
	rm -f *.png

.PHONY:readme uml

README_RST := $(README:%.md=%.rst)

readme:$(README_RST)

$(README_RST):$(README)
	@pandoc --from=markdown --to=rst -o $(@) $(<)

SEQUENCE_PNG := $(SEQUENCE:%.uml=%.png)
CLASS_PNG := $(CLASS:%.uml=%.png)
DATABASE_PNG := $(DATABASE:%.uml=%.png)

uml:$(SEQUENCE_PNG) $(CLASS_PNG) $(DATABASE_PNG)

%.png:%.uml
	@plantuml -tpng $(<)
