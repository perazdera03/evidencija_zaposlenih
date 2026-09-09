# uvoz potrebnih biblioteka
from flask import Flask, render_template, url_for, request, redirect, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import ast
import io
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# deklaracija Flask aplikacije
app = Flask(__name__)
app.secret_key = "tajni_kljuc_aplikacije"

import os

UPLOAD_FOLDER = "static/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# konekcija sa bazom
konekcija = mysql.connector.connect(
    passwd="root",
    user="root",
    database="evidencija_zaposlenih",
    port=3306
)
kursor = konekcija.cursor(dictionary=True)


def ulogovan():
    if "ulogovani_korisnik" in session:
        return True
    else:
        return False


def rola():
    if ulogovan():
        return ast.literal_eval(session["ulogovani_korisnik"]).get("rola")


def moj_zaposleni_id():
    if ulogovan():
        return ast.literal_eval(session["ulogovani_korisnik"]).get("zaposleni_id")


@app.context_processor
def inject_rola():
    return dict(trenutna_rola=rola())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        forma = request.form
        upit = "SELECT * FROM korisnici WHERE email=%s"
        vrednost = (forma["email"],)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        if korisnik and check_password_hash(korisnik["lozinka"], forma["lozinka"]):
            session["ulogovani_korisnik"] = str(korisnik)
            if korisnik["rola"] == "zaposleni":
                return redirect(url_for("moj_profil"))
            return redirect(url_for("zaposleni"))
        else:
            return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("ulogovani_korisnik", None)
    return redirect(url_for("login"))

@app.route("/registracija", methods=["GET", "POST"])
def registracija():
    if request.method == "GET":
        return render_template("registracija.html")
    elif request.method == "POST":
        forma = request.form

        upit = """INSERT INTO zaposleni
            (ime, prezime, maticni_broj, jmbg, broj_telefona, email)
            VALUES (%s, %s, %s, %s, %s, %s)"""
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["maticni_broj"],
            forma["jmbg"],
            forma["broj_telefona"],
            forma["email"],
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        novi_zaposleni_id = kursor.lastrowid

        hesovana_lozinka = generate_password_hash(forma["lozinka"])
        upit = """INSERT INTO korisnici (ime, prezime, email, lozinka, rola, zaposleni_id)
            VALUES (%s, %s, %s, %s, %s, %s)"""
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["email"],
            hesovana_lozinka,
            "zaposleni",
            novi_zaposleni_id,
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        return redirect(url_for("login"))


@app.route("/zaposleni")
def zaposleni():
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() == "zaposleni":
        return redirect(url_for("moj_profil"))
    upit = """SELECT * FROM zaposleni
        WHERE id NOT IN (
            SELECT zaposleni_id FROM korisnici
            WHERE zaposleni_id IS NOT NULL AND rola IN ('administrator', 'menadzer')
        )"""
    kursor.execute(upit)
    lista_zaposlenih = kursor.fetchall()
    return render_template("zaposleni.html", zaposleni=lista_zaposlenih)


