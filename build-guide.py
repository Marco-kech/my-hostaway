#!/usr/bin/env python3
"""Génère le guide complet My Hostaway en HTML puis PDF via WeasyPrint."""

from weasyprint import HTML
import html as H

CSS = """
@page{size:A4;margin:18mm 16mm 22mm 16mm;
  @bottom-center{content:"My Hostaway — Guide d'utilisation · Page " counter(page);font-size:7.5px;color:#999}}
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
.toc{page-break-after:always}
.toc h2{border:none;font-size:20px}
.toc ul{list-style:none;padding:0}
.toc li{padding:3px 0;border-bottom:1px dotted #ddd;font-size:11px}
.toc li.l2{padding-left:14px;font-size:10px;color:#555}
.section{page-break-before:always}
.note{background:#f0edd8;border-left:3px solid #C9A227;padding:6px 10px;margin:6px 0;border-radius:3px;font-size:10px}
.warn{background:#fdf0e8;border-left:3px solid #d4772c;padding:6px 10px;margin:6px 0;border-radius:3px;font-size:10px}
.important{background:#e8f0e8;border-left:3px solid #2e7d52;padding:6px 10px;margin:6px 0;border-radius:3px;font-size:10px}
table{width:100%;border-collapse:collapse;margin:6px 0;font-size:9.5px}
th,td{padding:4px 6px;text-align:left;border:1px solid #ddd}
th{background:#14352A;color:#F7F6F1;font-weight:600;font-size:9px}
tr:nth-child(even){background:#fafaf5}
.cols2{display:flex;gap:14px}.cols2>div{flex:1}
.box{background:#f7f6f1;border:1px solid #e5e2d8;border-radius:6px;padding:10px;margin:6px 0}
.box h4{margin:0 0 3px;color:#14352A}
.step{display:flex;gap:8px;margin:4px 0;align-items:flex-start}
.step .num{background:#C9A227;color:#14352A;font-weight:700;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0}
.step .txt{flex:1}
.kbd{background:#eee;padding:1px 4px;border-radius:2px;font-family:monospace;font-size:9px;border:1px solid #ccc}
.example{background:#f5f5ff;border:1px solid #d0d0e8;border-radius:4px;padding:8px;margin:6px 0;font-size:10px}
.example b{color:#14352A}
hr{border:none;border-top:1px solid #e0e0e0;margin:12px 0}
"""

def step(n, txt):
    return f'<div class="step"><div class="num">{n}</div><div class="txt">{txt}</div></div>'

def field_table(fields):
    """Generate a detailed field documentation table."""
    rows = ""
    for f in fields:
        rows += f"<tr><td><b>{f[0]}</b></td><td>{f[1]}</td><td>{f[2]}</td></tr>\n"
    return f'<table><tr><th style="width:25%">Champ</th><th style="width:40%">Description</th><th>Valeurs / Options</th></tr>{rows}</table>'


body = ""

# ============= COUVERTURE =============
body += """
<div class="cover">
  <div style="font-size:12px;letter-spacing:3px;margin-bottom:16px;color:#C9A227">DPM CONCIERGERIE</div>
  <h1>My Hostaway</h1>
  <div class="sub">Guide complet d'utilisation</div>
  <p style="font-size:12px;max-width:480px;line-height:1.6">
    Ce guide couvre l'intégralité de l'application My Hostaway : chaque rubrique, chaque formulaire,
    chaque fonctionnalité — avec des procédures pas à pas, des exemples concrets et des conseils pratiques.<br><br>
    <b>Pour qui :</b> Administrateurs DPM, gestionnaires, collaborateurs.<br>
    <b>Guides séparés :</b> Espace partenaire (chapitre 16), Espace propriétaire (chapitre 17), Espace voyageur (chapitre 18).
  </p>
  <div class="info">
    Version 1.0 — novembre 2026<br>
    Application : https://marco-kech.github.io/my-hostaway/<br>
    Espace partenaire : .../partenaire/ · Espace propriétaire : .../proprietaire/ · Espace voyageur : .../sejour/<br>
    DPM Consulting Group — Marrakech, Maroc
  </div>
</div>
"""

# ============= TABLE DES MATIÈRES =============
toc_items = [
    ("1", "Prise en main", [
        "1.1 Les 4 interfaces de My Hostaway",
        "1.2 Connexion et navigation",
        "1.3 L'écran principal — menu, sous-menus, barre du haut",
        "1.4 Raccourcis clavier",
        "1.5 Mode sombre et impression",
    ]),
    ("2", "Vue d'ensemble — Tableau de bord", [
        "2.1 KPI et indicateurs",
        "2.2 Demandes à traiter (commandes en attente)",
    ]),
    ("3", "Calendrier — 3 vues", [
        "3.1 Vue multiple (tous les biens)",
        "3.2 Vue mensuelle",
        "3.3 Vue annuelle (taux d'occupation)",
    ]),
    ("4", "Boîte de réception — Messagerie complète", [
        "4.1 Conversations",
        "4.2 Réponses IA et Base de connaissances",
        "4.3 Modèles de message",
        "4.4 Messages automatisés — déclencheurs et brouillons",
        "4.5 Messages récurrents, Campagnes, Règles et Escalades",
    ]),
    ("5", "Réservations", [
        "5.1 Créer une réservation manuelle — procédure complète",
        "5.2 Accepter ou refuser une demande",
        "5.3 Fiche de réservation — tous les champs",
        "5.4 Contrat PDF automatique",
        "5.5 Check-in en ligne",
        "5.6 Coupons de réduction",
        "5.7 Importer des réservations",
    ]),
    ("6", "Annonces (Biens) — Fiche détaillée", [
        "6.1 Créer un bien — les 9 sections du formulaire",
        "6.2 Section par section : Identité, Description, Localisation",
        "6.3 Capacité, Tarifs, Remises, Politiques d'annulation",
        "6.4 Majorations par canal et frais personnalisés",
        "6.5 Arrivée et accès (code porte, wifi, instructions)",
        "6.6 Chambres & lits, Équipements",
        "6.7 Fenêtre de réservation et conditions",
        "6.8 Photos et pièces jointes",
        "6.9 Score ASO — optimiser ses annonces",
        "6.10 Multi-unités / Chambres",
        "6.11 Groupes, Duplication, Édition en masse",
    ]),
    ("7", "Tâches — Kanban, automatisation, checklists", [
        "7.1 Vue Kanban (À faire / En cours / Fait)",
        "7.2 Créer une tâche — champs et assignation",
        "7.3 Tâches automatiques — règles de déclenchement",
        "7.4 Modèles de checklist",
    ]),
    ("8", "Avis — Gestion et automatisation", []),
    ("9", "Rapports financiers", [
        "9.1 Analytique — graphiques et comparaisons",
        "9.2 Activité de location, Occupation, Formules",
        "9.3 Taxes, Paramètres financiers, Export comptable",
        "9.4 Prévisionnel et Rapport mensuel",
    ]),
    ("10", "Dépenses & suppléments", [
        "10.1 Créer une dépense ou un supplément",
        "10.2 Catégories personnalisées",
        "10.3 Automatisations (dépenses récurrentes)",
    ]),
    ("11", "Paiements voyageurs", [
        "11.1 Encaissements — suivi des paiements",
        "11.2 Factures voyageurs — génération et TVA",
        "11.3 Dépôts de garantie — cycle de vie",
        "11.4 Modèles de document",
        "11.5 Paramètres PayPal et CMI",
    ]),
    ("12", "Relevés propriétaire", [
        "12.1 Générer un relevé mensuel",
        "12.2 Relevés automatiques",
        "12.3 Tableau de bord propriétaire",
    ]),
    ("13", "Tarification", [
        "13.1 Tarifs saisonniers — priorité et chevauchement",
        "13.2 Calendrier tarifaire",
        "13.3 Extras & frais (par nuit, par personne, obligatoire)",
        "13.4 Tarification dynamique",
        "13.5 Minimum de nuits",
    ]),
    ("14", "Gestionnaire de canaux", [
        "14.1 Canaux connectés (Airbnb, Booking, VRBO)",
        "14.2 Synchronisation iCal",
        "14.3 Plans tarifaires Booking",
    ]),
    ("15", "Conciergerie — Prestations", [
        "15.1 Les 3 types de prestations (DPM, externe, interne)",
        "15.2 Créer une prestation — procédure complète",
        "15.3 Tarifs, commissions et net partenaire — avec exemples",
        "15.4 Horaires : plages, départs fixes, créneaux",
        "15.5 Liste avec onglets et filtres",
        "15.6 Options par bien — sélection personnalisée",
        "15.7 Équipes internes (services)",
    ]),
    ("16", "Conciergerie — Partenaires", [
        "16.1 Créer un partenaire — tous les champs",
        "16.2 Fiche partenaire complète",
        "16.3 Droits : modification prestations et promotions",
        "16.4 Statistiques et réservations reçues",
        "16.5 Espace partenaire — ce que voit le partenaire",
    ]),
    ("17", "Conciergerie — Propriétaires", [
        "17.1 Créer un propriétaire — tous les champs",
        "17.2 Fiche propriétaire complète",
        "17.3 Biens, Planning & remplissage, Revenus consolidés",
        "17.4 Prestations internes",
        "17.5 Espace propriétaire — ce que voit le propriétaire",
    ]),
    ("18", "Conciergerie — Voyageurs", [
        "18.1 Livre d'or — fiche voyageur",
        "18.2 Liens d'accès séjour — créer, copier, désactiver",
        "18.3 Espace voyageur — ce que voit le voyageur",
    ]),
    ("19", "Commandes & Statistiques de la conciergerie", [
        "19.1 Demandes de prestations — confirmer, refuser, marquer fait",
        "19.2 Statistiques globales de la conciergerie",
    ]),
    ("20", "Fiches & droits — Page centralisée", [
        "20.1 Les 5 onglets (Propriétaires, Partenaires, Séjours, Collaborateurs, Comptes)",
        "20.2 « Voir son espace » — aperçu administrateur",
        "20.3 Collaborateurs — invitation, rubriques, statut",
        "20.4 Comptes & accès — validation des demandes",
    ]),
    ("21", "Utilisateurs & groupes", []),
    ("22", "Moteur de réservation (site direct)", [
        "22.1 Design, Annonces publiées, Pages",
        "22.2 Livret d'accueil numérique",
        "22.3 SEO & Analytics, Traductions",
    ]),
    ("23", "Branchements & outils", [
        "23.1 Serrures intelligentes",
        "23.2 Assurance et Marketplace",
    ]),
    ("24", "Paramètres", [
        "24.1 Compte, Langues, Notifications",
        "24.2 Paiement CMI, WhatsApp, SMS",
        "24.3 Webhooks, API, Journal d'activité",
        "24.4 Politiques d'annulation",
    ]),
    ("25", "Annexes", [
        "A. Glossaire",
        "B. Calcul des commissions — exemples détaillés",
        "C. FAQ — Questions fréquentes",
        "D. Résolution de problèmes courants",
    ]),
]

toc_html = '<div class="toc"><h2>Table des matières</h2><ul>\n'
for num, title, subs in toc_items:
    toc_html += f'<li><b>{num}. {title}</b></li>\n'
    for s in subs:
        toc_html += f'<li class="l2">{s}</li>\n'
toc_html += '</ul></div>\n'
body += toc_html

