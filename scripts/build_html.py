"""Embed data/atlas_data.json and the methods text into scripts/atlas_template.html
-> summary/mind_body_atlas.html"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "data/atlas_data.json")))
log = json.load(open(os.path.join(ROOT, "data/curation_and_factcheck_log.json")))
n_corr = sum(len(p["corrections"]) for p in log["programs"])
n_excl = len(log["excluded"])
n_prog = len(data["programs"])

METHODS = f"""
<h2>Methods</h2>
<h3>1. Finding programs</h3>
<p>Seven discovery agents searched the web in parallel, each from a different angle:</p>
<ul>
<li>neuroplastic-pain and mind-body-syndrome therapies</li>
<li>limbic and brain-retraining courses</li>
<li>digital apps</li>
<li>somatic and movement practices</li>
<li>devices and neuromodulation</li>
<li>influencers, authors and long-standing contemplative programs</li>
<li>a bottom-up sweep of patient communities: Reddit (r/cfs, r/covidlonghaulers, r/ChronicPain, r/TMSHealing and others), Phoenix Rising, Health Rising and Science for ME</li>
</ul>
<p>Together they returned 219 raw candidates. A curation agent merged duplicates and kept 64, chosen for prominence (concrete signals such as user counts, book sales, community size, trials and clinic adoption), a specific identifiable program, and relevance to the target conditions. It excluded {n_excl} entries, listed in <code>data/curation_and_factcheck_log.json</code>.</p>
<p>A completeness critic then checked the list against the exclusions and fresh searches. It added 10 programs that a scholarly survey would be expected to cover, such as CBT/GET for CFS, STreSS (Aarhus), IFS, Physio4FMD and the Wise-Anderson Protocol. That brings the total to {n_prog}.</p>
<p>About the "Sanjay Gupta" lead: his 2025 book <em>It Doesn't Have to Hurt</em> was identified but excluded, because it is a book rather than a program. The "Gupta Program" for ME/CFS, long COVID and MCS is by Ashok Gupta.</p>
<h3>2. Researching and fact-checking each program</h3>
<p>One research agent per program read the official site (home, science, pricing, FAQ), founder biographies, PubMed and ClinicalTrials.gov, guideline and insurer sources, news, forums and the Wayback Machine. It wrote <code>programs/&lt;slug&gt;.md</code> and returned structured data.</p>
<p>A separate skeptical fact-checker then re-verified the claims most likely to be wrong: founders, founding year, prices, insurance, adoption, every listed trial (existence, authors, N, result, and whether it tested this program or only a generic technique) and popularity figures. It edited each file in place and wrote <code>data/programs/&lt;slug&gt;.json</code>. The fact-checkers logged {n_corr} corrections in total, recorded at the foot of each .md file.</p>
<h3>3. Normalizing categories</h3>
<p>Agents coded conditions, mechanisms and roots against controlled vocabularies, adding free-text terms where needed. <code>scripts/normalize.py</code> maps all terms to canonical categories with ordered keyword rules. That gives 23 condition groups in 5 clusters, 18 mechanisms in 6 families, and 29 root traditions in 9 families, each tradition with an approximate origin date. Every term was mapped.</p>
<p>The eight program families are a manual grouping by the author of this summary, made for display only. The primary mechanism is the first one the research agent listed.</p>
<h3>4. Popularity and reach estimates</h3>
<p>Each research agent collected dated popularity indicators: company-reported users, enrolment, practitioner counts, book sales, YouTube and podcast metrics, subreddit and forum sizes, trial sizes and Google Trends descriptions. Their summary reach figures used inconsistent definitions, so three calibration agents re-estimated every program on two common scales:</p>
<ul>
<li><b>engaged</b>: cumulative people who actually enrolled, were treated, or used the program</li>
<li><b>audience</b>: cumulative people exposed to it</li>
</ul>
<p>Each calibrator used a different anchoring lens: hard reported numbers, social signals converted with stated ratios, or institutional throughput. (Their estimates agreed within one log unit for every program. That agreement largely reflects the shared researcher indicators they all read, not independent measurement.) Where the three disagreed by one log unit or more on engaged reach, an audit agent researched the program and ruled; otherwise the median was used. Each calibrator also gave a yearly trajectory of new engaged users.</p>
<p>The streamgraph shows, for each program and year:</p>
<p><code>people(y) = 10^engaged_log10 × share(y) / Σ share</code></p>
<p>Here <code>share</code> is the median of the three calibrators' normalized trajectories, linearly interpolated. For programs older than 1960, calibrators entered a lump pre-1960 total, and only the post-1960 fraction is plotted.</p>
<p><b>Caveats.</b> These are order-of-magnitude estimates, typically ±0.5 log10 (about ×3) for mid-sized commercial programs. Few companies publish user numbers, and social-media signals measure attention, not treatment. For umbrella practices such as yoga therapy, tai chi, EMDR, CBT for pain and neurofeedback, only health-related use for chronic conditions is counted, and those boundaries are fuzzy. The confidence and full basis for every estimate appear in each program's profile under "How reach was estimated".</p>
<h3>5. Limits</h3>
<ul>
<li>The list favors English-language and online-visible programs.</li>
<li>Prices and insurance status were checked in October 2026 and change often.</li>
<li>"Evidence level" describes how much trial evidence exists, not whether it shows benefit. Several programs with multiple RCTs have mixed or null primary outcomes; see each .md file.</li>
<li>For several commercial programs, the trials were run by the program's founders or by people with financial ties to it.</li>
</ul>
<h3>Files</h3>
<ul>
<li><code>programs/*.md</code>: one review per program</li>
<li><code>data/programs/*.json</code>: verified structured data</li>
<li><code>data/popularity_calibration.json</code>: calibrator and audit outputs</li>
<li><code>data/atlas_data.json</code>: data behind this page</li>
<li><code>scripts/</code>: normalization and build scripts</li>
</ul>
"""

tpl = open(os.path.join(ROOT, "scripts/atlas_template.html")).read()
out = tpl.replace("/*DATA*/", json.dumps(data, separators=(",", ":"))).replace("/*METHODS*/''", json.dumps(METHODS))
os.makedirs(os.path.join(ROOT, "summary"), exist_ok=True)
open(os.path.join(ROOT, "summary/mind_body_atlas.html"), "w").write(out)
print("wrote summary/mind_body_atlas.html", len(out) // 1024, "KB")
