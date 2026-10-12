"""Normalize per-program JSON (data/programs/*.json) into canonical vocabularies
for the summary diagrams. Writes data/programs_normalized.json.

Free-text terms produced by research agents are mapped to canonical categories
by ordered keyword rules (first match wins). Unmapped terms are reported.
"""
import json, glob, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- conditions
COND = [  # (canonical, group, regex)
    ("Long COVID", "Post-viral / fatigue", r"long covid|post-covid"),
    ("ME/CFS & PVFS", "Post-viral / fatigue", r"me/cfs|pvfs|chronic fatigue|post-viral|fatigue|brain fog|burnout|ebv"),
    ("POTS / dysautonomia", "Post-viral / fatigue", r"pots|dysautonom"),
    ("Fibromyalgia", "Chronic pain", r"fibromyalg"),
    ("CRPS", "Chronic pain", r"crps"),
    ("Tension myositis (TMS)", "Chronic pain", r"\btms\b|tension myositis"),
    ("Back / neck pain", "Chronic pain", r"back|neck|sciatica|radicul|whiplash|spine|posture|scoliosis"),
    ("Headache / migraine", "Chronic pain", r"headache|migraine"),
    ("TMD / jaw", "Chronic pain", r"tmd|tmj|jaw"),
    ("Pelvic pain / endometriosis", "Chronic pain", r"pelvic|endometri|vulvod|prostat|levator|pudendal|coccyd|sexual pain|\bic\b"),
    ("Chronic pain (general)", "Chronic pain", r"pain|arthritis|osteoarth|tendin|repetitive strain|rsi|carpal|plantar|neuropath|neuralg|knee|shoulder"),
    ("IBS / functional GI", "Functional / sensitivity", r"ibs|gastro|functional gi|\bgi\b|sibo|gerd|nausea|ibd"),
    ("MCS / EHS / sensitivities", "Functional / sensitivity", r"mcs|iei|ehs|electromag|chemical|sensitiv|misophon|hypersensitiv|visual snow"),
    ("Chronic Lyme / mould / MCAS / adrenal fatigue", "Functional / sensitivity", r"lyme|mould|mold|cirs|mcas|adrenal"),
    ("Tinnitus / dizziness", "Functional / sensitivity", r"tinnitus|dizz|vertigo|pppd|vestib"),
    ("FND / dissociation", "Functional / sensitivity", r"fnd|functional neuro|dissociat|tic|stutter|dystonia|depersonal"),
    ("Somatic symptom disorder", "Functional / sensitivity", r"somatic symptom|bodily distress|somatoform"),
    ("PTSD / trauma", "Mental health", r"ptsd|trauma"),
    ("Anxiety / OCD", "Mental health", r"anxiety|panic|ocd|agoraphob|intrusive|phobia"),
    ("Depression", "Mental health", r"depress"),
    ("Insomnia", "Mental health", r"insomnia|sleep"),
    ("Addiction", "Mental health", r"addict|substance|withdrawal|opioid"),
    ("Stress / wellbeing", "Mental health", r"stress|wellbeing|well-being|performance|memory|cognition"),
    ("Other medical (MS, PD, cancer, autoimmune, CVD…)", "Other medical", r"."),
]

# ---------------------------------------------------------------- mechanisms
MECH = [  # (canonical, family, regex)
    ("Neuroplastic / learned pain (predictive brain)", "Brain threat & learning", r"neuroplastic|learned pain|predictive|danger signal|expectan|placebo|belief|remembered wellness|epigenetic"),
    ("Limbic / amygdala threat impairment", "Brain threat & learning", r"limbic|amygdala"),
    ("Conditioning / classical learning", "Brain threat & learning", r"condition(ing|ed)? |classical learning|^conditioning|reconsolidation|working-memory"),
    ("Central sensitization", "Brain threat & learning", r"central sensiti"),
    ("Autonomic dysregulation (fight-or-flight)", "Autonomic & physiological", r"autonomic|fight-or-flight|sympathetic"),
    ("Polyvagal / vagal safety signalling", "Autonomic & physiological", r"polyvagal|vagal|heart-brain|coherence"),
    ("Stress / HPA axis", "Autonomic & physiological", r"stress|hpa|hormesis|breathing pattern|breathing retraining"),
    ("Inflammation / immune", "Autonomic & physiological", r"inflamm|immune"),
    ("Mitochondrial / metabolic / cell danger", "Autonomic & physiological", r"mitochond|metabolic|cell danger|energy-envelope|push-crash"),
    ("Fear-avoidance / catastrophizing / appraisal", "Cognitive & attentional", r"fear-avoid|catastroph|appraisal|inflexib|avoidance|self-efficacy|social isolation"),
    ("Attention / interoception / hypervigilance", "Cognitive & attentional", r"attention|interocept|hypervig|hypnotic"),
    ("Mind-wandering / reactivity (mindfulness model)", "Cognitive & attentional", r"mind-wander|reactivity|secondary suffering|self-critic|compassion|hedonic|reward"),
    ("Repressed emotion / psychodynamic", "Emotion & trauma", r"repressed|psychodynamic|emotional awareness|unexpressed|parts/self"),
    ("Unresolved trauma held in the body", "Emotion & trauma", r"trauma|dissociation|toxic/chemical"),
    ("Sensorimotor / movement patterns / body schema", "Body & neural circuits", r"sensorimotor|movement|body schema|postural|co-contraction|myofascial"),
    ("Brain network / oscillation dysregulation", "Body & neural circuits", r"brain network|oscillation"),
    ("Peripheral nerve / pain gating", "Body & neural circuits", r"peripheral|gating|descending|conditioned pain"),
    ("Energy / qi / quantum (non-scientific)", "Energetic", r"qi|meridian|quantum|energetic"),
]