# ============= CHAPITRE 1 — PRISE EN MAIN =============
body += """
<div class="section">
<h2>1. Prise en main</h2>

<h3>1.1 Les 4 interfaces de My Hostaway</h3>
<p>My Hostaway comprend <b>4 interfaces distinctes</b>, chacune adaptée à un profil d'utilisateur :</p>

<div class="cols2">
<div class="box">
  <h4>🏢 Interface Admin (cette interface)</h4>
  <p><b>URL :</b> /my-hostaway/</p>
  <p><b>Pour :</b> L'équipe DPM (vous, Laurent, gestionnaires)</p>
  <p><b>Accès :</b> Toutes les rubriques, toutes les données, tous les biens, tous les partenaires et propriétaires</p>
  <p><b>Droits :</b> Création, modification, suppression, validation des comptes, configuration</p>
</div>
<div class="box">
  <h4>🤝 Interface Partenaire</h4>
  <p><b>URL :</b> /my-hostaway/partenaire/</p>
  <p><b>Pour :</b> Les prestataires externes (spa, transport, excursions…)</p>
  <p><b>Accès :</b> Uniquement ses propres prestations, commandes reçues et statistiques</p>
  <p><b>Droits :</b> Consultation. Si « Peut modifier ses prestations » est activé dans sa fiche : peut ajuster prix et descriptions. Si « Peut créer des promotions » : peut créer des offres spéciales.</p>
  <p><b>Création du compte :</b> Le partenaire demande un accès depuis l'URL ci-dessus. L'admin valide sa demande dans Comptes & accès et rattache le compte à sa fiche partenaire.</p>
</div>
</div>
<div class="cols2">
<div class="box">
  <h4>🏠 Interface Propriétaire</h4>
  <p><b>URL :</b> /my-hostaway/proprietaire/</p>
  <p><b>Pour :</b> Les propriétaires des biens en gestion</p>
  <p><b>Accès :</b> Ses biens, ses réservations, ses revenus, ses prestations internes</p>
  <p><b>Droits :</b> Consultation uniquement (sauf droits spécifiques activés par l'admin)</p>
  <p><b>Création du compte :</b> Même processus que le partenaire : demande depuis l'URL, validation par l'admin.</p>
</div>
<div class="box">
  <h4>✈️ Interface Voyageur</h4>
  <p><b>URL :</b> /my-hostaway/sejour/#/s/{token}</p>
  <p><b>Pour :</b> Le voyageur pendant son séjour</p>
  <p><b>Accès :</b> Informations du logement (adresse, wifi, code porte, instructions), catalogue des prestations disponibles pour ce bien, formulaire de commande, suivi de ses demandes</p>
  <p><b>Droits :</b> Consultation + commande de prestations</p>
  <p><b>Pas de compte :</b> Accès par lien unique généré par l'admin. Le lien expire 30 jours après le départ.</p>
</div>
</div>

<h3>1.2 Connexion et navigation</h3>
<p>Ouvrez l'application dans votre navigateur. L'authentification est gérée par Supabase (email + mot de passe). Après connexion, vous arrivez sur le <b>Tableau de bord</b>.</p>

<h4>Structure de l'écran</h4>
<table>
<tr><th style="width:25%">Zone</th><th>Description</th></tr>
<tr><td><b>Menu latéral gauche</b></td><td>22 rubriques principales. Cliquez sur une rubrique pour la déplier et voir ses sous-menus. La rubrique active est surlignée en vert.</td></tr>
<tr><td><b>Sous-onglets (en haut)</b></td><td>Quand une rubrique a plusieurs sous-pages, les onglets apparaissent sous le titre de la rubrique. Ex : Conciergerie → Demandes / Statistiques / Toutes les prestations / …</td></tr>
<tr><td><b>Barre du haut</b></td><td>De gauche à droite : titre de la page, barre de recherche globale, bouton mode sombre 🌙, notifications 🔔, aide ❓, bouton + Ajouter (selon la page).</td></tr>
<tr><td><b>Zone centrale</b></td><td>Le contenu de la page : liste, formulaire, tableau de bord, statistiques…</td></tr>
</table>

<h3>1.3 L'écran principal — menu, sous-menus, barre du haut</h3>
<p>L'application compte <b>22 rubriques</b> dans le menu, organisées en blocs logiques :</p>

<table>
<tr><th>Bloc</th><th>Rubriques</th></tr>
<tr><td>Synthèse</td><td>Vue d'ensemble (tableau de bord)</td></tr>
<tr><td>Calendrier</td><td>Multiple, Mensuel, Annuel</td></tr>
<tr><td>Communication</td><td>Boîte de réception (conversations, IA, modèles, automatisations)</td></tr>
<tr><td>Opérations</td><td>Réservations, Annonces (biens), Tâches</td></tr>
<tr><td>Satisfaction</td><td>Avis, Qualité d'hébergement</td></tr>
<tr><td>Finance</td><td>Rapports financiers, Dépenses & suppléments, Paiements voyageurs, Relevés propriétaire</td></tr>
<tr><td>Pricing</td><td>Tarification</td></tr>
<tr><td>Distribution</td><td>Gestionnaire de canaux</td></tr>
<tr><td>Conciergerie</td><td>Partenaires, Propriétaires, Voyageurs, Conciergerie (prestations, commandes, fiches)</td></tr>
<tr><td>Technique</td><td>Branchements & outils, Utilisateurs & groupes, Moteur de réservation, Paramètres</td></tr>
</table>

<h3>1.4 Raccourcis clavier</h3>
<table>
<tr><th style="width:25%">Raccourci</th><th>Action</th></tr>
<tr><td><span class="kbd">Alt + 1</span> à <span class="kbd">Alt + 9</span></td><td>Accès direct aux 9 premières rubriques du menu</td></tr>
<tr><td><span class="kbd">Alt + D</span></td><td>Revenir au Tableau de bord</td></tr>
<tr><td><span class="kbd">Alt + T</span></td><td>Basculer le mode sombre</td></tr>
<tr><td><span class="kbd">Alt + P</span></td><td>Imprimer la page courante</td></tr>
<tr><td><span class="kbd">Échap</span></td><td>Fermer le formulaire / la modale en cours</td></tr>
</table>

<h3>1.5 Mode sombre et impression</h3>
<p>Le <b>mode sombre</b> s'active avec le bouton 🌙 en haut à droite (ou Alt+T). Tous les éléments s'adaptent automatiquement.</p>
<p>L'<b>impression</b> (Alt+P ou Ctrl+P) masque le menu et la barre du haut pour un rendu propre du contenu affiché.</p>
</div>
"""

# ============= CHAPITRE 2 — TABLEAU DE BORD =============
body += """
<div class="section">
<h2>2. Vue d'ensemble — Tableau de bord</h2>
<p>Le tableau de bord est la page d'accueil de l'application. Il synthétise l'activité du mois en cours.</p>

<h3>2.1 KPI et indicateurs</h3>
<table>
<tr><th style="width:35%">Indicateur</th><th>Ce qu'il mesure</th><th>Comment il est calculé</th></tr>
<tr><td><b>Commissions DPM (partenaires)</b></td><td>Ce que DPM gagne sur les prestations partenaires</td><td>(Prix facturé − Net partenaire) × Quantité, sur les commandes confirmées du mois</td></tr>
<tr><td><b>À reverser aux partenaires</b></td><td>Ce que DPM doit reverser</td><td>Net partenaire × Quantité, sur les commandes confirmées du mois</td></tr>
<tr><td><b>CA services internes</b></td><td>Chiffre d'affaires des prestations internes (propriétaires)</td><td>Prix × Quantité des commandes de type « interne » confirmées du mois</td></tr>
<tr><td><b>Occupation du parc</b></td><td>Taux d'occupation global</td><td>Nuits réservées / Nuits disponibles × 100, sur le mois</td></tr>
<tr><td><b>Réservations confirmées</b></td><td>Nombre de séjours confirmés du mois</td><td>Réservations avec statut « confirmée » dont l'arrivée ou le départ est dans le mois</td></tr>
</table>

<h3>2.2 Demandes à traiter (commandes en attente)</h3>
<p>Sous les KPI, le tableau de bord liste les <b>commandes de prestations en attente</b> de confirmation. Pour chaque demande :</p>
<table>
<tr><th>Colonne</th><th>Contenu</th></tr>
<tr><td>Prestation</td><td>Icône + nom de la prestation. Si le voyageur a ajouté un commentaire, il apparaît en dessous.</td></tr>
<tr><td>Bien · Voyageur</td><td>Nom du bien et du voyageur</td></tr>
<tr><td>Date</td><td>Date et heure de la prestation demandée</td></tr>
<tr><td>Qté</td><td>Nombre de personnes / unités</td></tr>
<tr><td>Montant</td><td>Prix total facturé</td></tr>
<tr><td>Type</td><td>Partenaire ou Interne</td></tr>
</table>
<p><b>Actions :</b></p>
""" + step(1, "<b>Confirmer</b> — Valide la commande. Le partenaire est notifié, le montant est comptabilisé.") + """
""" + step(2, "<b>Refuser</b> — Refuse la commande. Le voyageur est informé.") + """

<div class="note">💡 Ces mêmes demandes apparaissent dans <b>Conciergerie → Demandes de prestations</b> où vous pouvez aussi filtrer par statut et par date.</div>
</div>
"""

# ============= CHAPITRE 5 — RÉSERVATIONS =============
body += """
<div class="section">
<h2>3–4. Calendrier et Boîte de réception</h2>
<h3>3. Calendrier</h3>
<p><b>Vue multiple :</b> tous les biens sur une frise temporelle horizontale. Chaque réservation est une barre colorée (vert = confirmée, jaune = en attente, rouge = annulée). Glissez horizontalement pour naviguer dans le temps.</p>
<p><b>Vue mensuelle :</b> calendrier classique avec les réservations positionnées sur les jours. Cliquez sur une réservation pour ouvrir sa fiche complète.</p>
<p><b>Vue annuelle :</b> grille 12 mois × nombre de biens, avec le taux d'occupation en couleur (vert foncé = haute occupation, rouge = basse). Idéal pour repérer les périodes creuses.</p>

<h3>4. Boîte de réception</h3>
<h4>Conversations</h4>
<p>Tous les échanges centralisés. Les messages des plateformes (Airbnb, Booking, WhatsApp) arrivent ici avec la photo et le nom du voyageur, rattachés à la réservation.</p>

<h4>Réponses IA</h4>
<p>L'assistant IA rédige des réponses suggérées basées sur votre <b>Base de connaissances</b>. Ajoutez-y toutes les informations pratiques : adresse exacte, wifi, code porte, horaires de check-in, recommandations restaurants, règlement intérieur. Chaque fait peut être rattaché à un bien précis ou être général (tous les biens).</p>

<h4>Messages automatisés</h4>
<p>Programmez des messages déclenchés automatiquement :</p>
<table>
<tr><th>Déclencheur</th><th>Exemple</th></tr>
<tr><td>X jours avant l'arrivée</td><td>5 jours avant → instructions de check-in avec code porte et wifi</td></tr>
<tr><td>Jour de l'arrivée</td><td>Message de bienvenue avec lien vers l'espace voyageur</td></tr>
<tr><td>Pendant le séjour (J+2)</td><td>Proposition de prestations : massage, excursion, chef privé</td></tr>
<tr><td>Après le départ (J+1)</td><td>Remerciement et demande d'avis</td></tr>
</table>
<div class="warn">⚠️ <b>Sécurité :</b> Les messages automatisés créent toujours des <b>brouillons</b> à valider avant envoi. Aucun message n'est jamais envoyé automatiquement sans votre validation.</div>
</div>
"""

