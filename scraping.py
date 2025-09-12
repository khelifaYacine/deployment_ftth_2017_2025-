import pandas as pd
import requests
import zipfile
from io import BytesIO

# URL directe du ZIP
url_zip = "https://static.data.gouv.fr/resources/le-marche-du-haut-et-tres-haut-debit-fixe-deploiements/20250313-164217/2024t4-commune.zip"

# Télécharger le ZIP
response = requests.get(url_zip)
response.raise_for_status()

# Ouvrir le ZIP en mémoire
with zipfile.ZipFile(BytesIO(response.content)) as z:
    print("📂 Contenu du ZIP :", z.namelist())

    # Chercher le fichier CSV contenant "commune"
    csv_file = next((f for f in z.namelist() if "commune" in f.lower() and f.endswith(".csv")), None)
    if not csv_file:
        raise ValueError("❌ Aucun fichier CSV 'commune' trouvé dans le ZIP")

    # Charger le CSV
    with z.open(csv_file) as f:
        df = pd.read_csv(f, sep=";", low_memory=False)

# Vérifier les colonnes disponibles
print("📋 Colonnes disponibles :", df.columns.tolist())

# Détection dynamique de la colonne département
dep_col = next((col for col in df.columns if "DEP" in col.upper()), None)
if not dep_col:
    raise ValueError("❌ Colonne département introuvable")

# Filtrer le département 63
df_63 = df[df[dep_col].astype(str) == "63"].copy()

# Calculs
df_63["taux_couverture"] = df_63["ftth"] / df_63["Locaux"]
df_63["locaux_non_raccordés"] = df_63["Locaux"] - df_63["ftth"]

# Résumé
print(f"\n✅ Communes du 63 extraites : {len(df_63)}")
print(df_63[["NOM_COM", "Locaux", "ftth", "taux_couverture"]].sort_values(by="taux_couverture").head(10))
