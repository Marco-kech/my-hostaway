-- 215 — Champs de la fiche propriétaire utilisés par l'écran « Propriétaires → Liste » (ajouté le 26 nov.)
-- mais absents de la base : sans eux, l'enregistrement d'un propriétaire échoue. Ajout seulement, rejouable.
alter table proprietaire add column if not exists ville text;
alter table proprietaire add column if not exists ice text;
alter table proprietaire add column if not exists mode_paiement text;
alter table proprietaire add column if not exists rib text;
-- Retour arrière (si besoin) : alter table proprietaire drop column ville, drop column ice, drop column mode_paiement, drop column rib;