# ============= CHAPITRE 5 — RÉSERVATIONS DÉTAILLÉ =============
body += """
<div class="section">
<h2>5. Réservations</h2>

<h3>5.1 Créer une réservation manuelle — procédure complète</h3>
<p>Pour une réservation en direct (pas de plateforme) :</p>
""" + step(1, "Allez dans <b>Réservations → Liste</b>") + """
""" + step(2, "Cliquez <b>+ Nouvelle réservation</b> en haut à droite") + """
""" + step(3, "Remplissez le formulaire :") + """

<table>
<tr><th style="width:25%">Champ</th><th>Description</th><th style="width:25%">Obligatoire ?</th></tr>
<tr><td><b>Bien</b></td><td>Sélectionnez le bien dans la liste déroulante</td><td>✅ Oui</td></tr>
<tr><td><b>Voyageur</b></td><td>Sélectionnez un voyageur existant ou créez-en un nouveau</td><td>Recommandé</td></tr>
<tr><td><b>Arrivée</b></td><td>Date d'arrivée du voyageur</td><td>✅ Oui</td></tr>
<tr><td><b>Départ</b></td><td>Date de départ du voyageur</td><td>✅ Oui</td></tr>
<tr><td><b>Personnes</b></td><td>Nombre de voyageurs</td><td>Non</td></tr>
<tr><td><b>Canal</b></td><td>direct, airbnb, booking, vrbo, expedia, abritel, autre</td><td>Défaut : direct</td></tr>
<tr><td><b>Unité / chambre</b></td><td>Pour les biens multi-unités uniquement</td><td>Non</td></tr>
<tr><td><b>Réf. canal</b></td><td>Numéro de réservation de la plateforme</td><td>Non</td></tr>
<tr><td><b>Prix total</b></td><td>Montant total du séjour</td><td>Recommandé</td></tr>
<tr><td><b>Statut</b></td><td>demande, en_attente, confirmée, annulée, terminée, no_show, séjour propriétaire</td><td>Défaut : confirmée</td></tr>
<tr><td><b>Heure d'arrivée / départ</b></td><td>Heures prévues</td><td>Non</td></tr>
<tr><td><b>Contrat signé</b></td><td>Téléchargez le contrat signé (PDF, image)</td><td>Non</td></tr>
<tr><td><b>Notes</b></td><td>Informations internes (non visibles du voyageur)</td><td>Non</td></tr>
</table>

""" + step(4, "Cliquez <b>Enregistrer</b>. La réservation apparaît dans la liste et dans le calendrier.") + """

<h3>5.2 Accepter ou refuser une demande</h3>
<p>Les réservations importées depuis les plateformes arrivent en statut « demande » (inquiry Airbnb) ou « en_attente » (booking request).</p>
""" + step(1, "Dans la liste, repérez la réservation avec le statut jaune « demande » ou « en_attente »") + """
""" + step(2, "Cliquez <b>✅ Accepter</b> pour confirmer la réservation. Les dates sont bloquées dans le calendrier, la plateforme est synchronisée.") + """
""" + step(3, "Ou cliquez <b>❌ Refuser</b> pour rejeter la demande. La plateforme est notifiée.") + """

<div class="important">✅ <b>Conseil :</b> Répondez rapidement aux demandes Airbnb (< 24h) pour maintenir votre taux de réponse et votre classement.</div>

<h3>5.3 Fiche de réservation</h3>
<p>Cliquez sur le bouton <b>👁</b> d'une réservation pour ouvrir sa fiche complète. Vous y trouvez :</p>
<ul>
<li>Les informations du séjour (dates, nombre de nuits, prix/nuit calculé)</li>
<li>Le voyageur (nom, email, téléphone, avec lien vers sa fiche voyageur)</li>
<li>Le bien (nom, propriétaire)</li>
<li>Le statut du paiement</li>
<li>Les commandes de prestations rattachées à ce séjour</li>
<li>L'historique des messages échangés</li>
</ul>

<h3>5.4 Contrat PDF automatique</h3>
<p>Cliquez sur le bouton <b>📄</b> d'une réservation. L'application génère automatiquement un contrat de location au format PDF avec :</p>
<ul>
<li>En-tête aux couleurs DPM</li>
<li>Identification des parties (propriétaire + voyageur)</li>
<li>Description du bien</li>
<li>Dates et durée du séjour</li>
<li>Montant total, prix/nuit, conditions de paiement</li>
<li>Conditions d'annulation</li>
<li>Zone de signature</li>
</ul>

<h3>5.5 Check-in en ligne</h3>
<p>Le voyageur remplit un formulaire avant son arrivée (via un lien envoyé automatiquement) :</p>
<ul>
<li>Pièce d'identité (photo + numéro)</li>
<li>Heure d'arrivée prévue</li>
<li>Nombre exact de personnes</li>
<li>Selfie (si activé)</li>
</ul>
<p>Allez dans <b>Réservations → Check-in en ligne</b> pour voir l'état de chaque check-in (en attente, complété, vérifié) et télécharger les documents.</p>

<h3>5.6 Coupons de réduction</h3>
<p>Créez des codes promo dans <b>Réservations → Coupons</b> :</p>
<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td>Code</td><td>Le code que saisit le voyageur</td><td>BIENVENUE10</td></tr>
<tr><td>Type</td><td>Montant fixe ou pourcentage</td><td>pourcentage</td></tr>
<tr><td>Valeur</td><td>Le montant de la réduction</td><td>10 (= 10%)</td></tr>
<tr><td>Séjour min</td><td>Nombre minimum de nuits pour utiliser le coupon</td><td>3 nuits</td></tr>
<tr><td>Validité</td><td>Dates de début et fin de validité</td><td>01/12/2026 → 31/01/2027</td></tr>
<tr><td>Utilisations max</td><td>Nombre de fois que le code peut être utilisé</td><td>50</td></tr>
</table>

<h3>5.7 Filtres de la liste</h3>
<p>La liste des réservations offre des filtres avancés :</p>
<ul>
<li><b>Par date :</b> arrivée ou départ dans une fourchette (du … au …)</li>
<li><b>Par canal :</b> direct, airbnb, booking, vrbo, etc.</li>
<li><b>Recherche textuelle :</b> nom du voyageur, nom du bien, référence</li>
<li><b>Export CSV :</b> téléchargez la liste filtrée au format tableur</li>
</ul>
</div>
"""

# ============= CHAPITRE 6 — BIENS =============
body += """
<div class="section">
<h2>6. Annonces (Biens) — Fiche détaillée</h2>
<p>Chaque bien (villa, riad, appartement…) dispose d'une fiche complète organisée en <b>9 sections</b>.</p>

<h3>6.1 Créer un bien</h3>
""" + step(1, "Allez dans <b>Annonces → Liste</b>") + """
""" + step(2, "Cliquez <b>+ Ajouter un bien</b>") + """
""" + step(3, "Remplissez les 9 sections du formulaire (détaillées ci-dessous)") + """
""" + step(4, "Cliquez <b>Enregistrer</b>") + """

<h3>6.2 Section 1 — Informations générales</h3>
<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td><b>Nom de l'annonce</b> ✱</td><td>Nom affiché partout dans l'application</td><td>Riad Jasmin — Médina</td></tr>
<tr><td>Type de bien</td><td>Appartement, Villa, Riad, Studio, Maison, Chambre</td><td>Riad</td></tr>
<tr><td>Propriétaire</td><td>Rattachement au propriétaire qui gère ce bien</td><td>Propriétaire Démo</td></tr>
<tr><td>Commission prestations (%)</td><td>Commission DPM sur les services vendus par le propriétaire via la conciergerie</td><td>20%</td></tr>
<tr><td>Statut</td><td>en_ligne (visible), masqué (caché), brouillon</td><td>en_ligne</td></tr>
<tr><td>État de propreté</td><td>propre, en_nettoyage, a_nettoyer (mis à jour par l'équipe ménage)</td><td>propre</td></tr>
<tr><td>Type d'unité</td><td>simple (bien unique), parent (riad avec chambres), enfant (une chambre)</td><td>simple</td></tr>
</table>

<h3>6.3 Section 2 — Description & contenu</h3>
<p>Les descriptions sont synchronisées avec les plateformes. Les champs marqués 🏷 sont spécifiques à une plateforme.</p>
<table>
<tr><th>Champ</th><th>Envoyé à</th></tr>
<tr><td>Description principale</td><td>Toutes les plateformes</td></tr>
<tr><td>Résumé court</td><td>Booking, VRBO (description courte)</td></tr>
<tr><td>L'espace 🏷 Airbnb</td><td>Airbnb uniquement (champ "The Space")</td></tr>
<tr><td>Le quartier 🏷 Airbnb</td><td>Airbnb uniquement (champ "Neighborhood")</td></tr>
<tr><td>Transports 🏷 Airbnb</td><td>Airbnb uniquement (champ "Transit")</td></tr>
</table>

<h3>6.4 Sections 3 à 5 — Localisation, Capacité, Tarifs</h3>
<div class="cols2">
<div>
<h4>Localisation</h4>
<p>Adresse, ville, pays, code postal, coordonnées GPS (latitude/longitude). Les coordonnées GPS sont envoyées aux plateformes pour le positionnement sur la carte.</p>
</div>
<div>
<h4>Capacité & surface</h4>
<p>Voyageurs max, chambres, lits, salles de bain, superficie en m². Ces informations sont affichées sur les plateformes et servent au filtrage.</p>
</div>
</div>

<h4>Tarifs & conditions financières</h4>
<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td>Prix de base / nuit</td><td>Tarif standard hors saison</td><td>1 200 DH</td></tr>
<tr><td>Devise</td><td>MAD, EUR ou USD</td><td>MAD</td></tr>
<tr><td>Nuits minimum / maximum</td><td>Contraintes de durée de séjour</td><td>Min 2, Max 30</td></tr>
<tr><td>Supplément week-end / nuit</td><td>Majoration appliquée le vendredi et samedi</td><td>200 DH</td></tr>
<tr><td>Prix personne supp. / nuit</td><td>Facturation supplémentaire au-delà de la capacité de base</td><td>150 DH</td></tr>
<tr><td>Frais de ménage</td><td>Forfait unique par séjour</td><td>500 DH</td></tr>
<tr><td>Taxe de séjour / nuit</td><td>Taxe locale par nuit</td><td>25 DH</td></tr>
<tr><td>Caution demandée</td><td>Montant de la caution (pré-autorisation ou dépôt)</td><td>3 000 DH</td></tr>
<tr><td>Remise hebdomadaire</td><td>Réduction en % pour les séjours ≥ 7 jours (seuil configurable)</td><td>10%</td></tr>
<tr><td>Remise mensuelle</td><td>Réduction en % pour les séjours ≥ 30 jours (seuil configurable)</td><td>20%</td></tr>
<tr><td>Politique d'annulation</td><td>flexible, modérée, stricte, non_remboursable (par canal si besoin)</td><td>modérée</td></tr>
</table>

<h4>Majorations par canal</h4>
<p>Augmentez automatiquement le prix affiché sur chaque plateforme pour absorber leurs commissions :</p>
<div class="example">
<b>Exemple :</b> Prix de base 1 000 DH/nuit.<br>
Majoration Airbnb 15% → le voyageur Airbnb voit 1 150 DH/nuit.<br>
Majoration Booking 18% → le voyageur Booking voit 1 180 DH/nuit.<br>
Site direct 0% → le voyageur en direct paie 1 000 DH/nuit (meilleur prix).<br>
<i>→ Vous recevez toujours environ 1 000 DH net quelle que soit la plateforme.</i>
</div>

<h3>6.5 Section 6 — Arrivée & accès</h3>
<table>
<tr><th>Champ</th><th>Description</th></tr>
<tr><td>Heure d'arrivée / départ</td><td>Heures standard (envoyées aux plateformes et à l'espace voyageur)</td></tr>
<tr><td>Méthode de check-in</td><td>boîte à clés, serrure connectée, concierge, en personne, instructions</td></tr>
<tr><td>Code de porte / boîte à clés</td><td>Affiché dans l'espace voyageur le jour de l'arrivée</td></tr>
<tr><td>Wifi — nom et mot de passe</td><td>Affichés dans l'espace voyageur dès l'arrivée</td></tr>
<tr><td>Instructions d'arrivée</td><td>Texte détaillé : comment trouver le bien, où se garer, qui contacter</td></tr>
<tr><td>Contact d'urgence</td><td>Numéro affiché dans l'espace voyageur</td></tr>
</table>

<h3>6.6 Chambres & lits, Équipements</h3>
<p><b>Chambres & lits :</b> ajoutez autant de lignes que de chambres. Pour chaque chambre : nom, type de lit (double, simple, king, queen, canapé-lit, superposé, bébé), quantité.</p>
<p><b>Équipements :</b> cochez parmi 30 équipements standards (Wifi, Climatisation, Piscine, Cuisine équipée, Parking, etc.). Ces informations sont envoyées aux plateformes.</p>

<h3>6.7 Fenêtre de réservation et conditions</h3>
<table>
<tr><th>Champ</th><th>Description</th></tr>
<tr><td>Délai minimum avant arrivée</td><td>Ex : 2 jours → impossible de réserver pour demain</td></tr>
<tr><td>Réservable jusqu'à X jours</td><td>Ex : 365 → réservable jusqu'à 1 an à l'avance</td></tr>
<tr><td>Jours de préparation</td><td>Nombre de jours bloqués entre deux séjours (ménage, remise en état)</td></tr>
<tr><td>Jours d'arrivée / départ autorisés</td><td>Restreindre les arrivées au samedi uniquement, par exemple</td></tr>
<tr><td>Règlement intérieur</td><td>Texte du règlement affiché au voyageur</td></tr>
<tr><td>Enfants, Fumeur, Animaux</td><td>Politiques spécifiques (envoyées à Booking)</td></tr>
</table>

<h3>6.8 Score ASO</h3>
<p>L'onglet <b>Score ASO</b> analyse la qualité de chaque annonce sur 100 points :</p>
<ul>
<li>Complétude des champs (description, photos, équipements)</li>
<li>Nombre et qualité des photos</li>
<li>Temps de réponse moyen aux messages</li>
<li>Taux d'acceptation des réservations</li>
<li>Note moyenne des avis</li>
</ul>
<div class="note">💡 Un score > 80 améliore votre classement sur les plateformes. Visez 90+ pour chaque bien.</div>
</div>
"""

