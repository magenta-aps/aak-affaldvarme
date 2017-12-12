#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""This module contains all SQL used in the KMD EE Mox Agent."""

# This is the SQL to fetch all customers from the KMD EE database.
# Only relevant fields (please).

CUSTOMER_SQL = """
SELECT  [PersonnrSEnr]
      ,[LigestPersonnr]
      ,[Kundenr]
      ,[KundeSagsnr]
      ,[KundeNavn]
      ,[Telefonnr]
      ,[EmailKunde]
      ,[MobilTlf]
      ,[a].[ForbrugsstedID]
      ,[VejNavn]
      ,[a].[Postdistrikt]
      ,[Tilflytningsdato]
      ,[Fraflytningsdato]
      ,[Status]
      ,[FasadministratorID]
      ,[BoligadminID]
      ,[Husnr]
      ,[ForbrStVejnavn]
      ,[Vejkode]
      ,[b].[Postdistrikt] as [ForbrStPostdistrikt]
      ,[Postnr]
      ,[Bogstav]
      ,[Etage]
      ,[Sidedørnr]
  FROM Kunde a, Forbrugssted b
  WHERE Tilflytningsdato <= GETDATE() AND Fraflytningsdato >= GETDATE()
  and Afregningsgrpnr <> 999
  and a.ForbrugsstedID = b.ForbrugsstedID
"""


TREFINSTALLATION_SQL = """SELECT [InstalNummer],
                                 [AlternativStedID],
                                 [Målernr],
                                 [MaalerTypeBetegnel],
                                 [Målertypefabrikat],
                                 [DatoFra],
                                 [DatoTil]
    FROM TrefInstallation a, TrefMaaler b
    WHERE ForbrugsstedID = {0}
    AND a.InstallationID = b.InstallationID
    AND b.DatoFra <= GETDATE() and b.DatoTil >= GETDATE()
    """

RELEVANT_TREF_INSTALLATIONS_SQL = """SELECT [InstalNummer],
                                 [AlternativStedID],
                                 [Målernr],
                                 [MaalerTypeBetegnel],
                                 [Målertypefabrikat],
                                 [DatoFra],
                                 [DatoTil]
    FROM TrefInstallation a, TrefMaaler b
    WHERE
    a.InstallationID = b.InstallationID
    AND b.DatoFra <= GETDATE() and b.DatoTil >= GETDATE()
    AND ForbrugsstedID IN (SELECT a.ForbrugsstedID from Kunde a, Forbrugssted b
  WHERE Tilflytningsdato <= GETDATE() AND Fraflytningsdato >= GETDATE()
  and Afregningsgrpnr <> 999
  and a.ForbrugsstedID = b.ForbrugsstedID)
    """

RELEVANT_ALT_ADRESSE_SQL = """SELECT [HusnrAltern],
                                     [ForbrStVejnavn],
                                     [VejkodeAltern],
                                     [Postdistrikt],
                                     [Postnr],
                                     [Bogstav],
                                     [EtageAltAdr],
                                     [SidedørnrAltern]
                            FROM AlternativSted
                            WHERE AlternativStedID IN (
                SELECT AlternativStedID FROM TrefInstallation
                WHERE AlternativStedID <> 0
    AND ForbrugsstedID IN (
        SELECT a.ForbrugsstedID from Kunde a, Forbrugssted b
       WHERE Tilflytningsdato <= GETDATE() AND Fraflytningsdato >= GETDATE()
       and Afregningsgrpnr <> 999
       and a.ForbrugsstedID = b.ForbrugsstedID
  )
  )
  """
ALTERNATIVSTED_ADRESSE_SQL = """SELECT [HusnrAltern],
                                     [ForbrStVejnavn],
                                     [VejkodeAltern],
                                     [Postdistrikt],
                                     [Postnr],
                                     [Bogstav],
                                     [EtageAltAdr],
                                     [SidedørnrAltern]
                            FROM AlternativSted
                            WHERE AlternativStedID = {0}
                          """

if __name__ == '__main__':

    import pymssql

    from mssql_config import username, password, server, database
    from ee_utils import connect

    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)
    cursor.execute(RELEVANT_ALT_ADRESSE_SQL)
    rows = cursor.fetchall()
    n1 = cursor.rowcount
    cursor.execute(CUSTOMER_SQL)
    rows = cursor.fetchall()
    n2 = cursor.rowcount
    cursor.execute(RELEVANT_TREF_INSTALLATIONS_SQL)
    rows = cursor.fetchall()
    n3 = cursor.rowcount

    print(n1, "AltSted rows to consider")
    print(n2, "Customer rows to consider")
    print(n3, "Installation rows to consider")
