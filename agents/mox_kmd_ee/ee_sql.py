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
SELECT top(1000) [PersonnrSEnr]
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

FORBRUGSSTED_ADRESSE_SQL = """SELECT [Husnr],
                                     [ForbrStVejnavn],
                                     [Vejkode],
                                     [Postdistrikt],
                                     [Postnr],
                                     [Bogstav],
                                     [Etage],
                                     [Sidedørnr]
                            FROM Forbrugssted
                            WHERE ForbrugsstedID = {0}
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