# ============= CHAPITRE 15 — PRESTATIONS =============
body += """
<div class="section">
<h2>7. Tâches — Kanban, automatisation, checklists</h2>

<h3>7.1 Vue Kanban</h3>
<p>La rubrique <b>Tâches → Gérer les tâches</b> affiche un tableau Kanban en 3 colonnes : <b>À faire → En cours → Fait</b>. Glissez-déposez une tâche d'une colonne à l'autre pour changer son statut.</p>

<h3>7.2 Créer une tâche</h3>
""" + step(1, "Cliquez <b>+ Nouvelle tâche</b>") + """
""" + step(2, "Remplissez le formulaire :") + """
<table>
<tr><th style="width:28%">Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td><b>Titre</b> ✱</td><td>Description courte de la tâche</td><td>Ménage départ Riad Jasmin</td></tr>
<tr><td>Type</td><td>ménage, checkin, checkout, petit_déjeuner, transport, maintenance, inspection, autre</td><td>ménage</td></tr>
<tr><td>Bien</td><td>Le bien concerné</td><td>Riad Jasmin</td></tr>
<tr><td>Réservation</td><td>Réservation liée (optionnel)</td><td>Famille Dupont</td></tr>
<tr><td>Affecté à</td><td>L'intervenant responsable</td><td>Fatima (agent ménage)</td></tr>
<tr><td>Superviseur</td><td>La personne qui vérifie (optionnel)</td><td>Kenza</td></tr>
<tr><td>Commence le</td><td>Date prévue</td><td>15/12/2026</td></tr>
<tr><td>Heure</td><td>Heure de début</td><td>10:00</td></tr>
<tr><td>Doit se terminer avant</td><td>Date d'échéance</td><td>15/12/2026</td></tr>
<tr><td>Coût</td><td>Coût de la tâche (facturé au propriétaire)</td><td>350 DH</td></tr>
<tr><td>Statut</td><td>a_faire, accepté, en_cours, fait, annulée</td><td>a_faire</td></tr>
<tr><td>Description</td><td>Détails, liste de ce qu'il faut faire</td><td>Ménage complet + changement draps</td></tr>
</table>

<h3>7.3 Tâches automatiques</h3>
<p>Créez des règles qui génèrent automatiquement des tâches à chaque événement :</p>
<table>
<tr><th style="width:28%">Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td><b>Nom</b> ✱</td><td>Nom de la tâche qui sera créée</td><td>Ménage de départ</td></tr>
<tr><td>Catégorie</td><td>Type de tâche (ménage, transport…)</td><td>ménage</td></tr>
<tr><td><b>Événement déclencheur</b></td><td>Arrivée ou départ du voyageur</td><td>départ</td></tr>
<tr><td><b>Décalage (heures)</b></td><td>0 = à l'heure de l'événement, -2 = 2h avant, +2 = 2h après</td><td>0 (au moment du départ)</td></tr>
<tr><td>Échéance</td><td>même_jour ou prochaine_arrivée</td><td>prochaine_arrivée</td></tr>
<tr><td>Canal</td><td>Déclencher seulement pour ce canal (vide = tous)</td><td>vide (tous)</td></tr>
<tr><td>Bien</td><td>Déclencher seulement pour ce bien (vide = tous)</td><td>vide (tous)</td></tr>
<tr><td>Condition</td><td>Condition supplémentaire : paiement complet, séjour min 3 nuits, canal direct…</td><td>vide</td></tr>
<tr><td>Affecté à</td><td>L'intervenant qui recevra la tâche</td><td>Fatima</td></tr>
</table>

<div class="example">
<b>Exemple concret :</b> Créer une tâche automatique « Ménage de départ »<br>
• Événement : <b>départ</b>, Décalage : <b>0h</b>, Échéance : <b>prochaine_arrivée</b><br>
• Affecté à : Fatima, Coût : 350 DH, Type : ménage<br>
→ À chaque départ de voyageur, une tâche « Ménage de départ » est créée automatiquement pour Fatima, avec comme deadline la prochaine arrivée sur le même bien.
</div>

<h3>7.4 Modèles de checklist</h3>
<p>Préparez des listes de vérification réutilisables : checklist ménage (20 points à vérifier), checklist accueil (10 points), checklist départ (8 points). Chaque checklist peut être rattachée à une tâche.</p>
<p>L'<b>Agenda</b> montre toutes les tâches sur un calendrier. Les <b>Tâches archivées</b> conservent l'historique.</p>
</div>
"""

# ============= CHAPITRE 8 — AVIS =============
body += """
<div class="section">
<h2>8. Avis — Gestion et automatisation</h2>

<h3>8.1 Gérer les avis</h3>
<p>Tous les avis reçus des voyageurs, avec filtres par bien, canal et note.</p>
<table>
<tr><th style="width:28%">Champ</th><th>Description</th></tr>
<tr><td>Réservation / Bien / Voyageur</td><td>Rattachement à la réservation concernée</td></tr>
<tr><td>Canal + Origine</td><td>D'où vient l'avis (Airbnb, Booking, Google, TripAdvisor…)</td></tr>
<tr><td>Note globale /5</td><td>Note principale</td></tr>
<tr><td>Notes détaillées</td><td>Propreté, Communication, Emplacement, Qualité-prix (chacune sur 5)</td></tr>
<tr><td>Commentaire</td><td>Texte du voyageur</td></tr>
<tr><td>Réponse de l'hôte</td><td>Votre réponse publique</td></tr>
<tr><td>Étiquettes</td><td>Tags libres pour catégoriser (ex : « piscine », « petit-déjeuner »)</td></tr>
<tr><td>Afficher sur le site</td><td>Publier dans le moteur de réservation direct</td></tr>
<tr><td>Statut</td><td>publié, en_attente, masqué, programmé</td></tr>
</table>

<h3>8.2 Avis automatiques</h3>
<p>Programmez l'envoi automatique d'une demande d'avis après le séjour :</p>
<div class="example">
<b>Exemple :</b> Règle « Demande d'avis J+3 »<br>
• Événement : <b>départ</b>, Délai : <b>3 jours</b><br>
• Bien : vide (tous les biens), Canal : vide (tous les canaux)<br>
→ 3 jours après chaque départ, un message est préparé (brouillon) demandant au voyageur de laisser un avis.
</div>

<h3>8.3 Modèles d'avis</h3>
<p>Réponses types pré-rédigées pour gagner du temps : réponse à un avis positif, réponse à un avis négatif, réponse neutre. Chaque modèle inclut le texte de réponse et les notes à attribuer.</p>

<h3>8.4 Analyses IA (Qualité des avis)</h3>
<p>Synthèse automatique des avis par bien : points forts récurrents, points faibles, tendances sur les 3 derniers mois. Utile pour prioriser les améliorations.</p>
</div>
"""

# ============= CHAPITRE 9 — RAPPORTS FINANCIERS =============
body += """
<div class="section">
<h2>9. Rapports financiers</h2>

<h3>9.1 Analytique</h3>
<p>Tableau de bord financier avec graphiques. Filtrable par bien, par période et par canal :</p>
<ul>
<li><b>Revenus par mois</b> : barres empilées par canal (Airbnb, Booking, direct…)</li>
<li><b>Revenus par bien</b> : classement des biens par chiffre d'affaires</li>
<li><b>Comparaison N/N-1</b> : évolution par rapport à la même période l'année précédente</li>
<li><b>Prix moyen par nuit</b> : calculé sur les réservations confirmées</li>
</ul>

<h3>9.2 Activité de location</h3>
<p>Détail ligne par ligne de chaque nuit louée : bien, voyageur, montant, canal, commission plateforme. Export CSV pour votre comptable.</p>

<h3>9.3 Taux d'occupation</h3>
<p>Par bien et par période : pourcentage de nuits louées vs nuits disponibles. Visualisation calendaire (couleur par jour). Utile pour ajuster les tarifs des périodes creuses.</p>

<h3>9.4 Formules</h3>
<p>Personnalisez les calculs financiers utilisés dans les rapports et relevés :</p>
<ul>
<li>Formule de commission plateforme (% déduit du revenu brut)</li>
<li>Formule de ménage (forfait ou variable selon la durée)</li>
<li>Formule de reversement propriétaire (% après déduction des charges)</li>
</ul>

<h3>9.5 Taxes et Paramètres financiers</h3>
<p><b>Taxes :</b> configurez la taxe de séjour par bien (montant par nuit par personne). <b>Paramètres financiers :</b> devise, format de montant, règles d'arrondi.</p>

<h3>9.6 Export comptable</h3>
<p>Exportez toutes les écritures financières (revenus, dépenses, commissions) au format CSV, prêt à importer dans votre logiciel comptable. Filtrable par période.</p>

<h3>9.7 Prévisionnel</h3>
<p>Projection des revenus futurs basée sur :</p>
<ul>
<li>Les réservations déjà confirmées (revenus garantis)</li>
<li>Le taux d'occupation historique (estimation des revenus probables)</li>
<li>Les tarifs saisonniers paramétrés</li>
</ul>

<h3>9.8 Rapport mensuel</h3>
<p>Génération d'un rapport mensuel complet, prêt à envoyer au propriétaire : revenus bruts, dépenses, commissions, occupation, prestations vendues, net à reverser. Format PDF.</p>
</div>
"""

