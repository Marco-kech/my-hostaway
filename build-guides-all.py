#!/usr/bin/env python3
"""Génère les 3 guides séparés (partenaire, propriétaire, voyageur) en PDF."""
from weasyprint import HTML

CSS = """
@page{size:A4;margin:18mm 16mm 22mm 16mm;
  @bottom-center{content:"GUIDE_TITLE · Page " counter(page);font-size:7.5px;color:#999}}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,Arial,sans-serif;font-size:10.5px;line-height:1.5;color:#222}
h1{font-size:26px;color:#14352A;margin:0 0 6px;font-family:Georgia,serif}
h2{font-size:16px;color:#14352A;margin:28px 0 8px;padding-bottom:3px;border-bottom:2px solid #C9A227;page-break-after:avoid}
h3{font-size:12.5px;color:#1d4a3a;margin:14px 0 5px;page-break-after:avoid}
h4{font-size:11px;color:#333;margin:10px 0 3px;page-break-after:avoid}
p,li{margin-bottom:3px}
ul,ol{padding-left:16px}
.cover{background:linear-gradient(135deg,#14352A 0%,#1d4a3a 100%);color:#F7F6F1;padding:50px 36px;border-radius:10px;margin-bottom:20px;page-break-after:always}
.cover h1{color:#C9A227;font-size:34px;margin-bottom:8px}
.cover .sub{font-size:15px;opacity:.85;margin-bottom:20px}
.cover .info{font-size:10px;opacity:.6;margin-top:30px}
.section{page-break-before:always}
.note{background:#f0edd8;border-left:3px solid #C9A227;padding:6px 10px;margin:6px 0;border-radius:3px;font-size:10px}
.warn{background:#fdf0e8;border-left:3px solid #d4772c;padding:6px 10px;margin:6px 0;border-radius:3px;font-size:10px}
.important{background:#e8f0e8;border-left:3px solid #2e7d52;padding:6px 10px;margin:6px 0;border-radius:3px;font-size:10px}
table{width:100%;border-collapse:collapse;margin:6px 0;font-size:9.5px}
th,td{padding:4px 6px;text-align:left;border:1px solid #ddd}
th{background:#14352A;color:#F7F6F1;font-weight:600;font-size:9px}
tr:nth-child(even){background:#fafaf5}
.box{background:#f7f6f1;border:1px solid #e5e2d8;border-radius:6px;padding:10px;margin:6px 0}
.box h4{margin:0 0 3px;color:#14352A}
.step{display:flex;gap:8px;margin:4px 0;align-items:flex-start}
.step .num{background:#C9A227;color:#14352A;font-weight:700;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0}
.step .txt{flex:1}
.example{background:#f5f5ff;border:1px solid #d0d0e8;border-radius:4px;padding:8px;margin:6px 0;font-size:10px}
.example b{color:#14352A}
hr{border:none;border-top:1px solid #e0e0e0;margin:12px 0}
"""

def step(n, txt):
    return f'<div class="step"><div class="num">{n}</div><div class="txt">{txt}</div></div>'

