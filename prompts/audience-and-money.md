# audience and money — a research pass, not a listings pass

The other prompts in this folder produce rows or source inventories. This one
produces **a report**: how a site like Notice finds readers, and which ways of
earning from it are real at this size, on this coast, without breaking what the
About page promises.

It writes nothing to the database and changes no code. Its nearest relative is
the nature-sources pass — evidence gathered, each claim checked, the refusals
kept — pointed at a business question instead of a data one.

The numbers inside the block were read off the live database on 4 Oct 2026.
Re-count before trusting them later.

---

```text
═══ GETTING THE REPO — DO THIS FIRST ═══

Clone it. Do not go looking for a folder on the Mac.

  git clone https://github.com/Scott-Designed/whattodo.git
  cd whattodo

Public repo, anonymous clone, no key needed. You never write to the database, never need
.env, and change no code. You produce ONE file: prompts/log/audience-and-money.md. If you
cannot push, say so and hand the file back in the chat in full.

═══ WHAT YOU ARE RESEARCHING ═══

Notice (https://notice.place) is a community listings site for Jan Juc, the Surf Coast,
Geelong and the Bellarine, in Victoria, Australia. One person runs it: Scott, a designer.
The repo is called `whattodo`; the product is called Notice.

Two questions, in this order, because the second depends on the first:

  1. AUDIENCE   How does a local what's-on site actually get readers, and keep them?
  2. MONEY      Which ways of earning from it are real, at what audience size, and at what
                cost to the thing itself?

Scott has not said how much he wants it to earn. Do not guess and do not ask — answer for
three levels and let him pick:

  A  it pays its own running costs
  B  it pays for the hours that go into it (a day a week, say)
  C  it is a small business

═══ READ FIRST, IN THIS ORDER ═══

1. public/about.html — "what this is, and what it will not do". Every recommendation has
   to survive this page. It promises no account, nothing to sign up for, no guessing, and
   "the thing you would actually tell a friend, not tourist copy".

2. CLAUDE.md — long, and worth it. For this job read at least: the top "Shape of it"
   block, "Six kinds of listing", "Two meters", "Nothing reaches the board unapproved",
   "The nav bar, and the pages behind it", "A listing needs its own page", and "The email
   inbox". It is the record of what was decided and why.

3. The live site. Open /, /noticeboard, /torquay, /surfing, /second-hand, /about on a
   phone-width window. Judge it as a stranger would.

═══ WHAT NOTICE HAS TODAY — THE ASSETS ═══

  1,341 published listings      589 dated events, 324 venues, 230 spots, 62 at-home ideas
  136 kept OFF the board        68 shops, 12 makers, 56 groups — reference rows that only
                                appear on type and town pages. Nobody has decided what
                                these are FOR commercially. That is part of your job.
  ~50 town pages, 44 type pages /anglesea, /surfing — each with its own title and
                                description in the HTML, so they preview and index
  Automated intake              four scrapers Mon + Thu, a review queue, nothing published
                                unapproved. The calendar largely fills itself.
  events@notice.place           a working inbound address venues can email
  /api/conditions               live weather, swell, tide, wind per beach, what is in
                                flower — built, and not yet shown on the public site
  Running cost                  close to zero: Vercel, Supabase and GitHub Actions free
                                tiers. The one paid feature (Autofill) is switched off
                                because the API credit ran out. Cost discipline is real.

═══ WHAT IT DOES NOT HAVE — THE GAPS ═══

Check each of these yourself rather than taking this list on trust:

  - NO ANALYTICS. Nothing on the public site counts a visit. Nobody knows how many people
    read it. Say plainly what that means for every recommendation you make, and name the
    cheapest privacy-respecting way to fix it.
  - No newsletter, no social account, no way for a reader to hear from Notice again.
  - No accounts. Pins live in the browser only. A reader cannot be contacted.
  - No share image on any page (no og:image).
  - No page per listing. A concept exists (concepts/listing-page.html), not built.
  - Is there a sitemap.xml? A robots.txt? Is the site in Google at all? Check
    (`site:notice.place`), and report what you find.
  - Rows on the board do not link to the town and type pages.

═══ PART ONE — AUDIENCE ═══

1. WHO. Name the distinct readers and what each wants: a local parent on a Friday night,
   a weekender in a holiday house, a day-tripper from Melbourne, a new resident, a venue
   owner checking their own listing. Which of them does the site serve well today, and
   which is it built for but not reaching?

2. THE NEIGHBOURS. Map who already has this audience on this coast. Start with these and
   find the ones missing:

     Coast & Bay (coastandbay.com.au)        Surf Coast Events (surfcoastevents.com.au)
     The Geelong Gist (newsletter)           Visit Geelong & The Bellarine
     Geelong Mums (newsletter)               Surf Coast Times, Forte magazine
     Local Facebook community groups         Council and tourism-board channels

   For each: what it is, how big it says it is (and where it says so), how it earns, and
   whether it is a competitor, a possible partner, or a channel. Several of these are
   already SOURCES for Notice — a recommendation that sours that relationship costs data.

3. COMPARABLES ELSEWHERE. Find independent local listings or what's-on publications of a
   similar scale — Australian regional first, then anywhere — where the operator has
   published real numbers: readers, subscribers, revenue, how long it took. Founder
   write-ups, interviews, public revenue pages. A dozen good ones beat fifty thin ones.
   For each, say what transfers to a region of this size and what does not.

4. CHANNELS, ranked for THIS site. At minimum weigh:

     search            is there real demand for "things to do in Torquay this weekend",
                       "Anglesea markets", "op shops Geelong"? Who ranks now? The town and
                       type pages are the obvious surface.
     a weekly email    "what's on this weekend" is the format the neighbours use. It
                       collides with "nothing to sign up for" — say how you would square it.
     Instagram / Facebook groups
     the physical world   the product is called Notice and its list is a Notice Board. A
                       printed weekly sheet or QR on real community noticeboards, in
                       cafes, holiday rentals and caravan parks is on-brand. Is there
                       evidence this works anywhere?
     venues and groups 136 shops, makers and groups plus 324 venues are listed. Each has
                       its own audience. What would make them link or share?
     schools, holiday-rental managers, visitor centres

   For each channel: evidence it works for sites like this, hours per week it costs one
   person, what it needs that Notice does not have yet, and how you would know in four
   weeks whether it was working.

═══ PART TWO — MONEY ═══

For every model below — and any you find that is not here — give: who has done it at this
scale and what they earned (sourced), the audience size it needs before it is worth
starting, the hours it costs Scott each week, and what it does to the reader's trust.

  - featured or promoted listings, paid by a venue
  - a paid tier for venues and shops: claim your row, add photos, post your own events
  - sponsorship of a weekly email or of a town or type page
  - ticketing or booking affiliate income
  - reader support: memberships, donations, "keep it free"
  - grants and local funding: council community grants, tourism-board partnerships,
    community bank branches, arts and regional-media funds. Name real, current programs
    in Victoria with their amounts and closing dates.
  - selling the tooling or the data: a what's-on feed for a council, a holiday-rental
    manager or a visitor centre; the same site stood up for another region
  - print: a seasonal guide, a weekly sheet with a sponsor
  - display advertising — include it so you can say honestly whether it is worth it

Three things to treat as hard constraints, not preferences:

  a. THE BOARD IS NOT FOR SALE BY DEFAULT. The site's whole character is that a listing
     is there because it is true and worth knowing. Any model that changes what appears,
     or in what order, must say exactly how it is labelled. Read "Nothing reaches the
     board unapproved" before proposing anything paid.

  b. THE DATA HAS LICENCES, AND EARNING MONEY MAY CHANGE THEM. This is the part most
     likely to be missed, so do it properly. Read each source's own terms and quote them:

       Open-Meteo              free tier — is commercial use allowed? what does the paid
                               tier cost?
       iNaturalist, Atlas of Living Australia, Wikipedia / Commons (CC BY-SA)
       Visit Geelong & The Bellarine / ATDW   tourism data, read through a search key
       Coast & Bay, Surf Coast Events         scraped calendars; Coast & Bay's content
                                              signals say use=reference
       Geelong Regional Libraries, Parks Victoria, VicEmergency, CFA (already recorded
       in CLAUDE.md as personal, non-commercial use only)
       OpenStreetMap / Nominatim, CARTO basemaps

     Produce a table: source, what Notice uses it for, the licence in its own words,
     whether carrying ads or sponsors or charging venues changes anything, and what it
     would cost to put right. If a model depends on a source whose terms forbid it,
     say so beside the model.

  c. ONE PERSON. Anything needing a salesperson, a moderator or a support inbox is a
     different business. Cost every idea in Scott's hours.

Also flag — as things to check with an accountant or lawyer, not as advice — the
Australian rules a paid model would touch: disclosure of sponsored content under consumer
law, the Spam Act for any email list, the Privacy Act if readers are ever identified,
and the GST registration threshold.

═══ RULES FOR THE EVIDENCE ═══

This project has been burned by confident, unsourced claims. The same rules apply here
as to its data.

  - Every number carries its source and the date you read it. A link, not "industry
    data shows".
  - Say whose number it is. An operator's own claim about its audience is a claim, not
    a measurement; write it as one.
  - Never invent a statistic, a benchmark, a price or a program. "Could not find" is a
    finding, and a useful one.
  - Read the first-party page. A blog post summarising someone's revenue is weaker than
    their own write-up of it.
  - If a site's robots.txt refuses you, do not fetch it — Coast & Bay, Humanitix and
    Instagram all refuse ClaudeBot. Search around it or note it as unread.
  - Mark every example from a big city or the US as such, and say why it does or does
    not carry to a coast of small towns with a summer peak.
  - Do not sign up for anything, fill in any form, or contact anyone on Scott's behalf.

═══ WHAT TO HAND BACK ═══

One file, prompts/log/audience-and-money.md, in plain English. Scott is a designer, not a
developer or a marketer — no jargon without saying what it means. In this order:

  1. THE ANSWER, on one screen. What to do first, second and third, and what not to do.
  2. THE SEQUENCE. What is worth doing with no measurable audience, with around 1,000
     readers a month, and with around 10,000 — for each of levels A, B and C above.
  3. Who the readers are.
  4. The neighbours, as a table.
  5. The comparables, as a table, with their numbers and sources.
  6. The channels, ranked, each with its four-week test.
  7. The money models, as a table, then a paragraph on each one worth taking seriously.
  8. The licence table.
  9. QUESTIONS ONLY SCOTT CAN ANSWER — the decisions the research cannot make for him.
 10. CHECKED AND REJECTED — every idea, source and example you looked at and dropped,
     with the reason. This list is as valuable as the recommendations; do not trim it.

Lead with your own judgement. A ranked recommendation with its reasons is the job; a
neutral survey of options is not.
```
