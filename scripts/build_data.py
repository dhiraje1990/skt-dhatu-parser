import os
import json
import requests
import msgpack
from dhatu._transliterate import slp_to_hk

# Data Sources (Using Dhaval Patel's pre-computed JSONs for speed/accuracy)
ROOTS_URL = "https://raw.githubusercontent.com/drdhaval2785/SanskritVerb/master/Data/Dhātu.json"
# For a full v1, we would iterate over all lakara files. 
# Here is the logic for the "Actual Thing" build.
LAKARA_URL_TEMPLATE = "https://raw.githubusercontent.com/drdhaval2785/SanskritVerb/master/Data/JSON/{root}/{lakara}.json"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "dhatu", "data")

def fetch_json(url):
    print(f"Fetching {url}...")
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def build():
    forms_table = {}
    lemma_index = {}
    meta_table = {}

    # 1. Get Dhatupatha Metadata
    # In a real build, we parse the massive Dhātu.json
    # For this script, let's demonstrate with a core set of 100 common roots
    # to ensure the script completes and doesn't hit GitHub rate limits.
    roots_data = fetch_json(ROOTS_URL)
    
    # We will process a subset for the "Actual" structure
    # To do ALL 2000, simply remove the slice [:100]
    for entry in roots_data[:100]:
        # Entry format in SanskritVerb is often SLP1
        slp_root = entry['dhatu']
        hk_root = slp_to_hk(slp_root)
        
        meta_table[hk_root] = {
            "gana": entry.get('gana'),
            "meaning": entry.get('meaning'),
            "pada": entry.get('pada')
        }
        
        # 2. Fetch Forms for each Lakara
        lakaras = ["lat", "lit", "lut", "lRt", "loT", "laG", "liG", "luG", "lRG"]
        root_forms = {}

        for lak in lakaras:
            # Note: In production, you'd download a bulk ZIP of these JSONs
            # rather than hitting the URL 2000x9 times.
            lak_data = fetch_json(LAKARA_URL_TEMPLATE.format(root=slp_root, lakara=lak))
            if not lak_data: continue

            root_forms[lak] = {}
            
            # Structure: lak_data typically has 'p' (parasmai) and 'a' (atmane)
            for p_key, pada_name in [('p', 'parasmai'), ('a', 'atmane')]:
                if p_key in lak_data:
                    root_forms[lak][pada_name] = {}
                    # lak_data['p'] is a list of 9 forms: [P3e, P3d, P3b, P2e, ...]
                    forms = lak_data[p_key]
                    indices = [
                        ("prathama", "eka"), ("prathama", "dvi"), ("prathama", "bahu"),
                        ("madhyama", "eka"), ("madhyama", "dvi"), ("madhyama", "bahu"),
                        ("uttama", "eka"), ("uttama", "dvi"), ("uttama", "bahu")
                    ]
                    
                    for i, (purusa, vacana) in enumerate(indices):
                        if i < len(forms):
                            hk_form = slp_to_hk(forms[i])
                            key = f"{purusa}_{vacana}"
                            root_forms[lak][pada_name][key] = hk_form
                            
                            # 3. Update Lemma Index for reverse lookup
                            if hk_form not in lemma_index:
                                lemma_index[hk_form] = []
                            
                            lemma_index[hk_form].append({
                                "form_type": "tinanta",
                                "dhatu": hk_root,
                                "upasarga": "",
                                "lakara": lak,
                                "pada": pada_name,
                                "puruSa": purusa,
                                "vacana": vacana
                            })

        forms_table[(hk_root, "")] = root_forms

    # 4. Save to Msgpack
    print("Saving binary tables...")
    with open(os.path.join(DATA_DIR, "forms.msgpack"), "wb") as f:
        # Convert tuple keys to strings because msgpack requires string/bytes keys
        stringified_forms = {f"{k[0]}|{k[1]}": v for k, v in forms_table.items()}
        f.write(msgpack.packb(stringified_forms))

    with open(os.path.join(DATA_DIR, "lemma_index.msgpack"), "wb") as f:
        f.write(msgpack.packb(lemma_index))

    with open(os.path.join(DATA_DIR, "meta.msgpack"), "wb") as f:
        f.write(msgpack.packb(meta_table))

    print("Build complete.")

if __name__ == "__main__":
    build()