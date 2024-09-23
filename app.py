import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.secret_key = 'nvimonarchusingdvorak'


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        uname = request.form['username']
        passwd = request.form['password']

        conn = get_db_connection()
        account = conn.execute('SELECT TYPE FROM ACCOUNTS WHERE username = ? AND password = ?',
                     (uname,passwd)).fetchone()
        conn.commit()
        conn.close()
        if account == None:
            flash('no such account exists')
        elif account['TYPE'] == 'admin':
            return redirect(url_for('admin',username=uname)) # TODO: design adnim interface
        elif account['TYPE'] == 'sponsor':
            return redirect(url_for('sponsor',username=uname)) # TODO: design adnim interface
        elif account['TYPE'] == 'influencer':
            return redirect(url_for('influencer',username=uname)) # TODO: design adnim interface

    return render_template('login.html')


@app.route('/admin/<string:username>')
def admin(username):
    conn = get_db_connection()
    campaigns = conn.execute('SELECT * FROM CAMPAIGNS').fetchall()
    flags = conn.execute('SELECT * FROM ACCOUNTS WHERE INAPPROPIATE=1').fetchall()
    conn.close()
    return render_template('admin.html',username=username ,campaigns=campaigns, flags=flags)


@app.route('/sponsor/<string:username>')
def sponsor(username):
    conn = get_db_connection()
    campaigns = conn.execute('SELECT * FROM CAMPAIGNS WHERE SPONSOR = ? ',
                             (username,)).fetchall()
    requests = conn.execute('SELECT * FROM ADREQS A, CAMPAIGNS C WHERE A.CAMPAIGN_ID = C.ID AND C.SPONSOR= ?',
                            (username,)).fetchall()
    conn.close()
    return render_template('sponsor.html',campaigns=campaigns, requests = requests, username = username)

@app.route('/influencer/<string:username>')
def influencer(username):
    conn = get_db_connection()
    campaigns = conn.execute('SELECT * FROM CAMPAIGNS').fetchall()
    requests = conn.execute('SELECT * FROM ADREQS A, CAMPAIGNS C WHERE A.CAMPAIGN_ID = C.ID AND A.INFLUENCER_ID= ? ',
                            (username,)).fetchall()
    conn.close()
    return render_template('influencer.html',campaigns=campaigns, requests= requests, username= username)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register_sponsor', methods=('GET', 'POST'))
def register_sponsor():
    if request.method=='POST':
        username = request.form['username']
        industry = request.form['industry']
        budget = request.form['budget']
        password = request.form['password']

        conn = get_db_connection()
        conn.execute('INSERT INTO SPONSORS VALUES(?, ?, ?)',
                     (username, industry, budget))
        conn.execute('INSERT INTO ACCOUNTS VALUES(?, ?, ?, ?)',
                     (username, password, 'sponsor', 0))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register_sponsor.html')


@app.route('/register_influencer', methods=('GET', 'POST'))
def register_influencer():
    if request.method=='POST':
        username = request.form['username']
        name = request.form['name']
        category = request.form['category']
        niche = request.form['niche']
        reach = request.form['reach']
        password = request.form['password']

        conn = get_db_connection()
        conn.execute('INSERT INTO INFLUENCERS VALUES(?, ?, ?, ?, ?)',
                     (username, name, category, niche, reach))
        conn.execute('INSERT INTO ACCOUNTS VALUES(?, ?, ?, ?)',
                     (username, password, 'influencer', 0))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register_influencer.html')
 

