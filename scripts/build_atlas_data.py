"""Join normalized program data with calibrated popularity estimates and
emit data/atlas_data.json (embedded into summary/atlas.html by build_html.py).

Popularity model (see summary/methods section):
  engaged_log10   = median of 3 independent calibrators (audited where they
                    disagreed by >= 1 log unit; audit ruling replaces median)
  yearly users(y) = 10**engaged_log10 * share(y) / sum(share)
  where share(y) is the median calibrator trajectory, linearly interpolated to
  every year from founding (or 1960) to 2026.
"""
import json, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAMILY = {
    "Neuroplastic / mind-body syndrome": [
        "sarno-method", "pain-reprocessing-therapy", "emotional-awareness-expression-therapy",
        "unlearn-your-pain", "psychophysiologic-symptom-relief-therapy", "istdp",
        "journalspeak-nicole-sachs", "pain-free-you-dan-buglio", "atns-neuroplastic-symptoms-association",
        "curable", "lin-health", "pathways-pain-relief", "back-in-control-hanscom"],
    "Brain / limbic retraining": [
        "dnrs", "gupta-program", "lightning-process", "ans-rewire", "primal-trust", "mickel-therapy",
        "cfs-health", "cfs-recovery", "re-origin", "vital-side", "optimum-health-clinic", "raelan-agle",
        "joe-dispenza"],
    "Cognitive-behavioral & pain education": [
        "cbt-for-chronic-pain", "act-for-chronic-pain", "cbt-get-for-cfs", "explain-pain-pain-neuroscience-education",
        "graded-motor-imagery", "cognitive-functional-therapy", "empowered-relief", "mindspot-pain-course",
        "fibroguide-painguide", "stress-bodily-distress-syndrome-aarhus", "interdisciplinary-pain-rehabilitation-mayo",
        "physio4fmd-fnd-physiotherapy", "neurosymptoms-org", "dare-claire-weekes-method", "wise-anderson-protocol"],
    "Mindfulness & contemplative": [
        "mbsr", "mbct", "mindfulness-oriented-recovery-enhancement", "breathworks-mindfulness-for-health",
        "meditation-apps-headspace-calm", "irest-yoga-nidra", "center-for-mind-body-medicine",
        "relaxation-response-benson-henry"],
    "Somatic, trauma & emotion": [
        "somatic-experiencing", "polyvagal-theory-informed-therapy", "tre-trauma-releasing-exercises",
        "internal-family-systems", "emdr", "compassionate-inquiry-gabor-mate", "eft-tapping",
        "smartbody-smartmind-irene-lyon", "hanna-somatics"],
    "Movement & breath": [
        "feldenkrais-method", "alexander-technique", "yoga-therapy", "tai-chi-qigong", "wim-hof-method", "eno-breathe"],
    "Hypnosis": ["gut-directed-hypnotherapy", "nerva", "reveri"],
    "Devices & neuromodulation": [
        "neurofeedback", "heartmath", "non-invasive-vagus-nerve-stimulation", "transcranial-electrical-stimulation-tdcs-ces",
        "transcranial-magnetic-stimulation", "wearable-neuromodulation-pain-migraine", "safe-and-sound-protocol"],
}
FAM_OF = {s: f for f, ss in FAMILY.items() for s in ss}

SHORT = {  # compact display labels
    "sarno-method": "Sarno / TMS", "pain-reprocessing-therapy": "Pain Reprocessing Therapy",
    "emotional-awareness-expression-therapy": "EAET", "unlearn-your-pain": "Unlearn Your Pain",
    "psychophysiologic-symptom-relief-therapy": "PSRT / PSPR", "istdp": "ISTDP",
    "journalspeak-nicole-sachs": "JournalSpeak", "pain-free-you-dan-buglio": "Pain Free You",
    "atns-neuroplastic-symptoms-association": "ATNS / PPDA", "curable": "Curable", "lin-health": "Lin Health",
    "pathways-pain-relief": "Pathways", "back-in-control-hanscom": "Back in Control (Hanscom)",
    "dnrs": "DNRS", "gupta-program": "Gupta Program", "lightning-process": "Lightning Process",
    "ans-rewire": "ANS Rewire", "primal-trust": "Primal Trust", "mickel-therapy": "Mickel Therapy",
    "cfs-health": "CFS Health", "cfs-recovery": "CFS Recovery", "re-origin": "ReOrigin", "vital-side": "Vital Side",
    "optimum-health-clinic": "Optimum Health Clinic", "raelan-agle": "Raelan Agle", "joe-dispenza": "Joe Dispenza",
    "cbt-for-chronic-pain": "CBT for chronic pain", "act-for-chronic-pain": "ACT for chronic pain",
    "cbt-get-for-cfs": "CBT/GET for CFS", "explain-pain-pain-neuroscience-education": "Explain Pain / PNE",
    "graded-motor-imagery": "Graded Motor Imagery", "cognitive-functional-therapy": "Cognitive Functional Therapy",
    "empowered-relief": "Empowered Relief", "mindspot-pain-course": "MindSpot Pain Course",
    "fibroguide-painguide": "FibroGuide / PainGuide", "stress-bodily-distress-syndrome-aarhus": "STreSS (Aarhus)",
    "interdisciplinary-pain-rehabilitation-mayo": "Interdisciplinary pain rehab", "physio4fmd-fnd-physiotherapy": "Physio4FMD",
    "neurosymptoms-org": "neurosymptoms.org", "dare-claire-weekes-method": "DARE / Claire Weekes",
    "wise-anderson-protocol": "Wise-Anderson Protocol", "mbsr": "MBSR", "mbct": "MBCT",
    "mindfulness-oriented-recovery-enhancement": "MORE", "breathworks-mindfulness-for-health": "Breathworks",
    "meditation-apps-headspace-calm": "Headspace / Calm", "irest-yoga-nidra": "iRest Yoga Nidra",
    "center-for-mind-body-medicine": "Center for Mind-Body Medicine", "relaxation-response-benson-henry": "Relaxation Response",
    "somatic-experiencing": "Somatic Experiencing", "polyvagal-theory-informed-therapy": "Polyvagal-informed therapy",
    "tre-trauma-releasing-exercises": "TRE", "internal-family-systems": "IFS", "emdr": "EMDR",
    "compassionate-inquiry-gabor-mate": "Compassionate Inquiry (Maté)", "eft-tapping": "EFT Tapping",
    "smartbody-smartmind-irene-lyon": "SmartBody SmartMind", "hanna-somatics": "Hanna Somatics",
    "feldenkrais-method": "Feldenkrais", "alexander-technique": "Alexander Technique", "yoga-therapy": "Yoga therapy",
    "tai-chi-qigong": "Tai chi / qigong", "wim-hof-method": "Wim Hof Method", "eno-breathe": "ENO Breathe",
    "gut-directed-hypnotherapy": "Gut-directed hypnotherapy", "nerva": "Nerva", "reveri": "Reveri",
    "neurofeedback": "Neurofeedback", "heartmath": "HeartMath", "non-invasive-vagus-nerve-stimulation": "Non-invasive VNS",
    "transcranial-electrical-stimulation-tdcs-ces": "tDCS / CES", "transcranial-magnetic-stimulation": "rTMS",
    "wearable-neuromodulation-pain-migraine": "Wearable neuromodulation", "safe-and-sound-protocol": "Safe and Sound Protocol",
}