# ============= CHAPITRE 10 — DÉPENSES =============
body += """
<div class="section">
<h2>10. Dépenses & suppléments</h2>

<h3>10.1 Créer une dépense</h3>
""" + step(1, "Allez dans <b>Dépenses & suppléments → Dépenses</b> (ou Suppléments)") + """
""" + step(2, "Cliquez <b>+ Ajouter</b>") + """
""" + step(3, "Remplissez :") + """
<table>
<tr><th style="width:28%">Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td><b>Type</b></td><td><b>Dépense</b> = charge (ménage, réparation…) / <b>Supplément</b> = refacturé au voyageur (ménage de départ, linge extra…)</td><td>dépense</td></tr>
<tr><td><b>Date</b> ✱</td><td>Date de la dépense</td><td>15/12/2026</td></tr>
<tr><td><b>Libellé</b> ✱</td><td>Description</td><td>Remplacement robinet sdb</td></tr>
<tr><td>Catégorie</td><td>Ménage, Maintenance, Réparation, Fournitures, Linge, Loyer, Taxe foncière, Commission, Utilities, Autre</td><td>Réparation</td></tr>
<tr><td>Bien</td><td>Bien concerné</td><td>Riad Jasmin</td></tr>
<tr><td>Propriétaire</td><td>Propriétaire concerné</td><td>(auto via le bien)</td></tr>
<tr><td>Réservation</td><td>Réservation liée (optionnel)</td><td>vide</td></tr>
<tr><td><b>Montant</b> ✱</td><td>Montant en DH</td><td>450 DH</td></tr>
<tr><td>Pièce jointe</td><td>Photo de la facture / du ticket</td><td>facture.pdf</td></tr>
<tr><td>Masquer dans les relevés</td><td>Ne pas inclure dans le relevé propriétaire</td><td>Non</td></tr>
</table>

<h3>10.2 Catégories personnalisées</h3>
<p>Créez vos propres catégories dans <b>Catégories</b> pour organiser les dépenses selon votre plan comptable.</p>

<h3>10.3 Automatisations de dépenses</h3>
<p>Pour les dépenses récurrentes (loyer mensuel, abonnement internet, assurance…) :</p>
<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td>Nom</td><td>Libellé de la dépense créée</td><td>Abonnement internet</td></tr>
<tr><td>Nature</td><td>Dépense ou supplément</td><td>dépense</td></tr>
<tr><td>Répétition</td><td>Mensuel, hebdomadaire, annuel</td><td>mensuel</td></tr>
<tr><td>Jour du mois</td><td>Jour de création automatique</td><td>1er</td></tr>
<tr><td>Bien</td><td>Bien concerné (vide = tous)</td><td>Riad Jasmin</td></tr>
<tr><td>Montant</td><td>Montant récurrent</td><td>500 DH</td></tr>
</table>
<div class="note">💡 Bouton <b>Exécuter maintenant</b> : crée immédiatement la dépense sans attendre la prochaine échéance.</div>
</div>
"""

# ============= CHAPITRE 11 — PAIEMENTS =============
body += """
<div class="section">
<h2>11. Paiements voyageurs</h2>

<h3>11.1 Encaissements</h3>
<p>Suivi de tous les paiements reçus. Chaque encaissement est lié à une réservation et indique le montant, la date, le mode de paiement (plateforme, virement, espèces, CMI, PayPal) et le statut (payé, en attente, échoué).</p>

<h3>11.2 Factures voyageurs</h3>
<p>Générez des factures officielles :</p>
<table>
<tr><th>Champ</th><th>Description</th></tr>
<tr><td><b>Numéro</b> ✱</td><td>Numéro de facture (numérotation manuelle ou auto)</td></tr>
<tr><td>Réservation / Voyageur / Bien</td><td>Rattachement</td></tr>
<tr><td><b>Date de facture</b> ✱</td><td>Date d'émission</td></tr>
<tr><td>Date d'échéance</td><td>Date limite de paiement</td></tr>
<tr><td><b>Montant HT</b> ✱</td><td>Montant hors taxes</td></tr>
<tr><td>TVA %</td><td>Taux de TVA applicable (défaut 10%)</td></tr>
<tr><td>Montant TVA / TTC</td><td>Calculés automatiquement</td></tr>
<tr><td>Statut</td><td>brouillon, émise, payée, annulée</td></tr>
<tr><td>Notes / lignes</td><td>Détail des lignes de facturation</td></tr>
</table>

<h3>11.3 Dépôts de garantie</h3>
<p>Cycle de vie d'une caution :</p>
<div class="example">
<b>Pré-autorisation :</b> en_attente → capturé (si dégâts) → libéré (si RAS)<br>
<b>Dépôt classique :</b> en_attente → capturé (encaissé) → remboursé (après le départ)
</div>
<table>
<tr><th>Champ</th><th>Description</th></tr>
<tr><td>Type</td><td>Pré-autorisation (bloqué sur la CB) ou dépôt classique (encaissé)</td></tr>
<tr><td>Montant</td><td>Montant de la caution</td></tr>
<tr><td>Statut</td><td>en_attente → capturé → libéré / remboursé / annulé</td></tr>
</table>

<h3>11.4 Paramètres PayPal et CMI</h3>
<p>Configurez vos modes de paiement en ligne dans <b>Paramètres PayPal</b> (clé API, mode sandbox/production) et <b>Paramètres → Paiement CMI</b> (pour les paiements par carte au Maroc).</p>
</div>
"""

# ============= CHAPITRE 12 — RELEVÉS PROPRIÉTAIRE =============
body += """
<div class="section">
<h2>12. Relevés propriétaire</h2>

<h3>12.1 Générer un relevé mensuel</h3>
<p>Un relevé récapitule ce qui revient à un propriétaire pour un mois donné :</p>
<div class="example">
<b>Exemple — Relevé de novembre 2026 pour « Propriétaire Démo » :</b><br>
• Revenus bruts des réservations : 24 000 DH<br>
• − Commission DPM (20%) : −4 800 DH<br>
• − Dépenses (ménage × 3, réparation plomberie) : −1 550 DH<br>
• + Prestations internes vendues (petit-déjeuner × 12) : +1 800 DH<br>
• − Commission DPM sur prestations internes (20%) : −360 DH<br>
• <b>= Net à reverser : 19 090 DH</b>
</div>

<h3>12.2 Relevés automatiques</h3>
<p>Programmez la génération automatique chaque mois :</p>
<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td>Nom</td><td>Nom du relevé</td><td>Relevé mensuel tous propriétaires</td></tr>
<tr><td>Propriétaire</td><td>Vide = tous les propriétaires</td><td>vide</td></tr>
<tr><td>Jour du mois</td><td>Jour de génération (1-28)</td><td>5 (le 5 de chaque mois)</td></tr>
<tr><td>Message</td><td>Texte d'accompagnement</td><td>Bonjour, veuillez trouver ci-joint…</td></tr>
</table>

<h3>12.3 Tableau de bord propriétaire</h3>
<p>Vision consolidée : revenus par bien, par mois, comparaison avec les mois précédents. Accessible aussi depuis l'espace propriétaire.</p>
</div>
"""

# ============= CHAPITRE 13 — TARIFICATION =============
body += """
<div class="section">
<h2>13. Tarification</h2>

<h3>13.1 Tarifs saisonniers</h3>
<p>Définissez des périodes avec un prix/nuit différent du tarif de base :</p>
<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td>Bien ✱</td><td>Le bien concerné</td><td>Riad Jasmin</td></tr>
<tr><td>Nom</td><td>Nom de la saison</td><td>Haute saison été</td></tr>
<tr><td>Début / Fin ✱</td><td>Dates de la période</td><td>01/07 → 31/08</td></tr>
<tr><td>Prix / nuit ✱</td><td>Prix pendant cette période</td><td>2 500 DH</td></tr>
<tr><td>Nuits minimum</td><td>Minimum de nuits pour cette période</td><td>5</td></tr>
<tr><td>Priorité</td><td>En cas de chevauchement, le tarif de priorité la plus élevée gagne</td><td>10</td></tr>
</table>
<div class="example">
<b>Exemple de chevauchement :</b><br>
Période 1 : « Été » (01/07–31/08) → 2 500 DH, priorité 5<br>
Période 2 : « Semaine du Festival » (10/07–17/07) → 3 500 DH, priorité 10<br>
→ Du 10 au 17 juillet, le prix sera 3 500 DH (priorité 10 > 5). Le reste de l'été, 2 500 DH.
</div>

<h3>13.2 Calendrier tarifaire</h3>
<p>Vision jour par jour du prix effectif de chaque bien, en combinant le tarif de base, les tarifs saisonniers et les majorations par canal.</p>

<h3>13.3 Extras & frais</h3>
<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td>Nom ✱</td><td>Nom de l'extra</td><td>Taxe de séjour</td></tr>
<tr><td>Bien</td><td>Bien concerné (vide = tous)</td><td>vide</td></tr>
<tr><td>Mode de facturation</td><td>par_séjour, par_nuit, par_personne, par_personne_nuit</td><td>par_nuit</td></tr>
<tr><td>Prix ✱</td><td>Montant</td><td>25 DH</td></tr>
<tr><td>Obligatoire</td><td>Oui = ajouté d'office, Non = optionnel pour le voyageur</td><td>Oui</td></tr>
</table>
<div class="example">
<b>Exemple :</b> Taxe de séjour 25 DH/nuit/personne, obligatoire<br>
Séjour de 5 nuits, 2 personnes → 25 × 5 × 2 = <b>250 DH</b> ajoutés au total
</div>

<h3>13.4 Tarification dynamique</h3>
<p>Ajustement automatique des prix en fonction de la demande et des prix concurrents. Intégration possible avec PriceLabs ou Beyond Pricing. Configuration dans cette rubrique.</p>

<h3>13.5 Minimum de nuits</h3>
<p>Paramétrez le nombre minimum de nuits par bien et par période. Ex : 2 nuits en basse saison, 5 nuits en haute saison, 7 nuits pendant les fêtes.</p>
</div>
"""

# ============= CHAPITRE 14 — CANAUX =============
body += """
<div class="section">
<h2>14. Gestionnaire de canaux</h2>

<h3>14.1 Canaux connectés</h3>
<p>Chaque bien peut être connecté à une ou plusieurs plateformes :</p>
<table>
<tr><th>Canal</th><th>Synchronisation</th></tr>
<tr><td>Airbnb</td><td>Calendrier, tarifs, réservations, messages</td></tr>
<tr><td>Booking.com</td><td>Calendrier, tarifs, réservations</td></tr>
<tr><td>VRBO / Abritel</td><td>Calendrier, tarifs, réservations</td></tr>
<tr><td>Expedia</td><td>Calendrier, réservations</td></tr>
<tr><td>Direct</td><td>Réservations manuelles ou via moteur de réservation</td></tr>
</table>
""" + step(1, "Allez dans <b>Gestionnaire de canaux → Canaux connectés</b>") + """
""" + step(2, "Cliquez <b>+ Connecter un canal</b>") + """
""" + step(3, "Sélectionnez le <b>bien</b> et le <b>canal</b>") + """
""" + step(4, "Collez l'<b>URL iCal d'import</b> (fournie par la plateforme)") + """
""" + step(5, "Enregistrez. La synchronisation démarre automatiquement.") + """

<h3>14.2 Synchronisation iCal</h3>
<p>L'iCal est un format standard de calendrier. Chaque plateforme fournit une URL d'export (calendrier de la plateforme) et accepte une URL d'import (votre calendrier).</p>
<ul>
<li><b>Import</b> : collez l'URL iCal de la plateforme dans le champ « URL iCal (import) ». My Hostaway récupère les réservations de cette plateforme.</li>
<li><b>Export</b> : My Hostaway génère une URL iCal pour chaque bien. Collez-la dans la plateforme pour synchroniser les disponibilités.</li>
</ul>
<div class="warn">⚠️ La synchronisation iCal a un délai de 15-30 minutes. Pour une synchronisation en temps réel, utilisez les API directes (Airbnb, Booking).</div>

<h3>14.3 Plans tarifaires Booking</h3>
<p>Configuration des plans tarifaires spécifiques à Booking.com : non remboursable (prix réduit), flexible (prix standard), petit-déjeuner inclus.</p>

<h3>14.4 Carte des annonces</h3>
<p>Carte géographique montrant tous vos biens et leurs connexions aux plateformes.</p>
</div>
"""