@app.route('/flag/<int:id>/<string:username>', methods=('POST',))
def flag(id,username):
    conn = get_db_connection()
    conn.execute('UPDATE CAMPAIGNS SET INAPPROPIATE = 1 '
                 'WHERE ID = ?',
                 (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', username=username))


@app.route('/campaign/<int:id>')
def campaign(id):
    conn = get_db_connection()
    campaign = conn.execute('SELECT * FROM CAMPAIGNS WHERE ID = ?',
                 (id,)).fetchone()
    conn.commit()
    conn.close()
    return render_template('campaign.html', campaign = campaign)


@app.route('/<string:actype>/<string:username>/find', methods = ('GET', 'POST'))
def find(actype,username,findstr=''):
    if request.method == 'POST':
        findstr = request.form['findstr']
    conn = get_db_connection()
    if actype == 'sponsor':
        data = conn.execute('SELECT * FROM INFLUENCERS WHERE NAME LIKE ?',
                            ('%'+findstr+'%',)).fetchall()
        conn.close()
        return render_template('sponsor_findpage.html',username = username,  influencers = data)
    elif actype == 'influencer':
        campaigns = conn.execute('SELECT * FROM CAMPAIGNS WHERE NAME LIKE ?',
                            ('%'+findstr+'%',)).fetchall()
        conn.close()
        return render_template('influencer_findpage.html', campaigns = campaigns, username = username)
    else:
        data1 = conn.execute('SELECT * FROM INFLUENCERS WHERE NAME LIKE ?',
                            ('%'+findstr+'%',)).fetchall()
        data2 = conn.execute('SELECT * FROM SPONSORS WHERE NAME LIKE ?',
                            ('%'+findstr+'%',)).fetchall()
        conn.close()
        return render_template('admin_findpage.html', influencers = data1, campaigns= data2, username= username ) 


@app.route('/sponsor/<string:username>/new_campaign', methods=('GET', 'POST'))
def new_campaign(username):
    if request.method== 'POST':
        name= request.form['name']
        description= request.form['description']
        budget= request.form['budget']
        goals= request.form['goals']

        conn = get_db_connection()
        conn.execute('INSERT INTO CAMPAIGNS(SPONSOR, NAME, DESCRIPTION, PROGRESS, BUDGET, VISIBILITY, GOALS) VALUES(?, ?, ?, ?, ?, ?, ?)',
                     (username, name, description, 'active', budget, 'public',goals ))
        conn.commit()
        conn.close()
        return redirect(url_for('sponsor', username = username))
    return render_template('new_campaign.html')


@app.route('/influencer/<string:username>/<int:id>/sendreq', methods = ('GET', 'POST'))
def sendreq_to_sponsor(username, id):
    if request.method == 'POST':
        messages = request.form['messages']
        amount = request.form['payment amount']
        conn = get_db_connection()
        conn.execute('INSERT INTO ADREQS VALUES(?, ?, ?, ?, ?)',
                     (id, username, messages, amount, 'sent by influencer'))
        conn.commit()
        conn.close()
        return redirect('/influencer/'+ username)
    return render_template('sendreq.html')



@app.route('/sponsor/<string:username>/<string:id>/sendreq', methods = ('GET', 'POST'))
def sendreq_to_influencer(username):
    if request.method == 'POST':
        id = request.form['id']
        messages = request.form['messages']
        amount = request.form['payment amount']
        conn = get_db_connection()
        conn.execute('INSERT INTO ADREQS VALUES(?, ?, ?, ?, ?)',
                     (id, username, messages, amount, 'sent by sponsor'))
        conn.commit()
        conn.close()
        return redirect('/influencer/'+ username)
    return render_template('sendreq2.html')


@app.route('/sponsor/<string:username>/<int:id>/<string:influencer>/accept', methods = ('POST',))
def accept(username, id, influencer):
    conn = get_db_connection()
    conn.execute('UPDATE ADREQS SET STATUS = ? WHERE CAMPAIGN_ID = ? AND INFLUENCER_ID = ?',
                 ('accepted', id, influencer))
    conn.commit()
    conn.close()
    return redirect(url_for('sponsor', username = username ) )


@app.route('/sponsor/<string:username>/<int:id>/<string:influencer>/reject', methods = ('POST',))
def reject(username, id, influencer):
    conn = get_db_connection()
    conn.execute('UPDATE ADREQS SET STATUS = ? WHERE CAMPAIGN_ID = ? AND INFLUENCER_ID = ?',
                 ('rejected', id, influencer))
    conn.commit()
    conn.close()
    return redirect(url_for('sponsor', username = username ) )


@app.route('/influencer/<string:influencer>/<int:id>/accept', methods = ('POST',))
def acceptinf(username, id, influencer):
    conn = get_db_connection()
    conn.execute('UPDATE ADREQS SET STATUS = ? WHERE CAMPAIGN_ID = ? AND INFLUENCER_ID = ?',
                 ('accepted', id, influencer))
    conn.commit()
    conn.close()
    return redirect(url_for('sponsor', username = username ) )


@app.route('/influencer/<string:influencer>/<int:id>/reject', methods = ('POST',))
def rejectinf(username, id, influencer):
    conn = get_db_connection()
    conn.execute('UPDATE ADREQS SET STATUS = ? WHERE CAMPAIGN_ID = ? AND INFLUENCER_ID = ?',
                 ('rejected', id, influencer))
    conn.commit()
    conn.close()
    return redirect(url_for('sponsor', username = username ) )


@app.route('/campaigns/<int:id>/delete/<string:username>', methods = ('POST',))
def delete(id,username):
    conn = get_db_connection()
    conn.execute('DELETE FROM CAMPAIGNS WHERE ID = ?',
                 ( id,))
    conn.execute('DELETE FROM ADREQS WHERE CAMPAIGN_ID = ?',
                 ( id,))
    conn.commit()
    conn.close()
    return redirect(url_for('sponsor', username = username ) )
