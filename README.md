PubMed Author Evaluation
========================
[![DOI](https://zenodo.org/badge/123303534.svg)](https://zenodo.org/badge/latestdoi/123303534)


A selection of Python scripts for automatic search of biomedical publications followed by extraction and processing of information about their authors using the [PubMed](https://europepmc.org/) database.

## Background

The goal of this project is to identify individual actors in the public debate of scientific issues and to determine their position within science. It specifically aims to establish:

1. whether an actor can be considered a ***contributing expert*** in a given **subject area** as demonstrated through published research papers
2. whether an actor can be considered a ***contributing expert***, but has **not** published research papers in a given **subject area**


## Installation and execution

See: [Python Installation und Ausführung](docs/python/Installation_und_Ausfuehrung.md) (german)

## Procedure

![Flow Chart Grafik](docs/flow-chart.jpg)

#### Manual: Adjustment of input files
- Add topics (`topic.csv`)
- Add actors in CSV file

#### Automatic via get_actors_publications.py
- Collects all publications for every actor (via PubMed)
- Filters publications (via `journal_ranking.csv`)
- Generates author file for every actor
	- one row = one publication

#### Manual: Review of output
- Review generated author files
	- Particularly the values `Active` and `Authorship Confidence`
- Adjust input files if necessary
	- Adjust search string for topic/actors
	- In case of automatic authorship rating: improve lists `Location` and `Institution`
	- On changes: Execute `get_actors_publications.py` again

#### Automatic via calc_authors_results.py
- Uses all author files
- Generates complete list with all authors and their metrics
	- one row = one author

Both scripts ask for the topic (see `topics.csv`) upon launch and whether publications should be retrieved using the name or [ORCID](https://orcid.org/) of the author.

## In- and output

### *INPUT* folder

The *INPUT* folder contains all lists with actors and the journal ranking. Of importance here is the file `topics.csv` as it is the so-called configuration file for the scripts.

#### topics.csv

File format: csv  
First row: column names  
Following rows: **one row = one topic**

- `short` – an acronym for the topic, used upon script launch

- `search string` – search string is the way to check whether a research paper was published in a specific subject area. A search in PubMed is initiated, which contains the publication ID and this search string. (see code for further details)

- `actors list file` – file name of the lists of actors in a given subject area


#### Lists of actors

File format: csv  
First row: column names  
Following rows: **one row = one actor**

- `AktID` – unique ID of an actor
- `Name` – precise name of a person
- `Position` (optional)
- `Institution` (optional)
- `Label` (optional, e.g. doctor, expert, researcher)
- `InstitutionList` – list of institutions at which the actor published research papers (for automatic authorship evaluation)
- `LocationList` – list of known cities/countries in which the actor published research papers (for automatic authorship evaluation)
- `PubMedSearch` – search string used to identify person in PubMed. Simple string or [complex query](https://europepmc.org/Help#mostofsearch).


#### journal-ranking.csv
Export from [Scimago Journal & Country Rank](http://www.scimagojr.com/journalrank.php)


### *OUTPUT* folder

- `author_[topic]/` subfolder – contains all author files of the specified topic.

- `result_[topic].csv` – contains final evaluation for all authors of a the specified topic.


#### Autordateien

File format: csv  
First row: column names  
Following rows: **one row = one publication**

- `Active` – 0 or 1. Controls whether publication will be considered in the complete evaluation of a subject area.
- `Authorship Confidence` – Result of an automatic authorship evaluation. (see below)
- `ID (LINK)` – ID of publication in PubMed database. It is linked and can be opened with Ctrl+Click.
- `Topic` – Acronym of subject area: if the publication could be assigned to the subject area (via subject area search string).
- `Title` – Title of publication
- `Citations` – Number of citations in other publications
- `Date` – Date of publication
- `Author Position` – first/middle/last
- `Co-Author count` – Number of coauthors


## Automatic authorship evaluation

Because the data in the PubMed databank are inconsistent, the algorithm cannot always assure that the person (the actor) under consideration is, in fact, the author of the found research paper or it is, for instance, a person with similar initials.

To address this issues, the script `get_actors_publications.py` facilitates an automatic evaluation of the authorship. This can be turned on or off upon launch.

There are indicators that increase the confidence over the authorship.
When applies, the number will be added to the `Authorship Confidence` value.

- `+0.4` – Firstname matches
- `+0.3` – an institution matches
- `+0.2` – a location matches

The data about *institution* and *location* will be fed from the list of authors. The more data is available in the list, the more significant is the `Authorship Confidence` value.

The `Authorship Confidence` value has a direct impact on the `Active` value. Should the `Authorship Confidence` be equal zero, so the `Active` will also be set to zero. In this case, it is necessary **to review the authorship manually** again. Should the person under consideration be the author of publication, it is necessary to add *institution* and *location* to the list of actors. This ensures a better `Authorship Confidence` value in the next run of the script.  


# License
- **Conception:** Prof. Dr. Markus Lehmkuhl (KIT & FU Berlin), Dr. Evgeniya Boklage (FU Berlin)
- **Implementation:** Yannick Milhahn (TU Berlin & FU Berlin)

Distributed under GPLv3 License.
See [LICENSE](LICENSE) for more information.
