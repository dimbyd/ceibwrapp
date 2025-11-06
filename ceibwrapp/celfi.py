# celfi.py
'''
Creu `dict o wrthrychau `Cerdd` o'r ffeiliau yn /data/cerddi/.

Mae hyn ar gyfer `ceibwrapp` - dyle fe fod fana, neu o leia
dyle hwn allbynnu ffeil .json (h.y. fformat safonol).
'''

import os
import yaml
from pathlib import Path
from slugify import slugify

from .settings import CERDDI_FOLDER, MEFUS_FOLDER
from ceibwr.peiriant import Peiriant


def create_cerddi_dict():
    '''
    Creu `dict` awdur: [cerdd01, cerdd02, ...]
    lle mae
    cerdd = {teitl, awdur, ..., slug, cynnwys}
    '''

    db = {}

    rp = Path(CERDDI_FOLDER)
    for subdir in rp.iterdir():

        # ignore dot folders
        if subdir.name.startswith('.'):
            continue

        print('SUBDIR:', subdir.name)

        db[subdir.name] = {
            'slug': slugify(subdir.name),
            'cerddi': [],
         }

        for file in subdir.iterdir():
            print('FILE:', file)

            # ignore dot files
            if file.name.startswith('.'):
                continue

            with open(file) as f:

                s = f.read().strip()

                # parse header
                parts = s.split('---')
                if not parts[0]:
                    parts = parts[1:]
                head = parts[0].strip()
                body = parts[1].strip()

                cerdd = yaml.safe_load(head)  # dict
                print(cerdd)

                # enforce `teitl`
                if 'teitl' not in cerdd:
                    continue

                cerdd['slug'] = slugify(subdir.name + ' ' + cerdd['teitl'])
                cerdd['testun'] = body
                cerdd['amrwd'] = s  # hac

                db[subdir.name]['cerddi'].append(cerdd)

        # sort
        db[subdir.name]['cerddi'] = sorted(db[subdir.name]['cerddi'], key=lambda d: d['teitl'])

    # sort
    db = {key: value for key, value in sorted(db.items())}

    # print('DB:', db.keys())
    # kk = list(db.keys())[0]
    # print('EX:', db[kk])
    return db


# mefus
def create_mefus():
    '''
    Rhestr datrysiadau xml.
    Pearls before swine.
    '''

    pe = Peiriant()
    mefus = {}

    cerddi_root = Path(CERDDI_FOLDER)
    for subdir in cerddi_root.iterdir():

        # skip dot folders
        if subdir.name.startswith('.'):
            continue

        print(subdir)  # awdur

        for file in subdir.iterdir():

            # skip dot files
            if file.name.startswith('.'):
                continue

            print(file.name)

            with open(file) as f:
                s = f.read().strip()

            # parse
            meta, uned = pe.parse(s)

            # enforce teitl
            if 'teitl' not in meta:
                continue

            # datrys
            dat = pe.datryswr(uned)                
            dat.meta = meta

            # record (dict)
            slug = slugify(subdir.name + ' ' + meta['teitl'])
            mefus[slug] = dat.xml_str(include_header=False)

            # write
            fname = os.path.join(MEFUS_FOLDER, slug + '.xml')
            print('FNAME:', fname)
            with open(fname, 'w+') as f:
                f.write(dat.xml_str())


def main():
    import pprint

    # cd = creu_cerddi_dict()
    # pprint.pprint(cd)
    # print()

    mefus = create_mefus()
    pprint.pprint(mefus)
    print()


if __name__ == "__main__":
    main()
