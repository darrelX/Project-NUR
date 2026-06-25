# ══════════════════════════════════════════════════════════════
# routes_ia.py — Routes Flask à intégrer dans ton app existante
# ══════════════════════════════════════════════════════════════
#
# Dans ton fichier principal (app.py / main.py), ajoute :
#   from breakdown_ia import classifier_fichier_excel, demander_cause_ia, verifier_serveur_ia
#   app.register_blueprint(routes_ia)
#
# Ou copie directement ces routes dans ton app si tu n'utilises
# pas de blueprints.
# ══════════════════════════════════════════════════════════════

import os
import tempfile
from flask import Blueprint, request, jsonify, send_file, render_template

from breakdown_ia import classifier_fichier_excel, demander_cause_ia, verifier_serveur_ia

routes_ia = Blueprint("routes_ia", __name__)


# ── PAGE CLASSIFICATION ────────────────────────────────────────
@routes_ia.route("/classification", methods=["GET"])
def page_classification():
    return render_template("classification.html")


@routes_ia.route("/api/classifier", methods=["POST"])
def api_classifier():
    """
    Reçoit le fichier Excel compilé (déjà nettoyé par l'app),
    l'envoie au serveur IA, renvoie le fichier résultat.
    """
    if "fichier" not in request.files:
        return jsonify({"erreur": "Aucun fichier reçu"}), 400

    fichier = request.files["fichier"]
    if fichier.filename == "":
        return jsonify({"erreur": "Nom de fichier vide"}), 400

    if not fichier.filename.endswith((".xlsx", ".xls")):
        return jsonify({"erreur": "Le fichier doit être un .xlsx ou .xls"}), 400

    # Sauvegarder temporairement le fichier uploadé
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        fichier.save(tmp.name)
        chemin_temp = tmp.name

    try:
        succes, resultat = classifier_fichier_excel(chemin_temp)
    finally:
        os.unlink(chemin_temp)

    if not succes:
        return jsonify({"erreur": resultat}), 502

    # Écrire le résultat dans un fichier temporaire pour l'envoyer
    chemin_resultat = tempfile.mktemp(suffix="_breakdown_classifie.xlsx")
    with open(chemin_resultat, "wb") as f:
        f.write(resultat)

    return send_file(
        chemin_resultat,
        as_attachment=True,
        download_name="breakdown_classifie.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ── PAGE CHAT ───────────────────────────────────────────────────
@routes_ia.route("/chat", methods=["GET"])
def page_chat():
    return render_template("chat.html")


@routes_ia.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Reçoit un commentaire (+ champs optionnels) depuis le front,
    retourne la cause et l'analyse du modèle.
    """
    data = request.get_json(silent=True) or {}
    commentaire = data.get("commentaire", "").strip()

    if not commentaire:
        return jsonify({"erreur": "Le commentaire ne peut pas être vide"}), 400

    owner = data.get("owner", "")
    topology = data.get("topology", "")
    vendors = data.get("vendors", "")

    succes, resultat = demander_cause_ia(commentaire, owner, topology, vendors)

    if not succes:
        return jsonify({"erreur": resultat}), 502

    return jsonify(resultat)


# ── VÉRIFICATION ÉTAT SERVEUR IA (pour affichage statut dans l'UI) ──
@routes_ia.route("/api/ia/health", methods=["GET"])
def api_ia_health():
    ok, info = verifier_serveur_ia()
    return jsonify({"disponible": ok, "info": info})