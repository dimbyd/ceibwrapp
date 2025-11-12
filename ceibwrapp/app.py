# app.py
'''Flask web server.'''

import os
import time

from flask import Flask, render_template, request, url_for
from flask import flash, redirect
from werkzeug.utils import secure_filename

from pathlib import Path

from ceibwr.peiriant import Peiriant
from ceibwr.beiro import Beiro
from ceibwr.cysonion import llythrenwau

from ceibwr.odliadur import odl_search
from ceibwr.cleciadur import clec_search

from ceibwr.mesur import Mesur
from ceibwr.cynghanedd import Llusg

from ceibwr.cerdd import Cerdd
from ceibwr.pennill import Pennill
from ceibwr.llinell import Llinell
from ceibwr.rhaniad import Rhaniad
from ceibwr.corfan import Corfan
from ceibwr.gair import Gair
from ceibwr.sillaf import Sillaf, Odl
from ceibwr.nod import Nod, Cytsain, Bwlch, EOL


# from . import sbwriel
from ceibwrapp.celfi import create_cerddi_dict
from ceibwrapp.celfi import create_mefus
from ceibwrapp.darlun import plot

from ceibwrapp.settings import (
    CERDDI_FOLDER,
    MEFUS_FOLDER,
)

app = Flask(__name__)

# symbols
smap = {
    "whitespace": {
        # 'SPC': '\u2E31',
        # 'SPC': '~',  # space
        # 'EOL': '*',  # end-of-line
        'SPC': '&nbsp;',  # space
        'EOL': '</br>',  # end-of-line
        'TOR': '|',  # caesura
    },
    "acenion": {
        'PRA': '/',  # prifacen
        'ISA': 'v',  # is-acen
        'INL': ':',  # inline
    }
}

# colours: mae'n gwneud synnwyr fod 
# 1. nodau cysylltben yr un lliw a gefyll
# 2. nodau trychben yr un lliw a nodau traws/canolgoll

cmap = {
    "odlau": {
        "OFE": "lightcoral",  # odl fewnol
        "OGY": "hotpink",     # odl gyrch
        "ODL": "goldenrod",   # prifodl
    },
    "cytseinedd": {
        "GEF": "hotpink",   # gefell
        "CYS": "red",       # cyswllt
        "TRA": "darkcyan",      # traws
        "TRB": "darkcyan",      # trychben
        "CYB": "magenta",   # cysylltben
        "GWG": "darkcyan",  # gwreiddgoll
        "PEG": "green",     # pengoll
    }
}

app.secret_key = os.urandom(24)

# UPLOAD_FOLDER = url_for('static', filename='uploads/')


def refresh_mefus():
    mefus_files = [os.path.join(path, name) for path, subdirs, files in os.walk(MEFUS_FOLDER) for name in files]
    cerddi_files = [os.path.join(path, name) for path, subdirs, files in os.walk(CERDDI_FOLDER) for name in files]

    mefus_time = max(os.path.getmtime(f) for f in mefus_files)
    cerddi_time = max(os.path.getmtime(f) for f in cerddi_files)
    
    print(mefus_time)
    print(cerddi_time)
    print(mefus_time < cerddi_time)

    if mefus_time < cerddi_time:
        print('REFRESHING MEFUS')
        create_mefus()


# init
with app.app_context():
    refresh_mefus()


# filters
@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]


# -------------------------
# tests for type checking
@app.template_test('mesur')
def is_mesur(value):
    return isinstance(value, Mesur)


@app.template_test('llusg')
def is_llusg(value):
    return isinstance(value, Llusg)


@app.template_test('cerdd')
def is_cerdd(value):
    return isinstance(value, Cerdd)


@app.template_test('pennill')
def is_pennill(value):
    return isinstance(value, Pennill)


@app.template_test('llinell')
def is_llinell(value):
    return isinstance(value, Llinell)


@app.template_test('rhaniad')
def is_rhaniad(value):
    return isinstance(value, Rhaniad)


@app.template_test('corfan')
def is_corfan(value):
    return isinstance(value, Corfan)


@app.template_test('gair')
def is_gair(value):
    return isinstance(value, Gair)


@app.template_test('sillaf')
def is_sillaf(value):
    return isinstance(value, Sillaf)


@app.template_test('odl')
def is_odl(value):
    return isinstance(value, Odl)


@app.template_test('cytsain')
def is_cytsain(value):
    return isinstance(value, Cytsain)


@app.template_test('nod')
def is_nod(value):
    return isinstance(value, Nod)


@app.template_test('bwlch')
def is_bwlch(value):
    return isinstance(value, Bwlch)


@app.template_test('eol')
def is_eol(value):
    return isinstance(value, EOL)

# -------------------------
# routes

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/odliadur', methods=('GET', 'POST'))
def odliadur():
    if request.method == 'POST':
        sillaf = request.form['sillaf']

        if not sillaf:
            return render_template('odliadur.html', context=None)

        acennog_opt = request.form.get('acennog')
        acennog = True if acennog_opt else False

        llusg_opt = request.form.get('llusg')
        llusg = True if llusg_opt else False

        # chwilio
        odlau = odl_search(sillaf, acennog=acennog, llusg=llusg)

        # allbwn
        context = {}
        context['odlau'] = ' '.join(odlau)
        context['acennog'] = acennog
        context['llusg'] = llusg

        return render_template('odliadur.html', context=context)

    return render_template('odliadur.html', context=None)


