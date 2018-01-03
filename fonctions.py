#! /usr/bin/env python3
# coding: utf-8
import pandas as pd

def get_doc():
    """Ouvre le document et formatage des noms de colonnes pour
    éviter les conflits d'utilisation du point"""
    filename = input("Entrez le chemin du fichier (format xlsx): ")
    export = pd.read_excel(filename)
    export.columns = [name.replace(".", "_") for name in export.columns]
    return export

def format_author(export):
    """Formater la colonne qui contient le nom du compte en rajoutant un "@"."""
    author_formate = [name.replace(name, "@"+name) for name in
                      export.extra_author_attributes_short_name]
    return author_formate

def format_date(export):
    """Formatage des dates de la colonne 'published' """
    date_time = pd.to_datetime(export['published'], errors='coerce', dayfirst=True)
    return date_time

class node:
    """classe qui vise à créer notre fichier de nodes"""
    def __init__(self, export, author_formate, date_time):
        self.export = export
        self.author_formate = author_formate
        self.date_time = date_time

    def get_accounts_authors(self):
        """Récupération des accounts émetteurs des tweets"""
        authors = pd.DataFrame({"id": self.author_formate, "Label": self.author_formate,
                                "interval": self.date_time.dt.date})
        return authors

    def get_accounts_in_tweets(self):
        """Récupération de la liste des accounts présents dans les tweets"""
        content_tweets = self.export.content
        compte_twitter = r"@[a-zA-Z\d/_/-]+"
        list_accounts_twitter = content_tweets.str.findall(compte_twitter)

        return list_accounts_twitter

    def list_accounts_in_tweets(self):
        list_accounts_twitter = self.get_accounts_in_tweets()
        df_list_accounts_twitter = pd.DataFrame(list_accounts_twitter.tolist(),
                                                self.date_time.dt.date)
        df_list_accounts_twitter = df_list_accounts_twitter.reset_index()
        df_list_accounts_twitter = pd.melt(df_list_accounts_twitter,
                                           id_vars=["published"],
                                           value_name='Labels')
        df_list_accounts_twitter = df_list_accounts_twitter.drop("variable", axis=1)
        df_list_accounts_twitter = df_list_accounts_twitter[df_list_accounts_twitter.Labels.notnull()]
        df_list_accounts_twitter = pd.DataFrame({"Id": df_list_accounts_twitter["Labels"],
                                                 "Label": df_list_accounts_twitter["Labels"],
                                                 "Interval": df_list_accounts_twitter["published"]})
        return df_list_accounts_twitter

    def concat_list_accounts(self):
        """Ajout des deux listes pour créer un seul fichier"""
        concat_list = pd.concat([self.get_accounts_authors(), self.list_accounts_in_tweets()])
        trie_list = concat_list.sort_values(by='interval')
        drop_duplicates = trie_list.drop_duplicates(subset='Label')
        reset_index = drop_duplicates.reset_index(drop=True)
        nodes = input("Nommez le fichier des nodes (en .csv): ")

        return reset_index.to_csv(nodes)

class link(node):
    """Création du fichier des links qui doit contenir au moins deux colonnes : source et target"""

    def get_source_destination(self):
        """Récupération de la colonne source en reprenant la colonne
        "author" et la colonne destination via les accounts présents dans les tweets"""
        source = pd.DataFrame({"Source": self.author_formate})
        destination = self.get_accounts_in_tweets()
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
        get_links = input("Nommez le fichier des links (en .csv): ")

        return sort_sources.to_csv(get_links)

def main():
    export = get_doc()
    authors_formate = format_author(export)
    date_formatee = format_date(export)
    nodes = node(export, authors_formate, date_formatee)
    nodes.concat_list_accounts()
    links = link(export, authors_formate, date_formatee)
    links.get_links()

if __name__ == '__main__':
    main()