# ---------------------------------------------------------------- roots
# (canonical, family, approx origin year, regex)
ROOTS = [
    ("Third-wave CBT (ACT, DBT, compassion)", "Behavioral & cognitive", 1990, r"third-wave|act\b|acceptance|relational frame|compassion|dbt"),
    ("Buddhist meditation (vipassana, Zen, Tibetan)", "Ancient contemplative & movement", -500, r"buddhis|vipassana|zen|tummo|triratna|metta|non-striving|diamond approach|advaita|kashmiri|nondual"),
    ("Mindfulness programs (MBSR/MBCT lineage)", "Ancient contemplative & movement", 1979, r"mbsr|mbct|mindfulness|contemplative neuro|relapse prevention"),
    ("Yoga / pranayama / yoga nidra", "Ancient contemplative & movement", -200, r"yoga|pranayama|vedic|transcendental|satyananda|osho"),
    ("Daoist qigong / tai chi / TCM", "Ancient contemplative & movement", -300, r"qigong|tai chi|daoist|taoist|chinese|tcm|acupunct|acupress|martial|judo"),
    ("Mesmerism / hypnosis / suggestion", "Suggestion & mind-cure", 1775, r"hypno|mesmer|erickson|coué|coue|guided imagery|spiegel|whorwell"),
    ("New Thought / Christian Science / New Age", "Suggestion & mind-cure", 1866, r"new thought|christian science|mind-cure|new age|ramtha|quantum|parapsych|visualisation|wilber|enneagram"),
    ("NLP / energy psychology (TFT, EFT)", "Suggestion & mind-cure", 1975, r"nlp|energy psych|tft|thought field|eft|tapping|applied kinesiology|psych-k|laughter"),
    ("Psychoanalysis / psychodynamic", "Psychodynamic & emotion", 1895, r"freud|psychoanaly|psychodynamic|davanloo|istdp|malan|corrective emotional|alexander & french|alexander corrective|chicago psychosom|psychosomatic|mccullough|charcot|janet|hysteria|jungian"),
    ("Body psychotherapy (Reich, Lowen)", "Psychodynamic & emotion", 1930, r"reich|bioenerget|lowen"),
    ("Attachment / parts & family systems (IFS)", "Psychodynamic & emotion", 1950, r"attachment|bowlby|family|internal family|ifs|parts|inner-child|transactional|gestalt|emotion-focused|humanistic|phenomenolog|transpersonal|group psycho"),
    ("Expressive writing (Pennebaker)", "Psychodynamic & emotion", 1986, r"pennebaker|expressive|journal"),
    ("Sarno TMS / mind-body syndrome", "Pain science", 1975, r"sarno|schubiner|mind-body syndrome|pain reprocessing|eaet"),
    ("Pavlov / behaviorism / conditioning", "Behavioral & cognitive", 1903, r"pavlov|behaviorism|conditioning|reconsolidation|wolpe|desensiti|exposure|fordyce|operant|minnesota|ledoux"),
    ("Claire Weekes nervous-illness model", "Behavioral & cognitive", 1962, r"weekes|frankl|paradoxical"),
    ("CBT (Beck/Ellis) & pain-management programmes", "Behavioral & cognitive", 1963, r"cbt|cognitive|beck|ellis|pacing|self-management|lorig|motivational|single-session|unified protocol|barlow|conceptual change"),
    ("Life coaching / positive psychology", "Behavioral & cognitive", 1998, r"coaching|positive psych|arts-in-health|social prescrib|singing|elocution"),
    ("Limbic retraining (Gupta / DNRS lineage)", "Pain science", 2007, r"limbic retrain|gupta|dnrs|lightning"),
    ("Alexander / Feldenkrais / somatics", "Body & movement", 1895, r"alexander technique|feldenkrais|somatics|hanna|sherrington|magnus|dewey|cybernetic|reflex physiology|startle|motor learning|motor imagery|mirror-box|ramachandran"),
    ("Somatic Experiencing / ethology", "Body & movement", 1970, r"somatic experiencing|ethology|sensorimotor psycho|kain|somatic practice|somatic psych|tomatis|auditory"),
    ("Physiotherapy / osteopathy / rehab medicine", "Body & movement", 1813, r"neurasthenia|rest-cure|osteopath|chiropract|physiotherap|physical therap|manual|neurodynamic|rehabilitation|physiatry|mayo|bonica|mayer-gatchel|exercise|graded|gymnast|fall-prevention|geriatric|respiratory|travell|myofascial|hydrotherapy|cold-water"),
    ("Cannon / Selye stress physiology", "Stress physiology", 1915, r"selye|cannon|stress theory|fight-or-flight"),
    ("Autogenic training / relaxation response", "Stress physiology", 1932, r"autogenic|relaxation|jacobson|progressive relax"),
    ("Biofeedback / psychophysiology", "Stress physiology", 1965, r"biofeedback|heartmath|heart-brain|coherence|neurophysiol|qeeg|dynamical systems|behavioral medicine"),
    ("Polyvagal theory", "Stress physiology", 1994, r"polyvagal|hughlings"),
    ("Psychoneuroimmunology / ACE research", "Stress physiology", 1975, r"psychoneuroimm|ace research|cholinergic|placebo|allostasis|koob"),
    ("Gate control / neuromatrix / pain neuroscience education", "Pain science", 1965, r"neuroplasticity writing|doidge|gate control|neuromatrix|pain neuroscience|moseley|butler|diffuse noxious|conditioned pain|fear-avoidance|catastroph|sullivan|biopsychosocial|engel|liaison|wessely|rome foundation|monash|dgbi|predictive|bayesian|friston|fnd physio|specialist fnd|mayo motor"),
    ("Electrotherapy / neuromodulation", "Neurotechnology", 1804, r"galvan|electro|tens|vagus|neuromodulation|ect|faraday|ltp|neuroimaging|motor cortex|occipital|electrosleep|ces|nerve stimulation"),
    ("Functional / integrative medicine", "Integrative medicine", 1990, r"functional/integrative|integrative|functional medicine|naturopath"),
]


