"""Per-venue parsers — one file per host, and as few of them as possible.

The standing rule is that a source needing a per-venue special case is a source
we do not take, because such a parser fails SILENTLY the day the venue redesigns:
finding nothing is exactly what a venue with nothing on looks like, and the run
is unattended. Scott chose to make one exception on 7 Sep 2026, for Geelong Arts
Centre — the region's biggest venue, several sessions a day that no feed carries,
and a page that prints a weekday beside every date to checksum against.

Three guards make an exception bearable, and every parser here must keep them:
  1. it is keyed by HOST in PARSERS, so it can only ever run against one site;
  2. it refuses any date whose printed weekday does not match (from_listing's
     rule), so a page cannot mis-date a row by mistake;
  3. it remembers how many events it found last time in parser_counts.json,
     and finding ZERO where it found some before is reported as `failed`, which
     run_log.py colours red — never as a quiet venue.

scrape_venues.py consults PARSERS before its own strategy ladder and takes the
parser's answer as complete.
"""
from . import geelongartscentre

WRITE = False           # set by scrape_venues.main from --write; gates the ledger

PARSERS = {
    'geelongartscentre.org.au': geelongartscentre.read,
}