def interp(points, y0, y1):
    pts = sorted((int(p["year"]), float(p.get("share", p.get("relative_activity", 0)))) for p in points)
    pts = [p for p in pts if p[0] <= y1]
    out = {}
    for y in range(y0, y1 + 1):
        if not pts or y < pts[0][0]:
            out[y] = 0.0
            continue
        if y >= pts[-1][0]:
            out[y] = pts[-1][1]
            continue
        for (a, va), (b, vb) in zip(pts, pts[1:]):
            if a <= y <= b:
                out[y] = va + (vb - va) * (y - a) / (b - a) if b > a else vb
                break
    return out


def main():
    norm = json.load(open(os.path.join(ROOT, "data/programs_normalized.json")))
    cal = json.load(open(os.path.join(ROOT, "data/popularity_calibration.json")))
    rulings = {r["slug"]: r for r in cal.get("audits", [])}
    per = {}
    for c in cal["calibrations"]:
        for p in c["programs"]:
            per.setdefault(p["slug"], []).append(p)
    missing = [p["slug"] for p in norm["programs"] if p["slug"] not in FAM_OF]
    assert not missing, missing
    Y0, Y1 = 1960, 2026
    for p in norm["programs"]:
        s = p["slug"]
        p["family"] = FAM_OF[s]
        p["short"] = SHORT[s]
        ests = per.get(s, [])
        if ests:
            eng = statistics.median(e["engaged_log10"] for e in ests)
            aud = statistics.median(e["audience_log10"] for e in ests)
            conf = sorted(e["confidence"] for e in ests)[len(ests) // 2]
            basis = " | ".join(e["basis"] for e in ests)
        else:
            eng, aud, conf, basis = p["reach_log10_raw"], p["reach_log10_raw"], "low", "researcher estimate only"
        if s in rulings:
            eng, aud = rulings[s]["engaged_log10"], rulings[s]["audience_log10"]
            basis = "AUDIT: " + rulings[s]["reasoning"] + " || " + basis
        p.update(engaged_log10=round(eng, 2), audience_log10=round(max(aud, eng), 2), pop_confidence=conf, pop_basis=basis,
                 engaged_spread=round(max(e["engaged_log10"] for e in ests) - min(e["engaged_log10"] for e in ests), 2) if ests else None)
        start = max(Y0, p["founded_year"] or Y0)
        # median of calibrator trajectories (each normalized to sum 1) after interpolation
        curves = []
        for e in ests:
            c = interp(e["trajectory"], start, Y1)
            tot = sum(c.values()) or 1
            curves.append({y: v / tot for y, v in c.items()})
        if not curves:
            c = interp(p["trajectory_raw"], start, Y1)
            tot = sum(c.values()) or 1
            curves = [{y: v / tot for y, v in c.items()}]
        med = {y: statistics.median(cv[y] for cv in curves) for y in range(start, Y1 + 1)}
        tot = sum(med.values()) or 1
        # pre-1960 users: calibrators entered them as lump totals at year < 1960
        # (relative to the yearly scale). Plot only the post-1960 fraction.
        fracs = []
        for e in ests:
            c = interp(e["trajectory"], start, Y1)
            pre = sum(float(t["share"]) for t in e["trajectory"] if int(t["year"]) < Y0)
            post = sum(c.values())
            fracs.append(post / (post + pre) if post + pre else 1.0)
        frac_post = statistics.median(fracs) if fracs else 1.0
        N = 10 ** eng * frac_post
        p["yearly"] = {y: round(N * v / tot) for y, v in med.items()}
        del p["trajectory_raw"]
    norm["calibration_notes"] = [c.get("method_notes", "") for c in cal["calibrations"]]
    norm["families"] = list(FAMILY.keys())
    json.dump(norm, open(os.path.join(ROOT, "data/atlas_data.json"), "w"), indent=1)
    print("ok", len(norm["programs"]))


if __name__ == "__main__":
    main()