def match(term, rules, idx_name=0):
    t = term.lower()
    for r in rules:
        if re.search(r[-1], t):
            return r
    return None


def main():
    progs = []
    unmapped = {"conditions": set(), "mechanisms": set(), "roots": set()}
    for f in sorted(glob.glob(os.path.join(ROOT, "data/programs/*.json"))):
        d = json.load(open(f))
        d = d.get("data", d)
        conds, mechs, roots = [], [], []
        for c in d["conditions_claimed"]:
            r = match(c, COND)
            if r[0].startswith("Other"):
                unmapped["conditions"].add(c)
            if r[0] not in conds:
                conds.append(r[0])
        prim = []
        for c in d.get("conditions_primary", []):
            r = match(c, COND)
            if r[0] not in prim:
                prim.append(r[0])
        for m in d["mechanisms"]:
            r = match(m, MECH)
            if not r:
                unmapped["mechanisms"].add(m)
                continue
            if r[0] not in mechs:
                mechs.append(r[0])
        for x in d["roots"]:
            r = match(x, ROOTS)
            if not r:
                unmapped["roots"].add(x)
                continue
            if r[0] not in roots:
                roots.append(r[0])
        progs.append(dict(
            slug=d["slug"], name=d["name"], url=d["url"], founders=d["founders"],
            founded_year=d["founded_year"], founded_year_range=d["founded_year_range"],
            category=d["category"], delivery=d["delivery"], business_model=d["business_model"],
            cost_summary=d["cost_summary"], cost_usd_typical=d["cost_usd_typical"],
            differentiation=d["differentiation"], mechanism_summary=d["mechanism_summary"],
            mainstream_adoption=d["mainstream_adoption"], insurance=d["insurance"],
            evidence_level=d["evidence_level"], n_trials=len(d["key_trials"]),
            conditions=conds, conditions_primary=prim, mechanisms=mechs, roots=roots,
            mechanisms_primary=(match(d["mechanisms"][0], MECH) or ["?"])[0] if d["mechanisms"] else None,
            trajectory_raw=d["popularity"]["trajectory"], reach_log10_raw=d["popularity"]["reach_log10"],
        ))
    meta = dict(
        conditions=[dict(name=c[0], group=c[1]) for c in COND],
        mechanisms=[dict(name=m[0], family=m[1]) for m in MECH],
        roots=[dict(name=r[0], family=r[1], year=r[2]) for r in ROOTS],
    )
    json.dump(dict(meta=meta, programs=progs), open(os.path.join(ROOT, "data/programs_normalized.json"), "w"), indent=1)
    for k, v in unmapped.items():
        print(f"\nUNMAPPED {k} ({len(v)}):", sorted(v), file=sys.stderr)


if __name__ == "__main__":
    main()
