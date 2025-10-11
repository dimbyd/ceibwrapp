# app.py
'''Flask web server.'''

import os
from flask import Flask, render_template, request
from flask import flash, redirect
from werkzeug.utils import secure_filename

from ceibwr.peiriant import Peiriant
from ceibwr.beiro import Beiro
from ceibwr.cysonion import llythrenwau

from ceibwr.odliadur import odl_search
from ceibwr.cleciadur import clec_search

from ceibwr.cerddi import creu_cerddi_dict
from ceibwr.cerddi import creu_mefus

from ceibwr.cynghanedd import Llusg

from ceibwr.cerdd import Cerdd  
from ceibwr.pennill import Pennill
from ceibwr.llinell import Llinell
from ceibwr.rhaniad import Rhaniad
from ceibwr.corfan import Corfan
from ceibwr.gair import Gair
from ceibwr.sillaf import Sillaf, Odl
from ceibwr.nod import Nod, Cytsain, Bwlch, EOL

UPLOAD_FOLDER = '/Users/scmde/projects/ceibwrapp/ceibwrapp/static/uploads'
# UPLOAD_FOLDER = os.path.join(url_for('static'), 'uploads')

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

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
        "OFE": "lightseagreen",  # odl fewnol
        "OGY": "hotpink",      # odl gyrch
        "ODL": "crimson",         # prifodl
    },
    "cytseinedd": {
        "GEF": "magenta",   # gefell
        "CYS": "red",       # cyswllt
        "TRA": "blue",      # traws
        "TRB": "blue",      # trychben
        "CYB": "magenta",   # cysylltben
        "GWG": "darkcyan",  # gwreiddgoll
        "PEG": "green",     # pengoll
        "TOR": "r",         # toriad
    }
}

app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# filters
@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]

# -------------------------
# tests for type checking

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

        # chwilio
        clecs = clec_search(ymholiad)

        # allbwn
        context = {}
        context['clecs'] = clecs
        context['llythrenwau'] = llythrenwau['aceniad']

        return render_template('cleciadur.html', context=context)

    return render_template('cleciadur.html', context=None)


@app.route('/datryswr', methods=('GET', 'POST'))
def datryswr():
    if request.method == 'POST':
        s = request.form['mewnbwn']

        pe = Peiriant()

        uned = s
        if type(s) is str:
            meta, uned = pe.parse(s)

        # console
        print('meta:', meta)  
        print('uned:', uned)

        # datrys
        datrysiad = pe.datryswr(uned, unigol=True)
        # print('Datrysiad:', repr(datrysiad))

        # console
        if not datrysiad.dosbarth:
            beiro = Beiro()
            print(beiro.magenta('XXX'))

        # create xml docs
        xml_text = uned.xml_str()
        xml_sain = datrysiad.xml_str()

        # context
        context = {}
        context['smap'] = smap
        context['cmap'] = cmap
        context['meta'] = meta
        context['uned'] = uned
        context['datrysiad'] = datrysiad 
        context['xml_text'] = xml_text
        context['xml_sain'] = xml_sain
        context['llythrenwau'] = llythrenwau['cynghanedd'] | llythrenwau['cwpled'] | llythrenwau['mesur']

        # maps 
        # acenion: `Llafariad`: prifacen|isacen
        context['acenion'] = datrysiad.cyfuno_acenion()
        # cytseinedd: `Cytsain`: GEF|TRA|CYS|GWG|etc.
        context['odlau'] = datrysiad.cyfuno_odlau()
        # odlau: `Odl`: ODF|ODG|ODL
        context['cytseinedd'] = datrysiad.cyfuno_cytseinedd()
        
        return render_template('datryswr.html', context=context, scroll='prif')

    return render_template('datryswr.html', context=None)


@app.route('/pysgotwr', methods=('GET', 'POST'))
def pysgotwr():
    if request.method == 'POST':
        s = request.form['mewnbwn']

        pe = Peiriant()

        dalfa = pe.pysgotwr(s, min_sillafau=4, max_sillafau=8)

        # console
        # print('dalfa:', dalfa)
        
        # context
        context = {}
        context['smap'] = smap
        context['cmap'] = cmap
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

        return render_template('pysgotwr.html', context=context)

    return render_template('pysgotwr.html', context=None)


@app.route('/dysgu')
def dysgu():
    return render_template('dysgu.html')


@app.route('/cerddi', methods=('GET', 'POST'))
def cerddi():
    context = {}
    context['db'] = creu_cerddi_dict()
    return render_template('cerddi.html', context=context)


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


@app.route('/mefus')
def mefus():
    context = {}
    context['mefus'] = creu_mefus()
    return render_template('mefus.html', context=context)