@app.route("/zaposleni_novi", methods=["GET", "POST"])
def zaposleni_novi():
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    if request.method == "GET":
        return render_template("zaposleni_novi.html")
    elif request.method == "POST":
        forma = request.form

        naziv_slike = None
        if "slika" in request.files:
            file = request.files["slika"]
            if file.filename:
                naziv_slike = forma["jmbg"] + "_" + file.filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))

        upit = """INSERT INTO zaposleni
            (ime, prezime, maticni_broj, jmbg, datum_rodjenja, broj_telefona, email, godina_zaposlenja, bracni_status, slika)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["maticni_broj"],
            forma["jmbg"],
            forma["datum_rodjenja"],
            forma["broj_telefona"],
            forma["email"],
            forma["godina_zaposlenja"],
            forma["bracni_status"],
            naziv_slike,
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for("zaposleni"))


@app.route("/zaposleni_izmena/<id>", methods=["GET", "POST"])
def zaposleni_izmena(id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    if request.method == "GET":
        upit = "SELECT * FROM zaposleni WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        zaposleni_ = kursor.fetchone()
        return render_template("zaposleni_izmena.html", zaposleni=zaposleni_)
    elif request.method == "POST":
        forma = request.form

        upit = "SELECT slika FROM zaposleni WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        postojeci = kursor.fetchone()
        naziv_slike = postojeci["slika"]

        if forma.get("obrisi_sliku") and naziv_slike:
            stara_putanja = os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike)
            if os.path.exists(stara_putanja):
                os.remove(stara_putanja)
            naziv_slike = None

        if "slika" in request.files:
            file = request.files["slika"]
            if file.filename:
                if naziv_slike:
                    stara_putanja = os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike)
                    if os.path.exists(stara_putanja):
                        os.remove(stara_putanja)
                naziv_slike = forma["jmbg"] + "_" + file.filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))

        upit = """UPDATE zaposleni SET
            ime=%s, prezime=%s, maticni_broj=%s, jmbg=%s,
            datum_rodjenja=%s, broj_telefona=%s, email=%s, godina_zaposlenja=%s, bracni_status=%s, slika=%s
            WHERE id=%s"""
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["maticni_broj"],
            forma["jmbg"],
            forma["datum_rodjenja"],
            forma["broj_telefona"],
            forma["email"],
            forma["godina_zaposlenja"],
            forma["bracni_status"],
            naziv_slike,
            id,
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        upit = "SELECT id FROM korisnici WHERE zaposleni_id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        povezani_korisnik = kursor.fetchone()
        if povezani_korisnik:
            upit = "UPDATE korisnici SET ime=%s, prezime=%s, email=%s WHERE id=%s"
            vrednosti = (forma["ime"], forma["prezime"], forma["email"], povezani_korisnik["id"])
            kursor.execute(upit, vrednosti)
            konekcija.commit()

        return redirect(url_for("zaposleni"))


@app.route("/zaposleni_brisanje/<id>", methods=["POST"])
def zaposleni_brisanje(id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    upit = "DELETE FROM zaposleni WHERE id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    konekcija.commit()
    return redirect(url_for("zaposleni"))


@app.route("/zaposleni/<id>")
def zaposleni_detalji(id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() == "zaposleni":
        return redirect(url_for("moj_profil"))

    upit = """SELECT id FROM korisnici
        WHERE zaposleni_id=%s AND rola IN ('administrator', 'menadzer')"""
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    zasticen = kursor.fetchone()
    if zasticen:
        return redirect(url_for("zaposleni"))

    upit = "SELECT * FROM zaposleni WHERE id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    zaposleni_ = kursor.fetchone()

    upit = """SELECT ocene_ucinka.*, projekti.naziv AS projekat_naziv
        FROM ocene_ucinka
        JOIN projekti ON ocene_ucinka.projekat_id = projekti.id
        WHERE zaposleni_id=%s"""
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    ocene = kursor.fetchall()

    upit = "SELECT * FROM projekti"
    kursor.execute(upit)
    projekti_lista = kursor.fetchall()

    return render_template(
        "zaposleni_detalji.html",
        zaposleni=zaposleni_,
        ocene=ocene,
        projekti=projekti_lista,
    )


@app.route("/moj_profil")
def moj_profil():
    if not ulogovan():
        return redirect(url_for("login"))

    id = moj_zaposleni_id()

    upit = "SELECT * FROM zaposleni WHERE id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    zaposleni_ = kursor.fetchone()

    args = request.args.to_dict()
    pretraga = "%" + args.get("projekat", "") + "%"

    order_by = args.get("order_by", "datum")
    order_type = "asc"
    if "order_by" in args and "prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]:
        if args.get("order_type") == "asc":
            order_type = "desc"

    dozvoljene_kolone = {"projekat_naziv": "projekti.naziv", "ocena": "ocene_ucinka.ocena", "datum": "ocene_ucinka.datum"}
    kolona_za_sort = dozvoljene_kolone.get(order_by, "ocene_ucinka.datum")

    upit = f"""SELECT ocene_ucinka.*, projekti.naziv AS projekat_naziv
        FROM ocene_ucinka
        JOIN projekti ON ocene_ucinka.projekat_id = projekti.id
        WHERE zaposleni_id=%s AND projekti.naziv LIKE %s
        ORDER BY {kolona_za_sort} {order_type}"""
    vrednost = (id, pretraga)
    kursor.execute(upit, vrednost)
    ocene = kursor.fetchall()

    return render_template(
        "moj_profil.html",
        zaposleni=zaposleni_,
        ocene=ocene,
        args=args,
        order_type=order_type,
    )


@app.route("/moj_profil_izmena", methods=["GET", "POST"])
def moj_profil_izmena():
    if not ulogovan():
        return redirect(url_for("login"))

    id = moj_zaposleni_id()

    if request.method == "GET":
        upit = "SELECT * FROM zaposleni WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        zaposleni_ = kursor.fetchone()
        return render_template("moj_profil_izmena.html", zaposleni=zaposleni_)
    elif request.method == "POST":
        forma = request.form

        upit = "SELECT slika FROM zaposleni WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        postojeci = kursor.fetchone()
        naziv_slike = postojeci["slika"]

        if forma.get("obrisi_sliku") and naziv_slike:
            stara_putanja = os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike)
            if os.path.exists(stara_putanja):
                os.remove(stara_putanja)
            naziv_slike = None

        if "slika" in request.files:
            file = request.files["slika"]
            if file.filename:
                if naziv_slike:
                    stara_putanja = os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike)
                    if os.path.exists(stara_putanja):
                        os.remove(stara_putanja)
                naziv_slike = str(id) + "_" + file.filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))

        upit = """UPDATE zaposleni SET
            broj_telefona=%s, email=%s, bracni_status=%s, slika=%s
            WHERE id=%s"""
        vrednosti = (
            forma["broj_telefona"],
            forma["email"],
            forma["bracni_status"],
            naziv_slike,
            id,
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        korisnik_podaci = ast.literal_eval(session["ulogovani_korisnik"])
        upit = "UPDATE korisnici SET email=%s WHERE id=%s"
        vrednosti = (forma["email"], korisnik_podaci["id"])
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        upit = "SELECT * FROM korisnici WHERE id=%s"
        vrednost = (korisnik_podaci["id"],)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        session["ulogovani_korisnik"] = str(korisnik)

        return redirect(url_for("moj_profil"))


@app.route("/promena_lozinke", methods=["GET", "POST"])
def promena_lozinke():
    if not ulogovan():
        return redirect(url_for("login"))

    korisnik_podaci = ast.literal_eval(session["ulogovani_korisnik"])
    id = korisnik_podaci["id"]

    if request.method == "GET":
        upit = "SELECT * FROM korisnici WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        return render_template("promena_lozinke.html", korisnik=korisnik)
    elif request.method == "POST":
        forma = request.form

        upit = "SELECT * FROM korisnici WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()

        if not check_password_hash(korisnik["lozinka"], forma["stara_lozinka"]):
            return render_template("promena_lozinke.html", korisnik=korisnik, greska="Pogrešna trenutna lozinka.")

        hesovana_lozinka = generate_password_hash(forma["nova_lozinka"])
        upit = "UPDATE korisnici SET lozinka=%s WHERE id=%s"
        vrednosti = (hesovana_lozinka, id)
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        upit = "SELECT * FROM korisnici WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        session["ulogovani_korisnik"] = str(korisnik)

        return render_template("promena_lozinke.html", korisnik=korisnik, poruka="Lozinka je uspešno promenjena.")


@app.route("/export_mojih_ocena")
def export_mojih_ocena():
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "zaposleni":
        return redirect(url_for("zaposleni"))

    id = moj_zaposleni_id()

    upit = """SELECT projekti.naziv AS projekat, ocene_ucinka.ocena, ocene_ucinka.datum
        FROM ocene_ucinka
        JOIN projekti ON ocene_ucinka.projekat_id = projekti.id
        WHERE zaposleni_id=%s"""
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    ocene = kursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Projekat", "Ocena", "Datum"])
    for red in ocene:
        writer.writerow([red["projekat"], red["ocena"], red["datum"]])
    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=moje_ocene.csv"},
    )


@app.route("/export_mojih_ocena_pdf")
def export_mojih_ocena_pdf():
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "zaposleni":
        return redirect(url_for("zaposleni"))

    id = moj_zaposleni_id()

    upit = "SELECT * FROM zaposleni WHERE id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    zaposleni_ = kursor.fetchone()

    upit = """SELECT projekti.naziv AS projekat, ocene_ucinka.ocena, ocene_ucinka.datum
        FROM ocene_ucinka
        JOIN projekti ON ocene_ucinka.projekat_id = projekti.id
        WHERE zaposleni_id=%s"""
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    ocene = kursor.fetchall()

    output = io.BytesIO()
    p = canvas.Canvas(output, pagesize=A4)
    sirina, visina = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, visina - 50, "Izveštaj o ocenama")

    p.setFont("Helvetica", 12)
    p.drawString(50, visina - 80, f"Zaposleni: {zaposleni_['ime']} {zaposleni_['prezime']}")
    p.drawString(50, visina - 100, f"Matični broj: {zaposleni_['maticni_broj']}")
    p.drawString(50, visina - 120, f"Prosečna ocena: {zaposleni_['prosecna_ocena']}")

    y = visina - 160
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Projekat")
    p.drawString(250, y, "Ocena")
    p.drawString(350, y, "Datum")
    y -= 20

    p.setFont("Helvetica", 11)
    for red in ocene:
        p.drawString(50, y, str(red["projekat"]))
        p.drawString(250, y, str(red["ocena"]))
        p.drawString(350, y, str(red["datum"]))
        y -= 20
        if y < 50:
            p.showPage()
            y = visina - 50

    p.save()
    output.seek(0)

    return Response(
        output,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=moje_ocene.pdf"},
    )


@app.route("/ocena_nova/<id>", methods=["POST"])
def ocena_nova(id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "menadzer":
        return redirect(url_for("zaposleni"))
    forma = request.form
    upit = """INSERT INTO ocene_ucinka (zaposleni_id, projekat_id, ocena, datum)
        VALUES (%s, %s, %s, %s)"""
    vrednosti = (id, forma["projekat_id"], forma["ocena"], forma["datum"])
    kursor.execute(upit, vrednosti)
    konekcija.commit()

    upit = "SELECT AVG(ocena) AS rezultat FROM ocene_ucinka WHERE zaposleni_id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    prosek = kursor.fetchone()

    upit = """SELECT SUM(p.bodovi_vrednosti) AS rezultat
        FROM ocene_ucinka o
        JOIN projekti p ON o.projekat_id = p.id
        WHERE o.zaposleni_id=%s"""
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    bodovi = kursor.fetchone()

    upit = "UPDATE zaposleni SET ukupno_bodova=%s, prosecna_ocena=%s WHERE id=%s"
    vrednosti = (bodovi["rezultat"], prosek["rezultat"], id)
    kursor.execute(upit, vrednosti)
    konekcija.commit()

    return redirect(url_for("zaposleni_detalji", id=id))


@app.route("/ocena_brisanje/<id>/<zaposleni_id>", methods=["POST"])
def ocena_brisanje(id, zaposleni_id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "menadzer":
        return redirect(url_for("zaposleni"))
    upit = "DELETE FROM ocene_ucinka WHERE id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    konekcija.commit()

    upit = "SELECT AVG(ocena) AS rezultat FROM ocene_ucinka WHERE zaposleni_id=%s"
    vrednost = (zaposleni_id,)
    kursor.execute(upit, vrednost)
    prosek = kursor.fetchone()

    upit = """SELECT SUM(p.bodovi_vrednosti) AS rezultat
        FROM ocene_ucinka o
        JOIN projekti p ON o.projekat_id = p.id
        WHERE o.zaposleni_id=%s"""
    vrednost = (zaposleni_id,)
    kursor.execute(upit, vrednost)
    bodovi = kursor.fetchone()

    prosecna_ocena = prosek["rezultat"] if prosek["rezultat"] else 0
    ukupno_bodova = bodovi["rezultat"] if bodovi["rezultat"] else 0

    upit = "UPDATE zaposleni SET ukupno_bodova=%s, prosecna_ocena=%s WHERE id=%s"
    vrednosti = (ukupno_bodova, prosecna_ocena, zaposleni_id)
    kursor.execute(upit, vrednosti)
    konekcija.commit()

    return redirect(url_for("zaposleni_detalji", id=zaposleni_id))


@app.route("/projekti")
def projekti():
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    upit = "SELECT * FROM projekti"
    kursor.execute(upit)
    lista_projekata = kursor.fetchall()
    return render_template("projekti.html", projekti=lista_projekata)


@app.route("/projekti_novi", methods=["GET", "POST"])
def projekti_novi():
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    if request.method == "GET":
        return render_template("projekti_novi.html")
    elif request.method == "POST":
        forma = request.form
        upit = """INSERT INTO projekti (sifra, naziv, bodovi_vrednosti, status)
            VALUES (%s, %s, %s, %s)"""
        vrednosti = (
            forma["sifra"],
            forma["naziv"],
            forma["bodovi_vrednosti"],
            forma["status"],
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for("projekti"))


@app.route("/projekti_izmena/<id>", methods=["GET", "POST"])
def projekti_izmena(id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    if request.method == "GET":
        upit = "SELECT * FROM projekti WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        projekat = kursor.fetchone()
        return render_template("projekti_izmena.html", projekat=projekat)
    elif request.method == "POST":
        forma = request.form
        upit = """UPDATE projekti SET
            sifra=%s, naziv=%s, bodovi_vrednosti=%s, status=%s
            WHERE id=%s"""
        vrednosti = (
            forma["sifra"],
            forma["naziv"],
            forma["bodovi_vrednosti"],
            forma["status"],
            id,
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for("projekti"))


@app.route("/projekti_brisanje/<id>", methods=["POST"])
def projekti_brisanje(id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    upit = "DELETE FROM projekti WHERE id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    konekcija.commit()
    return redirect(url_for("projekti"))


@app.route("/korisnici")
def korisnici():
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    upit = "SELECT * FROM korisnici"
    kursor.execute(upit)
    lista_korisnika = kursor.fetchall()
    return render_template("korisnici.html", korisnici=lista_korisnika)


@app.route("/korisnici_novi", methods=["GET", "POST"])
def korisnici_novi():
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    if request.method == "GET":
        return render_template("korisnici_novi.html")
    elif request.method == "POST":
        forma = request.form

        upit = """INSERT INTO zaposleni
            (ime, prezime, maticni_broj, jmbg, broj_telefona, email)
            VALUES (%s, %s, %s, %s, %s, %s)"""
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["maticni_broj"],
            forma["jmbg"],
            forma["broj_telefona"],
            forma["email"],
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        novi_zaposleni_id = kursor.lastrowid

        hesovana_lozinka = generate_password_hash(forma["lozinka"])
        upit = """INSERT INTO korisnici (ime, prezime, email, lozinka, rola, zaposleni_id)
            VALUES (%s, %s, %s, %s, %s, %s)"""
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["email"],
            hesovana_lozinka,
            forma["rola"],
            novi_zaposleni_id,
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        return redirect(url_for("korisnici"))


@app.route("/korisnici_izmena/<id>", methods=["GET", "POST"])
def korisnici_izmena(id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    if request.method == "GET":
        upit = "SELECT * FROM korisnici WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        return render_template("korisnici_izmena.html", korisnik=korisnik)
    elif request.method == "POST":
        forma = request.form

        if forma["lozinka"]:
            hesovana_lozinka = generate_password_hash(forma["lozinka"])
            upit = """UPDATE korisnici SET
                ime=%s, prezime=%s, email=%s, lozinka=%s, rola=%s
                WHERE id=%s"""
            vrednosti = (
                forma["ime"],
                forma["prezime"],
                forma["email"],
                hesovana_lozinka,
                forma["rola"],
                id,
            )
        else:
            upit = """UPDATE korisnici SET
                ime=%s, prezime=%s, email=%s, rola=%s
                WHERE id=%s"""
            vrednosti = (
                forma["ime"],
                forma["prezime"],
                forma["email"],
                forma["rola"],
                id,
            )
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        upit = "SELECT zaposleni_id FROM korisnici WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        povezani = kursor.fetchone()
        if povezani and povezani["zaposleni_id"]:
            upit = "UPDATE zaposleni SET ime=%s, prezime=%s, email=%s WHERE id=%s"
            vrednosti = (forma["ime"], forma["prezime"], forma["email"], povezani["zaposleni_id"])
            kursor.execute(upit, vrednosti)
            konekcija.commit()

        return redirect(url_for("korisnici"))


@app.route("/korisnici_brisanje/<id>", methods=["POST"])
def korisnici_brisanje(id):
    if not ulogovan():
        return redirect(url_for("login"))
    if rola() != "administrator":
        return redirect(url_for("zaposleni"))
    upit = "DELETE FROM korisnici WHERE id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    konekcija.commit()
    return redirect(url_for("korisnici"))


# pokretanje aplikacije
if __name__ == "__main__":
    app.run(debug=True)