#! /usr/bin/env python3
# coding: utf-8
import pandas as pd

def get_doc():
    """Ouvre le document et formatage des noms de colonnes pour
    éviter les conflits d'utilisation du point"""
    filename = input("Entrez le chemin du fichier (format xslx): ")
    export = pd.read_excel(filename)
    export.columns = [name.replace(".", "_") for name in export.columns]
    return export

def format_auteur(export):
    """Formater la colonne qui contient le nom du compte en rajoutant un "@"."""
    auteur_formate = [name.replace(name, "@"+name) for name in
                      export.extra_author_attributes_short_name]
    return auteur_formate

def format_date(export):
    """Formatage des dates de la colonne 'published' """
    date_time = pd.to_datetime(export['published'], errors='coerce', dayfirst=True)
    return date_time

class Noeud:
    """classe qui vise à créer notre fichier de noeuds"""
    def __init__(self, export, auteur_formate, date_time):
        self.export = export
        self.auteur_formate = auteur_formate
        self.date_time = date_time

    def get_comptes_auteurs(self):
        """Récupération des comptes émetteurs des tweets"""
        auteurs = pd.DataFrame({"id": self.auteur_formate, "Label": self.auteur_formate,
                                "interval": self.date_time.dt.date})
        return auteurs

    def get_comptes_in_tweets(self):
        """Récupération de la liste des comptes présents dans les tweets"""
        content_tweets = self.export.content
        compte_twitter = r"@[a-zA-Z\d/_/-]+"
        list_comptes_twitter = content_tweets.str.findall(compte_twitter)

        return list_comptes_twitter

    def list_comptes_in_tweets(self):
        list_comptes_twitter = self.get_comptes_in_tweets()
        df_list_comptes_twitter = pd.DataFrame(list_comptes_twitter.tolist(),
                                               self.date_time.dt.date)
        df_list_comptes_twitter = df_list_comptes_twitter.reset_index()
        df_list_comptes_twitter = pd.melt(df_list_comptes_twitter,
                                          id_vars=["published"],
                                          value_name='Labels')
        df_list_comptes_twitter = df_list_comptes_twitter.drop("variable", axis=1)
        df_list_comptes_twitter = df_list_comptes_twitter[df_list_comptes_twitter.Labels.notnull()]
        df_list_comptes_twitter = pd.DataFrame({"Id": df_list_comptes_twitter["Labels"],
                                                "Label": df_list_comptes_twitter["Labels"],
                                                "Interval": df_list_comptes_twitter["published"]})
        return df_list_comptes_twitter

    def concat_list_comptes(self):
        """Ajout des deux listes pour créer un seul fichier"""
        concat_list = pd.concat([self.get_comptes_auteurs(), self.list_comptes_in_tweets()])
        trie_list = concat_list.sort_values(by='interval')
        drop_duplicates = trie_list.drop_duplicates(subset='Label')
        reset_index = drop_duplicates.reset_index(drop=True)
        noeuds = input("Nommez le fichier des noeuds (en .csv): ")

        return reset_index.to_csv(noeuds)

class Lien(Noeud):
    """Création du fichier des liens qui doit contenir au moins deux colonnes : source et target"""

    def get_source_destination(self):
        """Récupération de la colonne source en reprenant la colonne
        "auteur" et la colonne destination via les comptes présents dans les tweets"""
        source = pd.DataFrame({"Source": self.auteur_formate})
        destination = self.get_comptes_in_tweets()
        destination = pd.DataFrame(destination.tolist())
        concat_src_dest = pd.concat([source, destination, self.date_time.dt.date], axis=1)

        return concat_src_dest

    def get_links(self):
        """Création de la liste de links"""
        concat_list = self.get_source_destination()
        melt_list = pd.melt(concat_list, id_vars=["Source", "published"], value_name='Target')
        melt_list = melt_list.drop("variable", axis=1)
        melt_list = melt_list[melt_list.Target.notnull()]
        sort_sources = melt_list.sort_values(by="Source")
        sort_sources = sort_sources.reset_index(drop=True)
        get_links = input("Nommez le fichier des liens (en .csv): ")

        return sort_sources.to_csv(get_links)

def main():
    export = get_doc()
    auteurs_formate = format_auteur(export)
    date_formatee = format_date(export)
    noeuds = Noeud(export, auteurs_formate, date_formatee)
    noeuds.concat_list_comptes()
    liens = Lien(export, auteurs_formate, date_formatee)
    liens.get_links()

if __name__ == '__main__':
    main()