# ============= CHAPITRE 15 — PRESTATIONS (déjà détaillé) =============
body += """
<div class="section">
<h2>15. Conciergerie — Prestations</h2>
<p>Les prestations sont le cœur de l'activité conciergerie DPM. Ce chapitre explique chaque aspect en détail.</p>

<h3>15.1 Les 3 types de prestations</h3>
<div class="cols2">
<div class="box">
  <h4>🤝 Type « Externe » (Partenaire)</h4>
  <p>Un prestataire externe fournit le service. DPM fait l'intermédiaire :</p>
  <ul>
  <li>DPM vend la prestation au voyageur au <b>prix facturé</b></li>
  <li>DPM reverse au partenaire le <b>net partenaire</b></li>
  <li>DPM conserve la <b>commission</b> (prix − net)</li>
  </ul>
  <p><b>Exemples :</b> massage, quad, transfert aéroport, guide privé, golf</p>
</div>
<div class="box">
  <h4>🏠 Type « Interne » (Propriétaire)</h4>
  <p>Le propriétaire fournit le service via son personnel (cuisinier, femme de ménage…). DPM prend une commission fixée par bien (champ « commission_prestation_pct » dans la fiche du bien, défaut 20%).</p>
  <p><b>Exemples :</b> petit-déjeuner, dîner privé, ménage supplémentaire, blanchisserie</p>
</div>
</div>
<div class="box">
  <h4>🏢 Type « DPM »</h4>
  <p>DPM source et fournit directement la prestation. Pas de reversement partenaire. Le <b>coût de revient</b> est suivi pour calculer la marge interne.</p>
  <p><b>Exemples :</b> service de conciergerie personnalisé, organisation d'événements, service DPM exclusif</p>
</div>

<h3>15.2 Créer une prestation — procédure complète</h3>
""" + step(1, "Allez dans <b>Conciergerie → Toutes les prestations</b>") + """
""" + step(2, "Cliquez <b>+ Ajouter une prestation</b>") + """
""" + step(3, "Remplissez les informations de base :") + """

<table>
<tr><th style="width:28%">Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td><b>Nom</b> ✱</td><td>Nom affiché au voyageur</td><td>Massage bien-être</td></tr>
<tr><td>Catégorie</td><td>Pour classer et filtrer</td><td>Bien-être</td></tr>
<tr><td><b>Type</b> ✱</td><td>Externe (partenaire), Interne (propriétaire), DPM</td><td>Externe</td></tr>
<tr><td>Partenaire ✱<sup>ext</sup></td><td>Obligatoire si type = externe. Sélectionnez le partenaire.</td><td>Prestataire bien-être</td></tr>
<tr><td>Propriétaire ✱<sup>int</sup></td><td>Obligatoire si type = interne. Sélectionnez le propriétaire.</td><td>Propriétaire Démo</td></tr>
<tr><td>Service interne</td><td>Pour les types internes : rattacher à un service (optionnel)</td><td>Spa du riad</td></tr>
<tr><td>Icône</td><td>Emoji affiché au voyageur dans le catalogue</td><td>💆</td></tr>
<tr><td>Unité</td><td>Ce que compte « 1 quantité »</td><td>par personne</td></tr>
<tr><td>Description</td><td>Texte descriptif pour le voyageur</td><td>Massage relaxant aux huiles essentielles…</td></tr>
</table>

""" + step(4, "Configurez les <b>lieux et tarifs</b> :") + """

<h4>Section « Au logement »</h4>
<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td>Proposée au logement</td><td>Le voyageur peut commander cette prestation à la villa/riad</td><td>true</td></tr>
<tr><td>Prix facturé au voyageur</td><td>Ce que paie le voyageur</td><td>600 DH</td></tr>
<tr><td>Prix public affiché</td><td>Prix barré sur le site (optionnel, pour montrer une réduction)</td><td>800 DH</td></tr>
<tr><td>Commission</td><td>Commission DPM sur cette prestation</td><td>15</td></tr>
<tr><td>Commission exprimée en</td><td>Pourcentage (%) ou montant fixe (DH)</td><td>pct</td></tr>
</table>

<h4>Section « À l'extérieur »</h4>
<p>Mêmes champs, pour les prestations réalisées en dehors du logement (hammam en ville, excursion…). Le prix peut être différent.</p>

""" + step(5, "Configurez le <b>reversement et les règles</b> :") + """

<table>
<tr><th>Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td>Net reversé au partenaire</td><td>Ce que touche le partenaire par unité</td><td>510 DH</td></tr>
<tr><td>Coût de revient</td><td>Pour les prestations DPM uniquement : coût interne</td><td>0</td></tr>
<tr><td>Validation</td><td>auto = confirmée immédiatement, manuelle = attente de validation admin</td><td>auto</td></tr>
<tr><td>Préavis (heures)</td><td>Délai minimum avant la prestation</td><td>24</td></tr>
</table>

<div class="important">✅ <b>Vérification automatique :</b> L'application vérifie la cohérence entre le prix facturé, la commission et le net partenaire. Si les chiffres ne collent pas, un message d'erreur détaillé vous indique la correction à apporter.</div>

<h3>15.3 Tarifs, commissions et net partenaire — avec exemples</h3>
<div class="example">
<b>Exemple 1 — Prestation externe avec commission en %</b><br>
Massage bien-être proposé au logement :<br>
• Prix facturé au voyageur : <b>600 DH</b><br>
• Commission DPM : <b>15 %</b><br>
• Calcul : 600 × 15% = 90 DH de commission<br>
• Net partenaire : 600 − 90 = <b>510 DH</b><br><br>
Le voyageur commande 2 massages :<br>
• Total facturé : 2 × 600 = 1 200 DH<br>
• Commission DPM : 2 × 90 = <b>180 DH</b><br>
• À reverser au partenaire : 2 × 510 = <b>1 020 DH</b>
</div>

<div class="example">
<b>Exemple 2 — Prestation interne (propriétaire)</b><br>
Petit-déjeuner livré à la villa :<br>
• Prix facturé au voyageur : <b>150 DH / personne</b><br>
• Commission DPM : fixée par le bien (ex : 20%)<br>
• Le propriétaire reçoit 80% du montant<br>
• DPM retient 20%<br><br>
4 personnes commandent le petit-déjeuner :<br>
• Total facturé : 4 × 150 = 600 DH<br>
• Part propriétaire : 600 × 80% = <b>480 DH</b><br>
• Commission DPM : 600 × 20% = <b>120 DH</b>
</div>

<div class="example">
<b>Exemple 3 — Prestation sans commission (net = prix)</b><br>
Transfert aéroport :<br>
• Prix facturé au voyageur : <b>250 DH / trajet</b><br>
• Commission DPM : <b>0</b><br>
• Net partenaire : <b>250 DH</b> (tout va au chauffeur)<br>
<i>→ DPM ne prend rien sur cette prestation, c'est un service rendu au voyageur pour fidéliser.</i>
</div>

<h3>15.4 Horaires : plages, départs fixes, créneaux</h3>
<p>Chaque prestation peut avoir des contraintes horaires. 3 modes :</p>

<table>
<tr><th style="width:25%">Mode</th><th>Description</th><th>Exemple</th></tr>
<tr><td><b>Toujours disponible</b></td><td>Aucune contrainte horaire</td><td>Blanchisserie, ménage supplémentaire</td></tr>
<tr><td><b>Plages d'ouverture</b></td><td>Par jour de la semaine : heure de début → heure de fin. Décochez un jour pour le fermer.</td><td>Massage : Lun-Sam 9h-19h, Dim fermé</td></tr>
<tr><td><b>Heures de départ fixes</b></td><td>Liste de créneaux horaires précis</td><td>Quad Agafay : départs 9:00, 14:00 uniquement</td></tr>
</table>

<h4>Mode « Plages d'ouverture » — le champ « Créneaux toutes les X min »</h4>
<p>Quand vous choisissez « Plages d'ouverture », un champ supplémentaire apparaît :</p>
<p><b>Créneaux proposés toutes les _____ minutes</b> (15, 30, 45, 60, 90, 120 min)</p>
<p>Ce champ divise la plage horaire en créneaux réguliers que le voyageur peut choisir.</p>

<div class="example">
<b>Exemple :</b> Massage 9h–19h, créneaux toutes les 30 min<br>
→ Le voyageur voit : 9:00, 9:30, 10:00, 10:30, …, 18:30<br>
Chaque créneau correspond à un slot de 30 minutes (durée du massage).
</div>

<h4>Raccourcis</h4>
<p>Deux boutons sous la grille horaires :</p>
<ul>
<li><b>24h/24, 7j/7</b> : coche tous les jours, met toutes les plages de 0h à 24h</li>
<li><b>Tous les jours 8h–20h</b> : coche tous les jours, met toutes les plages de 8h à 20h</li>
</ul>

<h3>15.5 Liste avec onglets et filtres</h3>
<p>La page <b>Conciergerie → Toutes les prestations</b> offre :</p>
<ul>
<li><b>4 onglets</b> : Toutes (20) | DPM (0) | Partenaires (16) | Internes (4) → avec compteur par type</li>
<li><b>Filtre par fournisseur</b> : menu déroulant « Tous les partenaires et propriétaires » avec le nombre de prestations par fournisseur (ex : « 🤝 Prestataire bien-être (3) »)</li>
<li><b>Recherche textuelle</b> : filtre en temps réel sur tous les champs</li>
<li><b>Sous-titre :</b> « X prestation(s) — internes (propriétaires) et externes (partenaires), avec commissions DPM. »</li>
</ul>
<p>Chaque prestation dans la liste affiche :</p>
<ul>
<li>Nom + catégorie + résumé horaires (ex : « 🕒 Départs 9h, 14h (2h) · Dim fermé »)</li>
<li>Type · Fournisseur</li>
<li>Prix, Commission (% ou « comm. DPM »), Net partenaire</li>
<li>Statut actif/inactif</li>
</ul>

<h3>15.6 Options par bien</h3>
<p>Depuis <b>Conciergerie → Options par bien</b>, vous choisissez quelles prestations sont proposées dans chaque bien :</p>
""" + step(1, "Sélectionnez le bien dans le menu déroulant") + """
""" + step(2, "Cochez les prestations à proposer (colonne « Proposée »)") + """
""" + step(3, "Cochez celles qui doivent apparaître sur le site WordPress (colonne « Visible sur le site »)") + """
""" + step(4, "Cliquez <b>Enregistrer</b>") + """
<div class="note">💡 Par défaut, toutes les prestations applicables sont proposées. Les prestations internes n'apparaissent que pour les biens de leur propriétaire.</div>
</div>
"""