@app.route('/cleciadur', methods=('GET', 'POST'))
def cleciadur():
    if request.method == 'POST':
        ymholiad = request.form['ymholiad']

        if not ymholiad:
            return render_template('cleciadur.html', context=None)

        # chwilio
        clecs = clec_search(ymholiad)

        # allbwn
        context = {}
        context['clecs'] = clecs
        context['llythrenwau'] = llythrenwau['aceniad']

        return render_template('cleciadur.html', context=context)

    return render_template('cleciadur.html', context=None)


@app.route('/datrys', methods=('GET', 'POST'))
def datrys():
    if request.method == 'POST':
        s = request.form['mewnbwn']

        if not s:
            return render_template('datrys.html', context=None)

        pe = Peiriant()

        uned = s
        if type(s) is str:
            meta, uned = pe.parse(s)

        # console output
        print('meta:', meta)  
        print('uned:', uned)

        # datrys

        dat = pe.datryswr(uned, unigol=True)
        dat.set_nbrs()  # dyle hwn prob. fod yn "datryswr"
        print('Datrysiad:', repr(dat))

        # console
        if not dat.dosbarth:
            beiro = Beiro()
            print(beiro.magenta('XXX'))

        # create xml docs
        xml_text = uned.xml_str()
        xml_sain = dat.xml_str()

        # context
        context = {}
        context['smap'] = smap
        context['cmap'] = cmap
        context['meta'] = meta
        context['uned'] = uned
        context['datrysiad'] = dat
        context['xml_text'] = xml_text
        context['xml_sain'] = xml_sain
        context['llythrenwau'] = llythrenwau['cynghanedd'] | llythrenwau['aceniad'] | llythrenwau['cwpled'] | llythrenwau['mesur']

        # maps 
        # acenion: `Llafariad`: prifacen|isacen
        context['acenion'] = dat.cyfuno_acenion()
        # cytseinedd: `Cytsain`: GEF|TRA|CYS|GWG|etc.
        context['odlau'] = dat.cyfuno_odlau()
        # odlau: `Odl`: ODF|ODG|ODL
        context['cytseinedd'] = dat.cyfuno_cytseinedd()
        
        return render_template('datrys.html', context=context, scroll='datrysiad')

    return render_template('datrys.html', context=None)


@app.route('/pysgota', methods=('GET', 'POST'))
def pysgota():
    if request.method == 'POST':
        s = request.form['mewnbwn']
        if not s:
            return render_template('pysgota.html', context=None)
        
        pe = Peiriant()

        dalfa = pe.pysgotwr(s, min_sillafau=4, max_sillafau=8)

        # console
        # print('dalfa:', dalfa)

        # context
        context = {}
        context['smap'] = smap
        context['cmap'] = cmap
        context['llythrenwau'] = llythrenwau['cynghanedd'] | llythrenwau['aceniad']

        context['dalfa'] = dalfa

        # init maps
        context['acenion'] = {}
        context['odlau'] = {}
        context['cytseinedd'] = {}

        # maps
        for dat in dalfa:
            context['acenion'] = context['acenion'] | dat.cyfuno_acenion()
            context['odlau'] = context['odlau'] | dat.cyfuno_odlau()
            context['cytseinedd'] = context['cytseinedd'] | dat.cyfuno_cytseinedd()

        return render_template('pysgota.html', context=context)

    return render_template('pysgota.html', context=None)


@app.route('/darlunio', methods=('GET', 'POST'))
def darlunio():
    if request.method == 'POST':
        s = request.form['mewnbwn']
        if not s or type(s) is not str:
            return render_template('darlunio.html', context=None)

        dtype = request.form['drawingType']

        pe = Peiriant()
        meta, uned = pe.parse(s)

        # console output
        print('meta:', meta)
        print('uned:', uned)

        # datrys
        dat = pe.datryswr(uned)
        dat.set_nbrs()

        if dtype == 'hyperbolic':
            fname = plot(dat, hyperbolic=True, ndots=100)
        else:
            fname = plot(dat)

        # import time
        # time.sleep(1)

        context = {}
        context['dtype'] = dtype
        # context['img_file'] = fname
        context['img_file'] = url_for('static', filename='tmp/{}'.format(fname))

        return render_template('darlunio.html', context=context)

    return render_template('darlunio.html', context={'dtype': 'hyperbolic'})


@app.route('/dysgu')
def dysgu():

    return render_template('dysgu.html')


@app.route('/cronfa', methods=('GET', 'POST'))
def upload_file():

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        print('file:', file)

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pth = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print('pth:', pth)
            fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(fullpath)

            context = {'filename': filename}

            pe = Peiriant()
            s = pe.read(fullpath)
            meta, body = pe.parse(s)
            context['meta'] = meta
            context['testun'] = body
            context['amrwd'] = s

            return render_template('diolch.html', context=context)

    return render_template('cronfa.html')


@app.route('/diolch', methods=('GET', 'POST'))
def diolch():
    return render_template('diolch.html', context={})


@app.route('/cc')
def cc():
    return render_template('cc.html')


@app.route('/cerddi', methods=('GET', 'POST'))
def cerddi():
    context = {}
    context['db'] = create_cerddi_dict()
    return render_template('cerddi.html', context=context)


@app.route('/mefus')
def mefus():

    refresh_mefus()

    mefus_root = Path(MEFUS_FOLDER)
    mefus = {}

    for file in mefus_root.iterdir():

        # skip dot files
        if file.name.startswith('.'):
            continue

        mefus[file.name] = url_for('static', filename='mefus/{}'.format(file.name))

    # sort and return
    mefus = {key: value for key, value in sorted(mefus.items())}
    return render_template('mefus.html', context=mefus)