def build_pdf(title, subtitle, icon, url, body_html, filename, footer_title):
    cover = f"""
    <div class="cover">
      <div style="font-size:12px;letter-spacing:3px;margin-bottom:16px;color:#C9A227">DPM CONCIERGERIE</div>
      <h1>{icon} {title}</h1>
      <div class="sub">{subtitle}</div>
      <div class="info">
        Version 1.0 — novembre 2026<br>
        Adresse : {url}<br>
        DPM Consulting Group — Marrakech, Maroc
      </div>
    </div>
    """
    css = CSS.replace("GUIDE_TITLE", footer_title)
    html = f'<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head><body>{cover}{body_html}</body></html>'
    with open(filename.replace('.pdf','.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    HTML(string=html).write_pdf(filename)
    import os
    print(f"  {filename}: {os.path.getsize(filename)//1024} KB")

# =============================
# GUIDE PARTENAIRE
# =============================
print("Building guide partenaire...")
partenaire_body = """
<div class="section">
<h2>1. Bienvenue dans votre espace partenaire</h2>
<p>En tant que partenaire DPM Conciergerie, vous proposez vos prestations (spa, transport, excursions, restauration…) aux voyageurs des villas et riads gérés par DPM. Votre espace vous permet de suivre vos commandes, gérer vos prestations et consulter vos statistiques.</p>

<h3>1.1 Votre adresse de connexion</h3>
<p>Votre espace est accessible à l'adresse :<br><b>https://marco-kech.github.io/my-hostaway/partenaire/</b></p>
<p>Vous pouvez aussi l'installer sur votre téléphone comme une application : ouvrez le lien dans Chrome, puis « Ajouter à l'écran d'accueil ».</p>

<h3>1.2 Créer votre compte</h3>
""" + step(1, "Ouvrez le lien ci-dessus dans votre navigateur") + """
""" + step(2, "Cliquez <b>« Devenir partenaire »</b>") + """
""" + step(3, "Remplissez le formulaire d'inscription : votre nom, votre email, votre activité") + """
""" + step(4, "Votre demande est envoyée à l'équipe DPM") + """
""" + step(5, "DPM valide votre demande et rattache votre compte à votre fiche partenaire") + """
""" + step(6, "Vous recevez un email de confirmation. Connectez-vous avec votre email et mot de passe.") + """
<div class="note">💡 En attendant la validation, vous verrez un message « Votre demande est en cours de traitement ». DPM traite les demandes sous 24-48h.</div>
</div>

<div class="section">
<h2>2. Votre tableau de bord</h2>
<p>Après connexion, vous arrivez sur votre tableau de bord qui résume votre activité :</p>
<table>
<tr><th style="width:35%">Information</th><th>Ce qu'elle indique</th></tr>
<tr><td><b>Réservations à confirmer</b></td><td>Nombre de commandes en attente de votre confirmation</td></tr>
<tr><td><b>Réservations confirmées</b></td><td>Nombre de commandes validées ce mois</td></tr>
<tr><td><b>Revenus prestations</b></td><td>Votre chiffre d'affaires du mois (net reversé)</td></tr>
<tr><td><b>Panier moyen</b></td><td>Montant moyen par commande</td></tr>
</table>
</div>

<div class="section">
<h2>3. Mes prestations</h2>
<p>Cette page liste toutes les prestations que vous proposez via DPM. Pour chaque prestation, vous voyez :</p>
<table>
<tr><th>Colonne</th><th>Description</th></tr>
<tr><td>Nom</td><td>Le nom de la prestation tel qu'il apparaît au voyageur</td></tr>
<tr><td>Catégorie</td><td>Bien-être, Transport, Excursion, Restauration…</td></tr>
<tr><td>Prix</td><td>Le prix facturé au voyageur</td></tr>
<tr><td>Net partenaire</td><td>Ce que vous recevez (après commission DPM)</td></tr>
<tr><td>Statut</td><td>Active ou inactive</td></tr>
</table>

<h3>3.1 Modifier une prestation</h3>
<p>Si DPM vous a donné le droit de modifier vos prestations (mention « Édite ses prestations » dans votre fiche) :</p>
""" + step(1, "Cliquez sur ✏️ à côté de la prestation") + """
""" + step(2, "Modifiez le prix, la description ou les horaires") + """
""" + step(3, "Cliquez <b>Enregistrer</b>") + """
<div class="warn">⚠️ Si le bouton ✏️ n'apparaît pas, contactez DPM pour activer ce droit sur votre fiche.</div>

<h3>3.2 Comprendre le calcul de votre reversement</h3>
<div class="example">
<b>Exemple :</b> Vous proposez un massage à 600 DH.<br>
Commission DPM : 15%<br>
<b>Votre net : 600 − (600 × 15%) = 510 DH</b><br><br>
Un voyageur commande 2 massages → vous recevez 2 × 510 = <b>1 020 DH</b>
</div>
</div>

<div class="section">
<h2>4. Réservations reçues (commandes)</h2>
<p>Toutes les réservations de prestations commandées par les voyageurs. Pour chaque commande :</p>
<table>
<tr><th>Colonne</th><th>Description</th></tr>
<tr><td>Date</td><td>Date et heure de la prestation</td></tr>
<tr><td>Prestation</td><td>Quelle prestation a été commandée</td></tr>
<tr><td>Bien</td><td>Dans quelle villa/riad le voyageur séjourne</td></tr>
<tr><td>Voyageur</td><td>Nom du voyageur</td></tr>
<tr><td>Quantité</td><td>Nombre de personnes / unités</td></tr>
<tr><td>Montant</td><td>Le montant que vous recevrez (votre net)</td></tr>
<tr><td>Statut</td><td>en_attente, confirmé, fait, annulé</td></tr>
</table>

<h3>4.1 Confirmer une commande</h3>
<p>Quand un voyageur commande une de vos prestations, elle apparaît en statut <b>« en_attente »</b>. Vous devez la confirmer :</p>
""" + step(1, "Ouvrez <b>Réservations</b>") + """
""" + step(2, "Repérez la commande en jaune « en_attente »") + """
""" + step(3, "Vérifiez la date, l'heure et le nombre de personnes") + """
""" + step(4, "Cliquez <b>Confirmer</b> si vous êtes disponible") + """
""" + step(5, "Ou cliquez <b>Refuser</b> si vous n'êtes pas disponible (le voyageur sera prévenu)") + """
<div class="important">✅ Répondez rapidement — les voyageurs attendent une confirmation pour organiser leur journée.</div>
</div>

<div class="section">
<h2>5. Statistiques</h2>
<p>Votre tableau de bord statistique mensuel :</p>
<ul>
<li><b>Chiffre d'affaires</b> : total de vos reversements du mois</li>
<li><b>Nombre de commandes</b> : commandes confirmées ce mois</li>
<li><b>Panier moyen</b> : montant moyen par commande</li>
<li><b>Top prestations</b> : vos prestations les plus commandées</li>
</ul>
<p>Utilisez les flèches ← → pour naviguer entre les mois.</p>
</div>

<div class="section">
<h2>6. Ma fiche</h2>
<p>Consultez et mettez à jour vos informations : nom, activité, contact, téléphone, email, adresse. Ces informations sont utilisées par DPM pour vous contacter et vous reverser vos paiements.</p>

<h2>7. Messages</h2>
<p>Échangez des messages avec l'équipe DPM. Idéal pour poser des questions, signaler un problème ou coordonner une prestation spéciale.</p>

<h2>8. Questions fréquentes</h2>
<h3>Comment je suis payé ?</h3>
<p>DPM vous reverse votre net partenaire selon les conditions définies dans votre fiche (virement, délai). Contactez DPM pour les détails.</p>

<h3>Puis-je refuser une commande ?</h3>
<p>Oui. Cliquez « Refuser » sur la commande. Le voyageur sera informé et pourra choisir une autre prestation ou une autre date.</p>

<h3>Comment ajouter une nouvelle prestation ?</h3>
<p>Contactez DPM — l'ajout de nouvelles prestations se fait en coordination avec l'équipe pour définir le prix, la commission et les horaires.</p>

<h3>Puis-je voir ce que voit le voyageur ?</h3>
<p>Non depuis votre espace. Demandez à DPM de vous montrer via la fonction « Voir comme partenaire » dans leur administration.</p>
</div>
"""

build_pdf(
    "Espace Partenaire",
    "Guide d'utilisation pour les prestataires DPM Conciergerie",
    "🤝",
    "https://marco-kech.github.io/my-hostaway/partenaire/",
    partenaire_body,
    "guide-partenaire.pdf",
    "Guide Partenaire — DPM Conciergerie"
)

# =============================
# GUIDE PROPRIÉTAIRE
# =============================
print("Building guide propriétaire...")
proprietaire_body = """
<div class="section">
<h2>1. Bienvenue dans votre espace propriétaire</h2>
<p>En tant que propriétaire d'un bien géré par DPM Conciergerie, votre espace vous permet de suivre vos réservations, vos revenus, l'activité de vos biens et les prestations internes que vous proposez aux voyageurs.</p>

<h3>1.1 Votre adresse de connexion</h3>
<p>Votre espace est accessible à l'adresse :<br><b>https://marco-kech.github.io/my-hostaway/proprietaire/</b></p>
<p>Vous pouvez aussi l'installer sur votre téléphone : ouvrez le lien dans Chrome, puis « Ajouter à l'écran d'accueil ».</p>

<h3>1.2 Créer votre compte (inscription)</h3>
""" + step(1, "Ouvrez le lien ci-dessus dans votre navigateur") + """
""" + step(2, "Cliquez le bouton <b>« Devenir propriétaire »</b> sur la page de connexion") + """
""" + step(3, "Remplissez le formulaire d'inscription : votre nom complet, votre adresse email et choisissez un mot de passe") + """
""" + step(4, "Votre demande est envoyée à l'équipe DPM") + """
""" + step(5, "DPM valide votre demande et rattache votre compte à votre fiche propriétaire (sous 24-48h)") + """
""" + step(6, "Vous recevez un email de confirmation. Connectez-vous avec votre email et votre mot de passe.") + """
<div class="note">💡 En attendant la validation, vous verrez un message « Votre demande est en cours de traitement ». DPM traite les demandes sous 24-48h.</div>
</div>

<div class="section">
<h2>2. Votre tableau de bord</h2>
<p>Après connexion, vous voyez la synthèse de vos biens :</p>
<table>
<tr><th style="width:35%">Information</th><th>Ce qu'elle indique</th></tr>
<tr><td><b>Mes biens</b></td><td>Liste de vos villas, riads ou appartements gérés par DPM</td></tr>
<tr><td><b>Réservations confirmées</b></td><td>Nombre de séjours confirmés ce mois sur vos biens</td></tr>
<tr><td><b>Taux d'occupation</b></td><td>Pourcentage de nuits louées sur vos biens</td></tr>
<tr><td><b>Revenus du mois</b></td><td>Revenus nets (après commission DPM) sur vos biens</td></tr>
</table>
</div>

<div class="section">
<h2>3. Réservations</h2>
<p>Toutes les réservations sur vos biens. Pour chaque réservation :</p>
<table>
<tr><th>Colonne</th><th>Description</th></tr>
<tr><td>Bien</td><td>Lequel de vos biens est concerné</td></tr>
<tr><td>Voyageur</td><td>Nom du voyageur</td></tr>
<tr><td>Arrivée / Départ</td><td>Dates du séjour</td></tr>
<tr><td>Canal</td><td>Airbnb, Booking, direct…</td></tr>
<tr><td>Montant</td><td>Prix total du séjour</td></tr>
<tr><td>Statut</td><td>confirmée, terminée, annulée…</td></tr>
</table>
<div class="note">💡 Les réservations sont gérées par DPM. Vous les consultez ici pour suivre l'activité de vos biens.</div>
</div>

<div class="section">
<h2>4. Revenus</h2>
<p>Détail de vos revenus mois par mois :</p>
<ul>
<li><b>Revenus bruts</b> : total des réservations encaissées</li>
<li><b>Commission DPM</b> : pourcentage retenu par DPM (défini dans votre contrat)</li>
<li><b>Dépenses</b> : charges déduites (ménage, maintenance, consommables…)</li>
<li><b>Revenus prestations internes</b> : si vos employés fournissent des prestations aux voyageurs</li>
<li><b>Net à recevoir</b> : ce qui vous est reversé</li>
</ul>

<div class="example">
<b>Exemple — Novembre 2026 :</b><br>
• Revenus bruts : 24 000 DH<br>
• Commission DPM (20%) : −4 800 DH<br>
• Dépenses (ménage × 3, réparation) : −1 550 DH<br>
• Prestations internes vendues : +1 800 DH<br>
• Commission DPM sur prestations (20%) : −360 DH<br>
• <b>Net à recevoir : 19 090 DH</b>
</div>
</div>

<div class="section">
<h2>5. Planning & remplissage</h2>
<p>Calendrier visuel de vos biens montrant :</p>
<ul>
<li>Les jours <b>occupés</b> (réservation confirmée)</li>
<li>Les jours <b>disponibles</b></li>
<li>Les jours <b>bloqués</b> (par vous ou par le ménage entre deux séjours)</li>
</ul>
<p>Utile pour savoir quand vous pouvez utiliser votre bien personnellement.</p>

<h2>6. Statistiques</h2>
<p>Synthèse mensuelle : occupation, revenus, nombre de réservations, comparaison avec les mois précédents.</p>

<h2>7. Ma fiche</h2>
<p>Vos informations personnelles : nom, email, téléphone, adresse, coordonnées bancaires pour les reversements.</p>

<h2>8. Messages</h2>
<p>Échangez avec l'équipe DPM : questions, demandes de travaux, signalements.</p>

<h2>9. Questions fréquentes</h2>

<h3>Quand suis-je payé ?</h3>
<p>DPM génère un relevé mensuel (généralement le 5 du mois suivant) et vous reverse le net sous le délai convenu dans votre contrat.</p>

<h3>Puis-je bloquer des dates pour usage personnel ?</h3>
<p>Oui. Contactez DPM pour qu'ils bloquent les dates souhaitées. La réservation sera marquée « séjour propriétaire ».</p>

<h3>Comment suivre les dépenses sur mon bien ?</h3>
<p>Toutes les dépenses (ménage, réparations, consommables) apparaissent dans votre relevé mensuel, déduites de vos revenus.</p>

<h3>Mes prestations internes (petit-déjeuner, dîner…) ?</h3>
<p>Si votre personnel fournit des prestations aux voyageurs (cuisine, ménage supplémentaire…), les revenus correspondants apparaissent dans vos revenus avec la commission DPM déduite.</p>
</div>
"""

build_pdf(
    "Espace Propriétaire",
    "Guide d'utilisation pour les propriétaires de biens DPM Conciergerie",
    "🏠",
    "https://marco-kech.github.io/my-hostaway/proprietaire/",
    proprietaire_body,
    "guide-proprietaire.pdf",
    "Guide Propriétaire — DPM Conciergerie"
)

# =============================
# GUIDE VOYAGEUR
# =============================
print("Building guide voyageur...")
voyageur_body = """
<div class="section">
<h2>1. Bienvenue</h2>
<p>Pendant votre séjour dans une villa ou un riad géré par DPM Conciergerie à Marrakech, vous avez accès à un espace personnel en ligne. Cet espace vous permet de :</p>
<ul>
<li>Retrouver toutes les <b>informations pratiques</b> de votre logement (adresse, wifi, code d'accès)</li>
<li>Découvrir et <b>commander des prestations</b> (massage, excursion, transfert aéroport, chef privé…)</li>
<li>Suivre vos <b>demandes</b> et communiquer avec l'équipe</li>
</ul>

<h3>1.1 Comment accéder à votre espace</h3>
<p>Vous avez reçu un <b>lien personnel</b> par WhatsApp ou par email de la part de DPM. Ce lien est unique et ne fonctionne que pour votre séjour.</p>
""" + step(1, "Cliquez sur le lien reçu (il ressemble à : .../sejour/#/s/abc123…)") + """
""" + step(2, "Votre espace s'ouvre dans le navigateur — aucun compte à créer, aucun mot de passe") + """
<div class="note">💡 Ajoutez la page à vos favoris ou à l'écran d'accueil de votre téléphone pour y accéder facilement pendant tout votre séjour.</div>
<div class="warn">⚠️ Le lien est personnel et temporaire. Il est actif pendant votre séjour et jusqu'à 30 jours après votre départ.</div>
</div>

<div class="section">
<h2>2. Informations de votre logement</h2>
<p>La page d'accueil de votre espace affiche :</p>
<table>
<tr><th style="width:30%">Information</th><th>Détail</th></tr>
<tr><td><b>Nom du logement</b></td><td>Le nom de votre villa ou riad</td></tr>
<tr><td><b>Dates du séjour</b></td><td>Vos dates d'arrivée et de départ</td></tr>
<tr><td><b>Adresse</b></td><td>L'adresse complète avec un lien vers Google Maps</td></tr>
<tr><td><b>Code Wifi</b></td><td>Nom du réseau et mot de passe</td></tr>
<tr><td><b>Code de porte</b></td><td>Le code d'accès ou la localisation de la boîte à clés</td></tr>
<tr><td><b>Instructions d'arrivée</b></td><td>Comment trouver le logement, où se garer, qui contacter</td></tr>
<tr><td><b>Contact d'urgence</b></td><td>Numéro à appeler en cas de besoin</td></tr>
<tr><td><b>Règlement intérieur</b></td><td>Les règles du logement</td></tr>
</table>
</div>

<div class="section">
<h2>3. Commander une prestation</h2>
<p>DPM Conciergerie vous propose un catalogue de prestations pendant votre séjour. Ouvrez l'onglet <b>« Catalogue »</b> pour découvrir ce qui est disponible :</p>

<h3>Exemples de prestations disponibles :</h3>
<table>
<tr><th>Catégorie</th><th>Exemples</th></tr>
<tr><td>🧖 Bien-être</td><td>Massage à domicile, hammam & gommage, coiffure & beauté</td></tr>
<tr><td>🍽️ Restauration</td><td>Chef privé, petit-déjeuner livré, dîner au bord de la piscine</td></tr>
<tr><td>🏜️ Excursions</td><td>Quad dans l'Agafay, journée à Essaouira, vol en montgolfière</td></tr>
<tr><td>🚘 Transport</td><td>Transfert aéroport, chauffeur à disposition</td></tr>
<tr><td>🏠 Services</td><td>Ménage supplémentaire, blanchisserie, garde d'enfants</td></tr>
<tr><td>⛳ Loisirs</td><td>Golf, guide privé dans la médina, séance photo</td></tr>
</table>

<h3>3.1 Passer une commande</h3>
""" + step(1, "Ouvrez le <b>Catalogue</b>") + """
""" + step(2, "Parcourez les prestations — elles sont classées par catégorie") + """
""" + step(3, "Cliquez sur <b>« Commander »</b> sur la prestation souhaitée") + """
""" + step(4, "Choisissez la <b>date</b> et l'<b>heure</b> souhaitées") + """
""" + step(5, "Indiquez le <b>nombre de personnes</b> (ou la quantité)") + """
""" + step(6, "Ajoutez un <b>commentaire</b> si besoin (allergie, préférence, précision…)") + """
""" + step(7, "Cliquez <b>« Envoyer la demande »</b>") + """

<div class="note">💡 Votre demande est envoyée à l'équipe DPM qui la confirme avec le prestataire. Vous recevez une notification quand c'est confirmé.</div>

<h3>3.2 Tarifs</h3>
<p>Les prix affichés sont les prix par personne (ou par unité selon la prestation). Le total est calculé automatiquement selon la quantité choisie. Les prestations sont facturées sur place ou ajoutées à votre note de séjour.</p>
</div>

<div class="section">
<h2>4. Suivre vos demandes</h2>
<p>L'onglet <b>« Mes demandes »</b> liste toutes vos commandes avec leur statut :</p>
<table>
<tr><th>Statut</th><th>Signification</th></tr>
<tr><td style="color:#C9A227"><b>En attente</b></td><td>Votre demande a été envoyée. L'équipe la traite sous quelques heures.</td></tr>
<tr><td style="color:#2e7d52"><b>Confirmée</b></td><td>La prestation est confirmée. Le prestataire sera là à l'heure convenue.</td></tr>
<tr><td style="color:#2e7d52"><b>Fait</b></td><td>La prestation a été réalisée.</td></tr>
<tr><td style="color:#A33A2A"><b>Refusée</b></td><td>La prestation n'est pas disponible à cette date/heure. Essayez une autre date.</td></tr>
</table>

<h2>5. Messages</h2>
<p>L'onglet <b>« Messages »</b> vous permet d'échanger directement avec l'équipe DPM pendant votre séjour : questions, besoins spéciaux, retours.</p>

<h2>6. Questions fréquentes</h2>

<h3>Dois-je créer un compte ?</h3>
<p>Non. Votre lien personnel suffit. Pas de mot de passe, pas d'inscription.</p>

<h3>Le lien ne fonctionne plus ?</h3>
<p>Le lien est actif pendant votre séjour et 30 jours après votre départ. Si votre séjour n'a pas encore commencé ou est trop ancien, le lien est désactivé. Contactez DPM.</p>

<h3>Puis-je commander pour plusieurs personnes ?</h3>
<p>Oui. Indiquez la quantité souhaitée lors de la commande (ex : 4 massages, 6 petits-déjeuners).</p>

<h3>Comment annuler une commande ?</h3>
<p>Contactez l'équipe DPM via l'onglet Messages. Les annulations sont possibles selon le préavis de chaque prestation.</p>

<h3>Puis-je commander pour un autre jour que celui de mon séjour ?</h3>
<p>Non. Les prestations ne sont disponibles que pendant vos dates de séjour.</p>
</div>
"""

build_pdf(
    "Espace Voyageur",
    "Guide pour les voyageurs — Commander des prestations pendant votre séjour",
    "✈️",
    "Lien personnel reçu par WhatsApp ou email",
    voyageur_body,
    "guide-voyageur.pdf",
    "Guide Voyageur — DPM Conciergerie"
)

print("\nAll guides generated!")