# ============= CHAPITRE 16 — PARTENAIRES =============
body += """
<div class="section">
<h2>16. Conciergerie — Partenaires</h2>

<h3>16.1 Créer un partenaire</h3>
""" + step(1, "Allez dans <b>Partenaires → Liste</b>") + """
""" + step(2, "Cliquez <b>+ Ajouter un partenaire</b>") + """
""" + step(3, "Remplissez :") + """
<table>
<tr><th style="width:28%">Champ</th><th>Description</th><th>Exemple</th></tr>
<tr><td><b>Nom</b> ✱</td><td>Nom de l'entreprise / du prestataire</td><td>Transport & chauffeur</td></tr>
<tr><td>Activité</td><td>Domaine d'activité</td><td>Transport & chauffeur</td></tr>
<tr><td>Contact</td><td>Personne à contacter</td><td>Youssef Benjelloun</td></tr>
<tr><td>Téléphone</td><td>Numéro principal</td><td>+212 6 61 20 10 06</td></tr>
<tr><td>E-mail</td><td>Email du contact</td><td>youssef@transport.ma</td></tr>
<tr><td>Adresse, Ville</td><td>Localisation</td><td>Marrakech</td></tr>
<tr><td>Site web</td><td>URL du site (optionnel)</td><td>www.transport-marrakech.ma</td></tr>
<tr><td>ICE</td><td>Identifiant commun de l'entreprise (Maroc)</td><td>001234567000089</td></tr>
<tr><td>Règlement</td><td>Mode de paiement, délai, coordonnées bancaires</td><td>Virement 30 jours, RIB : …</td></tr>
<tr><td>Note / conditions</td><td>Texte visible par le partenaire dans son espace</td><td>Pas de transport le dimanche</td></tr>
<tr><td>Interlocuteurs</td><td>Plusieurs contacts (nom, fonction, tél, email)</td><td>Responsable flotte, Comptable…</td></tr>
<tr><td>Ressources</td><td>Véhicules, équipes, matériel (pour le planning)</td><td>Mercedes Vito, Range Rover</td></tr>
<tr><td>Peut modifier ses prestations</td><td>Le partenaire peut ajuster prix et descriptions dans son espace</td><td>Non (par défaut)</td></tr>
<tr><td>Peut créer des promotions</td><td>Le partenaire peut créer des offres spéciales</td><td>Oui (par défaut)</td></tr>
</table>

<h3>16.2 Fiche partenaire complète</h3>
<p>Cliquez sur <b>👁</b> dans la liste ou dans Fiches & droits pour ouvrir la fiche complète d'un partenaire. Elle montre :</p>
<div class="cols2">
<div>
<h4>Colonne gauche</h4>
<ul>
<li>Toutes les informations de la fiche</li>
<li>Droits (peut modifier / peut promouvoir)</li>
</ul>
</div>
<div>
<h4>Colonne droite</h4>
<ul>
<li><b>Performance :</b> nb prestations, commandes confirmées, CA cumulé, panier moyen</li>
<li><b>Interlocuteurs</b></li>
<li><b>Règlement</b> et <b>Note/conditions</b></li>
</ul>
</div>
</div>
<p>En dessous :</p>
<ul>
<li><b>Ses prestations</b> : tableau avec bouton <b>+ Ajouter une prestation</b> (pré-rempli type=externe + partenaire_id) et ✏️ pour modifier chaque prestation</li>
<li><b>Dernières commandes</b> : les 10 dernières commandes sur ses prestations avec date, bien, montant, statut</li>
</ul>

<h3>16.3 Espace partenaire — ce que voit le partenaire</h3>
<p>L'espace partenaire (/partenaire/) est une application web séparée. Le partenaire :</p>
""" + step(1, "Crée un compte depuis l'URL /partenaire/ (formulaire d'inscription)") + """
""" + step(2, "Sa demande apparaît dans <b>Comptes & accès</b> avec statut « en_attente »") + """
""" + step(3, "L'admin rattache le compte à la bonne fiche partenaire et clique <b>Valider</b>") + """
""" + step(4, "Le partenaire se connecte et voit ses données : prestations, commandes reçues, statistiques") + """
<p>Pour vérifier ce que voit un partenaire, utilisez le bouton <b>« Voir comme »</b> dans Comptes & accès — il affiche un aperçu en lecture seule des données de la fiche.</p>
</div>
"""

# ============= CHAPITRE 17-20 — PROPRIETAIRES, VOYAGEURS, FICHES =============
body += """
<div class="section">
<h2>17. Conciergerie — Propriétaires</h2>
<p>Le processus est similaire aux partenaires. Chaque propriétaire a une fiche avec :</p>
<ul>
<li><b>Informations :</b> nom, email, tél, adresse, ville, ICE, commission DPM %, mode de paiement</li>
<li><b>Ses biens :</b> liste des biens rattachés avec statut et prix/nuit</li>
<li><b>Performance :</b> biens gérés, réservations confirmées, revenus cumulés</li>
<li><b>Prestations internes :</b> avec bouton <b>+ Ajouter une prestation</b> (pré-rempli type=interne + proprietaire_id)</li>
<li><b>Dernières réservations :</b> les 10 dernières sur ses biens</li>
</ul>
<p>L'espace propriétaire (/proprietaire/) fonctionne comme l'espace partenaire : inscription, validation par l'admin, consultation de ses données.</p>

<h2>18. Conciergerie — Voyageurs</h2>
<h3>18.1 Livre d'or</h3>
<p>Liste de tous les voyageurs avec : nom, email, téléphone, ville, pays, pièce d'identité, préférence marketing. Cliquez 👁 pour ouvrir la fiche complète.</p>

<h3>18.2 Liens d'accès séjour</h3>
<p>Pour chaque réservation confirmée, vous pouvez créer un <b>lien unique</b> :</p>
""" + step(1, "Allez dans <b>Voyageurs → Liens d'accès séjour</b>") + """
""" + step(2, "Repérez la réservation et cliquez <b>Créer le lien</b>") + """
""" + step(3, "Cliquez <b>Copier</b> pour copier le lien") + """
""" + step(4, "Envoyez-le au voyageur par WhatsApp, email ou message de plateforme") + """
<p>Le voyageur ouvre le lien dans son navigateur et accède à :</p>
<ul>
<li>Les informations du logement (adresse, wifi, code porte, instructions)</li>
<li>Le catalogue des prestations disponibles pour ce bien</li>
<li>Un formulaire de commande avec choix de date, heure, quantité</li>
<li>Le suivi de ses demandes (confirmée, en attente, refusée)</li>
</ul>
<div class="warn">⚠️ Le lien fonctionne uniquement pour les réservations confirmées ou terminées, et expire 30 jours après le départ. Cliquez <b>Désactiver</b> pour couper immédiatement l'accès.</div>

<h2>19. Commandes & Statistiques</h2>
<p><b>Demandes de prestations :</b> toutes les commandes voyageurs avec filtres par statut (en attente, confirmé, refusé, fait), par date et par bien. Actions : Confirmer, Refuser, Marquer comme fait.</p>
<p><b>Statistiques globales :</b> KPI mensuels de la conciergerie : CA total, nombre de commandes, top prestations, répartition par type et par bien. Navigation mois par mois.</p>
</div>
"""

# ============= CHAPITRE 20 — FICHES & DROITS =============
body += """
<div class="section">
<h2>20. Fiches & droits — Page centralisée</h2>
<p>Accessible depuis <b>Conciergerie → Fiches & droits</b>. Cette page centralise la gestion de tous les acteurs de la conciergerie.</p>

<h3>20.1 Les 5 onglets</h3>
<table>
<tr><th>Onglet</th><th>Contenu</th><th>Colonnes</th></tr>
<tr><td><b>Propriétaires</b></td><td>Tous les propriétaires avec leurs droits</td><td>Nom, Téléphone, Email, Ville, Droits, Actions</td></tr>
<tr><td><b>Partenaires</b></td><td>Tous les partenaires avec leurs droits</td><td>Nom, Catégorie, Contact, Ville, Téléphone, Droits, Actions</td></tr>
<tr><td><b>Séjours</b></td><td>Réservations avec lien d'accès voyageur</td><td>Voyageur, Bien, Dates, Lien unique</td></tr>
<tr><td><b>Collaborateurs</b></td><td>Membres de l'équipe avec rubriques visibles</td><td>Nom, Email, Rubriques visibles, Statut, Actions</td></tr>
<tr><td><b>Comptes</b></td><td>Demandes de compte partenaire/propriétaire</td><td>Nom, Email, Rôle, Fiche rattachée, Statut, Actions</td></tr>
</table>

<h3>20.2 « Voir son espace »</h3>
<p>Le bouton <b>👁 Voir son espace</b> ouvre la fiche complète d'un partenaire ou propriétaire en mode lecture. Vous voyez exactement les données que cette personne retrouve dans son espace : ses prestations, ses commandes, ses statistiques.</p>

<h3>20.3 Collaborateurs</h3>
<p>Gérez les membres de votre équipe :</p>
""" + step(1, "Cliquez <b>+ Inviter un collaborateur (copier le lien)</b> → le lien de l'application est copié") + """
""" + step(2, "Envoyez le lien par WhatsApp ou email au nouveau collaborateur") + """
""" + step(3, "Il crée son compte, apparaît ici en statut « invité »") + """
""" + step(4, "Cliquez <b>Modifier ses rubriques</b> → cochez les rubriques qu'il peut voir (Biens, Réservations, Prestations, etc.)") + """
""" + step(5, "Passez le statut sur <b>Actif</b> et enregistrez") + """
<div class="note">💡 Un compte <b>sans aucune case cochée</b> est « Administrateur complet » : il voit tout et peut gérer les droits des autres.</div>

<h3>20.4 Comptes & accès — validation des demandes</h3>
<p>Quand un partenaire ou propriétaire crée un compte depuis son espace, sa demande apparaît ici :</p>
""" + step(1, "Rattachez le compte à la bonne fiche dans le menu déroulant « Rattaché à la fiche »") + """
""" + step(2, "Cliquez <b>Valider</b> → le compte passe en « actif » et la personne peut se connecter") + """
<p>Bouton <b>« Voir comme »</b> : affiche un aperçu lecture seule de ce que voit ce compte dans son espace.</p>
</div>
"""

# ============= CHAPITRE 25 — ANNEXES =============
body += """
<div class="section">
<h2>21. Utilisateurs & groupes</h2>

<h3>21.1 Liste des utilisateurs</h3>
<p>Tous les membres de votre équipe avec leurs rôles et droits :</p>
<table>
<tr><th style="width:28%">Champ</th><th>Description</th></tr>
<tr><td><b>Nom complet</b> ✱</td><td>Nom affiché dans l'application</td></tr>
<tr><td>E-mail</td><td>Adresse e-mail de connexion</td></tr>
<tr><td>Titre du poste</td><td>Fonction dans l'entreprise</td></tr>
<tr><td>Téléphone</td><td>Numéro de contact</td></tr>
<tr><td>Rôle / groupe</td><td>Détermine les droits d'accès (voir ci-dessous)</td></tr>
<tr><td>Statut</td><td>actif, invité, suspendu</td></tr>
</table>

<h3>21.2 Rôles disponibles</h3>
<table>
<tr><th>Rôle</th><th>Accès</th></tr>
<tr><td>Propriétaire du compte</td><td>Accès total, gestion des abonnements et de la facturation</td></tr>
<tr><td>Administrateur</td><td>Accès total sauf facturation du compte</td></tr>
<tr><td>Gestionnaire</td><td>Biens, réservations, messages, tâches, prestations — pas de paramètres</td></tr>
<tr><td>Agent de ménage</td><td>Ses tâches de ménage uniquement</td></tr>
<tr><td>Chauffeur</td><td>Ses tâches de transport uniquement</td></tr>
<tr><td>Petit-déjeuner</td><td>Ses tâches de petit-déjeuner uniquement</td></tr>
<tr><td>Propriétaire d'un bien</td><td>Ses biens, ses réservations, ses revenus</td></tr>
<tr><td>Partenaire</td><td>Ses prestations, ses commandes</td></tr>
</table>

<h3>21.3 Intervenants</h3>
<p>Liste séparée des intervenants terrain (femmes de ménage, chauffeurs, techniciens) auxquels on assigne des tâches. Champs : nom, rôle, téléphone, email, biens rattachés.</p>

<h3>21.4 Groupes & droits</h3>
<p>Personnalisez les droits par groupe : quelles rubriques sont visibles, quelles actions sont autorisées (lecture seule, création, modification, suppression).</p>
</div>
"""

