-- 225 — Valeurs proposées par l'application mais absentes des listes de la base (l'enregistrement échouait).
alter type moyen_paiement add value if not exists 'paypal';
alter type statut_reservation add value if not exists 'sejour_proprietaire';