body += """
<div class="section">
<h2>22. Moteur de réservation (site direct)</h2>
<p>Your Hostaway inclut un moteur de réservation directe — un mini-site où les voyageurs réservent sans passer par Airbnb ou Booking (0% de commission plateforme).</p>

<h3>22.1 Design</h3>
<p>Personnalisez l'apparence : couleurs, logo, images de fond, texte d'accroche. Le site s'adapte automatiquement aux couleurs de votre marque.</p>

<h3>22.2 Annonces publiées</h3>
<p>Choisissez quels biens apparaissent sur le site de réservation directe. Chaque bien publié affiche ses photos, sa description, ses tarifs et un bouton « Réserver ».</p>

<h3>22.3 Pages</h3>
<p>Créez des pages supplémentaires : À propos, Conditions générales, FAQ, Contact. Éditeur de texte riche (titres, images, liens).</p>

<h3>22.4 Livret d'accueil numérique</h3>
<p>Remplace le guide papier de la villa. Le voyageur accède depuis son espace à :</p>
<ul>
<li>Instructions du logement (wifi, code porte, fonctionnement piscine…)</li>
<li>Recommandations restaurants, activités, transports</li>
<li>Numéros utiles (urgences, pharmacie, taxi…)</li>
<li>Règlement intérieur</li>
</ul>

<h3>22.5 SEO & Analytics</h3>
<p>Configuration des balises meta (titre, description), intégration Google Analytics et Facebook Pixel. Paramétrage du sitemap.</p>

<h3>22.6 Traductions</h3>
<p>Traduisez le site dans plusieurs langues. Chaque texte (boutons, messages, descriptions) peut avoir une traduction dans les langues activées.</p>
</div>
"""

body += """
<div class="section">
<h2>23. Branchements & outils</h2>

<h3>23.1 Serrures intelligentes</h3>
<p>Connectez des serrures connectées (Nuki, Yale, August…) pour générer automatiquement un code d'accès unique par réservation :</p>
<ul>
<li><b>Serrures :</b> listez vos serrures avec leur identifiant et le bien rattaché</li>
<li><b>Appareils :</b> état de la batterie, dernière connexion</li>
<li><b>Historique accès :</b> chaque utilisation d'un code est tracée (qui, quand, quelle porte)</li>
</ul>
<div class="example">
<b>Fonctionnement :</b> à la création d'une réservation confirmée, un code temporaire est généré (valide de J-arrivée 14h à J-départ 11h). Le code est affiché dans l'espace voyageur et dans les instructions d'arrivée.
</div>

<h3>23.2 Assurance</h3>
<p>Configuration d'une assurance voyageur proposée à la réservation (partenariat avec un assureur).</p>

<h3>23.3 Marketplace</h3>
<p>Intégrations avec des outils tiers : PriceLabs (tarification dynamique), Beyond Pricing, Wheelhouse, etc.</p>
</div>
"""

body += """
<div class="section">
<h2>24. Paramètres</h2>

<h3>24.1 Détails du compte</h3>
<p>Nom de l'entreprise, adresse, logo, coordonnées, numéro SIRET/RC, mentions légales. Ces informations apparaissent sur les factures et les contrats générés.</p>

<h3>24.2 Langues</h3>
<p>Langues disponibles dans les espaces voyageur, partenaire et propriétaire. Ajoutez ou retirez des langues selon votre clientèle.</p>

<h3>24.3 Intégrations email</h3>
<p>Configurez le serveur SMTP pour l'envoi d'emails depuis l'application (confirmations, factures, relevés). Champs : serveur, port, identifiant, mot de passe, adresse d'expédition.</p>

<h3>24.4 WhatsApp Business</h3>
<p>Connectez votre compte WhatsApp Business pour envoyer et recevoir des messages WhatsApp directement depuis la boîte de réception. Nécessite la validation Meta Business.</p>

<h3>24.5 SMS</h3>
<p>Configuration du fournisseur SMS (Twilio, etc.) pour l'envoi de notifications par SMS aux voyageurs.</p>

<h3>24.6 Webhooks</h3>
<p>Notifications automatiques vers des services externes. Chaque webhook est déclenché par un événement :</p>
<table>
<tr><th>Événement</th><th>Exemple d'utilisation</th></tr>
<tr><td>Nouvelle réservation</td><td>Notifier un channel Slack</td></tr>
<tr><td>Paiement reçu</td><td>Mettre à jour un tableur Google Sheets</td></tr>
<tr><td>Check-in complété</td><td>Envoyer un code de serrure</td></tr>
<tr><td>Nouvelle commande prestation</td><td>Notifier le partenaire par un autre système</td></tr>
</table>

<h3>24.7 API</h3>
<p>Clés API pour les développeurs : permettent d'accéder aux données de My Hostaway depuis des applications externes (site web, application mobile, intégration CRM).</p>

<h3>24.8 Notifications</h3>
<p>Paramétrez quelles notifications vous recevez et par quel canal : email, push, in-app. Par type d'événement (réservation, message, paiement, tâche).</p>

<h3>24.9 Journal d'activité</h3>
<p>Historique complet de toutes les actions effectuées dans l'application : qui a fait quoi, quand, sur quel élément. Utile pour le suivi et la traçabilité.</p>

<h3>24.10 Politiques d'annulation</h3>
<p>Modèles de politique d'annulation réutilisables :</p>
<table>
<tr><th>Politique</th><th>Conditions</th></tr>
<tr><td>Flexible</td><td>Remboursement intégral jusqu'à 24h avant l'arrivée</td></tr>
<tr><td>Modérée</td><td>Remboursement intégral jusqu'à 5 jours avant. 50% ensuite.</td></tr>
<tr><td>Stricte</td><td>Remboursement 50% jusqu'à 7 jours avant. 0% ensuite.</td></tr>
<tr><td>Non remboursable</td><td>Aucun remboursement (prix réduit)</td></tr>
</table>
</div>
"""

# ============= ANNEXES =============
body += """
<div class="section">
<h2>25. Annexes</h2>

<h3>A. Glossaire</h3>
<table>
<tr><th style="width:25%">Terme</th><th>Définition</th></tr>
<tr><td>Bien</td><td>Un logement géré (villa, riad, appartement, chambre)</td></tr>
<tr><td>Canal</td><td>Source de la réservation : direct, Airbnb, Booking, VRBO, Expedia, Abritel</td></tr>
<tr><td>Prestation</td><td>Service proposé au voyageur via la conciergerie</td></tr>
<tr><td>Partenaire</td><td>Prestataire externe qui fournit des prestations (spa, transport, excursions)</td></tr>
<tr><td>Propriétaire</td><td>Propriétaire d'un ou plusieurs biens en gestion chez DPM</td></tr>
<tr><td>Commission DPM</td><td>Part retenue par DPM sur les prestations vendues</td></tr>
<tr><td>Net partenaire</td><td>Montant reversé au partenaire après déduction de la commission</td></tr>
<tr><td>Commande</td><td>Demande de prestation faite par un voyageur</td></tr>
<tr><td>Tenant</td><td>Votre espace isolé dans la base de données (multi-comptes)</td></tr>
<tr><td>RLS</td><td>Row-Level Security — chaque utilisateur ne voit que ses propres données</td></tr>
<tr><td>Score ASO</td><td>Indicateur de qualité d'une annonce (complétude, photos, avis, réactivité)</td></tr>
<tr><td>iCal</td><td>Format standard de calendrier pour synchroniser les disponibilités entre plateformes</td></tr>
</table>

<h3>B. Calcul des commissions — tableau récapitulatif</h3>
<table>
<tr><th>Type</th><th>Qui fournit</th><th>Qui paie</th><th>Commission DPM</th><th>Reversement</th></tr>
<tr><td>Externe</td><td>Partenaire</td><td>Voyageur</td><td>Prix − Net partenaire</td><td>Net partenaire → au partenaire</td></tr>
<tr><td>Interne</td><td>Propriétaire (son personnel)</td><td>Voyageur</td><td>% fixé par bien (défaut 20%)</td><td>Reste → au propriétaire</td></tr>
<tr><td>DPM</td><td>DPM directement</td><td>Voyageur</td><td>Marge = Prix − Coût de revient</td><td>Rien (DPM conserve tout)</td></tr>
</table>

<h3>C. FAQ — Questions fréquentes</h3>

<h4>Comment modifier le prix d'une prestation ?</h4>
<p>Allez dans Conciergerie → Toutes les prestations → cliquez ✏️ sur la prestation → modifiez le prix → Enregistrer. Les nouvelles commandes utiliseront le nouveau prix.</p>

<h4>Comment donner accès à un partenaire ?</h4>
<p>Envoyez-lui le lien /partenaire/. Il crée son compte. Validez sa demande dans Comptes & accès en la rattachant à sa fiche partenaire.</p>

<h4>Comment générer le lien voyageur ?</h4>
<p>Voyageurs → Liens d'accès séjour → trouvez la réservation → Créer le lien → Copier. Envoyez le lien par message.</p>

<h4>Pourquoi je ne vois pas certaines prestations internes dans un bien ?</h4>
<p>Les prestations internes n'apparaissent que pour les biens rattachés au même propriétaire. Vérifiez que le bien et la prestation ont le même propriétaire.</p>

<h4>Comment changer la commission DPM sur un bien ?</h4>
<p>Annonces → Liste → ✏️ sur le bien → champ « Commission sur les services vendus par le propriétaire (%) » → Enregistrer.</p>

<h4>Comment exporter mes données ?</h4>
<p>Dans toute liste (réservations, prestations, partenaires…), cliquez le bouton <b>⬇ CSV</b> en haut à droite de la liste. Le fichier se télécharge directement.</p>

<h3>D. Résolution de problèmes courants</h3>
<table>
<tr><th style="width:35%">Problème</th><th>Solution</th></tr>
<tr><td>L'application ne charge pas</td><td>Videz le cache du navigateur (Ctrl+Shift+Suppr). Vérifiez votre connexion internet.</td></tr>
<tr><td>Un formulaire affiche « Erreur »</td><td>Vérifiez que les champs obligatoires (marqués ✱) sont remplis. Vérifiez la cohérence des données (commission vs net partenaire).</td></tr>
<tr><td>Un partenaire ne voit rien dans son espace</td><td>Vérifiez dans Comptes & accès que son compte est « actif » et rattaché à la bonne fiche partenaire.</td></tr>
<tr><td>Le lien voyageur ne fonctionne pas</td><td>Le lien expire 30 jours après le départ, et ne fonctionne que pour les réservations confirmées ou terminées. Vérifiez le statut de la réservation.</td></tr>
<tr><td>Les prestations n'apparaissent pas pour un bien</td><td>Vérifiez dans Conciergerie → Options par bien que les prestations sont cochées pour ce bien.</td></tr>
<tr><td>Les commissions ne sont pas calculées</td><td>Les commissions apparaissent uniquement pour les commandes confirmées. Confirmez la commande dans Demandes de prestations.</td></tr>
</table>
</div>
"""

# ============= PAGE FINALE =============
body += """
<div class="section" style="text-align:center;padding-top:50px">
<div style="font-size:13px;color:#C9A227;letter-spacing:3px;margin-bottom:8px">DPM CONCIERGERIE</div>
<h2 style="border:none;font-size:22px">My Hostaway — Guide complet d'utilisation</h2>
<p style="color:#888;font-size:11px;margin-top:16px">
Document généré le 27 novembre 2026<br>
DPM Consulting Group — Marrakech, Maroc<br><br>
Application : https://marco-kech.github.io/my-hostaway/<br>
Aide intégrée : bouton ❓ dans la barre du haut de l'application
</p>
</div>
"""

# ============= ASSEMBLAGE HTML =============
html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>My Hostaway — Guide complet</title>
<style>{CSS}</style>
</head>
<body>{body}</body>
</html>"""

with open("guide-my-hostaway.html", "w", encoding="utf-8") as f:
    f.write(html)
print("HTML generated")

HTML(string=html).write_pdf("guide-my-hostaway.pdf")
print("PDF generated")

import os
size = os.path.getsize("guide-my-hostaway.pdf")
print(f"PDF size: {size/1024:.0f} KB")
